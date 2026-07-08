"""Firestore persistence for cluster priority analysis and rankings."""

from __future__ import annotations

import logging
from datetime import UTC, datetime

from app.db.pagination import PaginationParams
from app.models.domain.cluster import ClusterPriorityAnalysis, ClusterResponse, ClusterSearchFilters, ClusterUpdate
from app.models.domain.complaint import ComplaintResponse
from app.repositories.cluster_repository import ClusterRepository
from app.repositories.complaint_repository import ComplaintRepository

logger = logging.getLogger(__name__)

PRIORITY_ACTOR = "civiclens-priority"


class PriorityRepository:
    """Reads cluster evidence and persists priority intelligence."""

    def __init__(
        self,
        cluster_repo: ClusterRepository,
        complaint_repo: ComplaintRepository,
    ):
        self.cluster_repo = cluster_repo
        self.complaint_repo = complaint_repo

    def get_cluster(self, cluster_id: str) -> ClusterResponse:
        return self.cluster_repo.get_by_id_or_raise(cluster_id)

    def get_cluster_complaints(self, cluster: ClusterResponse) -> list[ComplaintResponse]:
        complaints: list[ComplaintResponse] = []
        for complaint_id in cluster.complaint_ids:
            complaint = self.complaint_repo.get_by_id(complaint_id)
            if complaint is not None:
                complaints.append(complaint)
        return complaints

    def list_all_clusters(self, *, limit: int = 500) -> list[ClusterResponse]:
        result = self.cluster_repo.list(
            pagination=PaginationParams(limit=limit, order_by="metadata.created_at", order_direction="desc"),
        )
        return result.items

    def persist_priority_analysis(
        self,
        cluster_id: str,
        analysis: ClusterPriorityAnalysis,
    ) -> ClusterResponse:
        """Save full priority analysis and denormalized cluster fields."""
        now = datetime.now(UTC)
        normalized_priority = round(analysis.priority_score / 100.0, 4)

        return self.cluster_repo.update(
            cluster_id,
            ClusterUpdate(
                priority_analysis=analysis,
                priority_score=normalized_priority,
                impact_score=analysis.impact_score,
                urgency_level=analysis.urgency_level,
                priority_rank=analysis.priority_rank,
                recommended_department=analysis.suggested_department,
                recommended_action=analysis.recommended_action,
                estimated_budget=analysis.estimated_budget_range,
                estimated_resolution_time=analysis.estimated_resolution_time,
                affected_population=analysis.affected_population_estimate,
                priority_reasoning=analysis.reasoning,
                priority_confidence=analysis.confidence_score,
                priority_updated_at=now,
                priority_analysis_hash=analysis.analysis_hash,
                department=analysis.suggested_department,
                updated_by=PRIORITY_ACTOR,
            ),
        )

    def update_cluster_rank(self, cluster_id: str, priority_rank: int) -> ClusterResponse:
        cluster = self.cluster_repo.get_by_id_or_raise(cluster_id)
        if cluster.priority_analysis is None:
            return cluster
        updated_analysis = cluster.priority_analysis.model_copy(update={"priority_rank": priority_rank})
        return self.cluster_repo.update(
            cluster_id,
            ClusterUpdate(
                priority_rank=priority_rank,
                priority_analysis=updated_analysis,
                updated_by=PRIORITY_ACTOR,
            ),
        )

    def list_ranked_clusters(self, *, limit: int = 100) -> list[ClusterResponse]:
        clusters = self.list_all_clusters(limit=limit)
        ranked = [c for c in clusters if c.priority_analysis is not None]
        ranked.sort(
            key=lambda item: (
                -(item.priority_analysis.priority_score if item.priority_analysis else 0),
                -(item.impact_score or 0),
                -(item.complaint_count),
            ),
        )
        return ranked
