"""Cluster business logic for dashboard and clustering operations."""

from __future__ import annotations

import logging

from app.core.config import Settings
from app.core.exceptions import BadRequestError, NotFoundError
from app.db.pagination import PaginationParams
from app.models.domain.cluster import ClusterResponse, ClusterSearchFilters
from app.models.domain.complaint import ComplaintResponse
from app.models.enums.common import ClusterStatus
from app.models.schemas.cluster_portal import (
    ClusterComplaintSummary,
    ClusterDashboardSummary,
    ClusterDetailResponse,
    ClusterListItem,
    ClusterListResponse,
    ClusterProcessResponse,
)
from app.repositories.cluster_repository import ClusterRepository
from app.repositories.complaint_repository import ComplaintRepository
from app.services.clustering.duplicate_detection_service import DuplicateDetectionService

logger = logging.getLogger(__name__)


def _to_list_item(cluster: ClusterResponse) -> ClusterListItem:
    return ClusterListItem(
        id=cluster.id,
        title=cluster.title,
        theme=cluster.theme,
        category=cluster.category,
        status=cluster.status,
        department=cluster.department,
        village_name=cluster.village_name,
        complaint_count=cluster.complaint_count,
        average_severity=cluster.average_severity,
        latest_complaint_date=cluster.latest_complaint_date,
        representative_complaint_id=cluster.representative_complaint_id,
        priority_score=cluster.priority_score,
        hotspot_score=cluster.hotspot_score,
        average_confidence=cluster.average_confidence,
        affected_area=cluster.affected_area,
        impact_score=cluster.impact_score,
        urgency_level=cluster.urgency_level,
        priority_rank=cluster.priority_rank,
        recommended_department=cluster.recommended_department,
        recommended_action=cluster.recommended_action,
        priority_confidence=cluster.priority_confidence,
        priority_updated_at=cluster.priority_updated_at,
    )


def _to_complaint_summary(complaint: ComplaintResponse) -> ClusterComplaintSummary:
    return ClusterComplaintSummary(
        id=complaint.id,
        title=complaint.title,
        status=complaint.status.value,
        village_name=complaint.village_name,
        submitted_at=complaint.submitted_at,
        is_duplicate=complaint.is_duplicate,
        duplicate_score=complaint.duplicate_score,
        priority=complaint.priority.value,
    )


class ClusterPortalService:
    """Read and orchestration APIs for complaint clusters."""

    def __init__(
        self,
        cluster_repo: ClusterRepository,
        complaint_repo: ComplaintRepository,
        duplicate_service: DuplicateDetectionService,
        settings: Settings,
    ):
        self.cluster_repo = cluster_repo
        self.complaint_repo = complaint_repo
        self.duplicate_service = duplicate_service
        self.settings = settings

    def list_clusters(
        self,
        *,
        page: int = 1,
        page_size: int = 12,
        search: str | None = None,
        category: str | None = None,
        status: ClusterStatus | None = None,
    ) -> ClusterListResponse:
        page = max(page, 1)
        page_size = min(max(page_size, 1), 100)

        filters = ClusterSearchFilters(status=status)
        if category:
            from app.models.enums.common import ComplaintCategory

            try:
                filters.category = ComplaintCategory(category)
            except ValueError:
                pass

        fetch_limit = page * page_size
        pagination = PaginationParams(
            limit=fetch_limit,
            order_by="complaint_count",
            order_direction="desc",
        )

        if search and search.strip():
            result = self.cluster_repo.search(search.strip(), filters=filters, pagination=pagination)
        else:
            result = self.cluster_repo.list(filters=filters, pagination=pagination)

        total = self.cluster_repo.count(filters=filters)
        start = (page - 1) * page_size
        end = start + page_size
        page_items = result.items[start:end]

        return ClusterListResponse(
            items=[_to_list_item(item) for item in page_items],
            total=total,
            page=page,
            page_size=page_size,
            has_more=end < total,
        )

    def get_cluster(self, cluster_id: str) -> ClusterDetailResponse:
        cluster = self.cluster_repo.get_by_id(cluster_id)
        if cluster is None:
            raise NotFoundError(f"Cluster '{cluster_id}' not found")

        related: list[ClusterComplaintSummary] = []
        for complaint_id in cluster.complaint_ids:
            complaint = self.complaint_repo.get_by_id(complaint_id)
            if complaint:
                related.append(_to_complaint_summary(complaint))
        related.sort(key=lambda item: item.submitted_at, reverse=True)

        return ClusterDetailResponse(
            id=cluster.id,
            title=cluster.title,
            description=cluster.description,
            theme=cluster.theme,
            category=cluster.category,
            status=cluster.status,
            department=cluster.department,
            village_name=cluster.village_name,
            village_names=cluster.village_names,
            coordinates=cluster.coordinates,
            complaint_ids=cluster.complaint_ids,
            complaint_count=cluster.complaint_count,
            representative_complaint_id=cluster.representative_complaint_id,
            average_severity=cluster.average_severity,
            latest_complaint_date=cluster.latest_complaint_date,
            average_confidence=cluster.average_confidence,
            affected_area=cluster.affected_area,
            priority_score=cluster.priority_score,
            hotspot_score=cluster.hotspot_score,
            constituency=cluster.constituency,
            district=cluster.district,
            state=cluster.state,
            ai_insights=cluster.ai_insights,
            priority_analysis=cluster.priority_analysis,
            impact_score=cluster.impact_score,
            urgency_level=cluster.urgency_level,
            priority_rank=cluster.priority_rank,
            recommended_department=cluster.recommended_department,
            recommended_action=cluster.recommended_action,
            estimated_budget=cluster.estimated_budget,
            estimated_resolution_time=cluster.estimated_resolution_time,
            affected_population=cluster.affected_population,
            priority_reasoning=cluster.priority_reasoning,
            priority_confidence=cluster.priority_confidence,
            priority_updated_at=cluster.priority_updated_at,
            metadata=cluster.metadata,
            related_complaints=related,
        )

    def get_dashboard_summary(self) -> ClusterDashboardSummary:
        all_clusters = self.cluster_repo.list(
            pagination=PaginationParams(limit=500, order_by="complaint_count", order_direction="desc"),
        )
        items = all_clusters.items
        total = len(items)
        open_clusters = sum(1 for item in items if item.status == ClusterStatus.OPEN)
        total_complaints = sum(item.complaint_count for item in items)
        avg_size = round(total_complaints / total, 2) if total else 0.0
        hotspots = sorted(items, key=lambda c: c.hotspot_score, reverse=True)[:5]

        return ClusterDashboardSummary(
            total_clusters=total,
            open_clusters=open_clusters,
            total_clustered_complaints=total_complaints,
            average_cluster_size=avg_size,
            top_hotspots=[_to_list_item(item) for item in hotspots],
        )

    def process_complaint_clustering(
        self,
        complaint_id: str,
        *,
        force: bool = False,
    ) -> ClusterProcessResponse:
        if not self.settings.clustering_enabled:
            raise BadRequestError("Clustering is disabled")
        updated = self.duplicate_service.process_complaint(complaint_id, force=force)
        return ClusterProcessResponse(
            success=updated.cluster_id is not None,
            message="Clustering completed" if updated.cluster_id else "Clustering did not assign a cluster",
            complaint_id=updated.id,
            cluster_id=updated.cluster_id,
            is_duplicate=updated.is_duplicate,
            duplicate_score=updated.duplicate_score,
        )
