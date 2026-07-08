"""Cluster lifecycle management and statistics."""

from __future__ import annotations

import logging
from datetime import UTC, datetime

from app.db.collections import CollectionNames, build_document_path
from app.models.domain.cluster import ClusterCreate, ClusterResponse, ClusterUpdate
from app.models.domain.complaint import ComplaintResponse, ComplaintUpdate
from app.models.enums.common import ClusterStatus, ComplaintStatus
from app.models.schemas.common import DocumentMetadataCreate, GeoLocation
from app.repositories.cluster_repository import ClusterRepository
from app.repositories.complaint_repository import ComplaintRepository
from app.services.priority.priority_engine_service import PriorityEngineService

logger = logging.getLogger(__name__)

CLUSTER_ACTOR = "civiclens-clustering"

SEVERITY_WEIGHTS = {
    "low": 1.0,
    "medium": 2.0,
    "high": 3.0,
    "critical": 4.0,
}


def _severity_label(value: float) -> str:
    if value >= 3.5:
        return "Critical"
    if value >= 2.5:
        return "High"
    if value >= 1.5:
        return "Medium"
    return "Low"


def _complaint_severity_value(complaint: ComplaintResponse) -> float:
    if complaint.image_analysis and complaint.image_analysis.severity:
        return SEVERITY_WEIGHTS.get(complaint.image_analysis.severity.lower(), 2.0)
    if complaint.ai_analysis and complaint.ai_analysis.severity:
        return SEVERITY_WEIGHTS.get(complaint.ai_analysis.severity.lower(), 2.0)
    return 2.0


def _complaint_confidence(complaint: ComplaintResponse) -> float:
    scores: list[float] = []
    if complaint.ai_analysis:
        scores.append(complaint.ai_analysis.confidence_score)
    if complaint.image_analysis:
        scores.append(complaint.image_analysis.confidence_score)
    if not scores:
        return 0.5
    return sum(scores) / len(scores)


class ClusterService:
    """Creates clusters, assigns complaints, and maintains cluster statistics."""

    def __init__(
        self,
        cluster_repo: ClusterRepository,
        complaint_repo: ComplaintRepository,
        priority_engine: PriorityEngineService | None = None,
    ):
        self.cluster_repo = cluster_repo
        self.complaint_repo = complaint_repo
        self.priority_engine = priority_engine

    def _trigger_priority_analysis(self, cluster_id: str) -> None:
        if self.priority_engine is not None:
            self.priority_engine.analyze_if_needed_safe(cluster_id)

    def _build_cluster_title(self, complaint: ComplaintResponse) -> str:
        issue = (
            complaint.image_analysis.primary_issue
            if complaint.image_analysis
            else complaint.category_name or complaint.category.value.replace("_", " ").title()
        )
        return f"{issue} — {complaint.village_name}"

    def _build_cluster_description(self, complaint: ComplaintResponse) -> str:
        if complaint.ai_analysis and complaint.ai_analysis.summary:
            return complaint.ai_analysis.summary
        return complaint.description[:500]

    def _build_cluster_theme(self, complaint: ComplaintResponse) -> str:
        if complaint.ai_analysis and complaint.ai_analysis.keywords:
            return complaint.ai_analysis.keywords[0]
        return complaint.category.value

    def _resolve_department(self, complaint: ComplaintResponse) -> str:
        if complaint.ai_analysis and complaint.ai_analysis.responsible_department:
            return complaint.ai_analysis.responsible_department
        if complaint.image_analysis and complaint.image_analysis.suggested_department:
            return complaint.image_analysis.suggested_department
        return "General Administration"

    def _centroid(self, complaints: list[ComplaintResponse]) -> GeoLocation | None:
        points = [
            (item.location.latitude, item.location.longitude)
            for item in complaints
            if item.location is not None
        ]
        if not points:
            return None
        lat = sum(p[0] for p in points) / len(points)
        lng = sum(p[1] for p in points) / len(points)
        return GeoLocation(latitude=lat, longitude=lng)

    def _compute_statistics(
        self,
        complaints: list[ComplaintResponse],
    ) -> dict:
        severities = [_complaint_severity_value(item) for item in complaints]
        confidences = [_complaint_confidence(item) for item in complaints]
        avg_severity_value = sum(severities) / len(severities) if severities else 2.0
        avg_confidence = sum(confidences) / len(confidences) if confidences else 0.5
        latest = max(item.submitted_at for item in complaints)
        representative = max(complaints, key=_complaint_confidence)

        villages = sorted({item.village_name for item in complaints if item.village_name})
        affected_area = ", ".join(villages[:5])
        if complaint_landmarks := [c.landmark for c in complaints if c.landmark]:
            affected_area = f"{affected_area} ({complaint_landmarks[0]})"

        count = len(complaints)
        recency_days = max(
            0.0,
            (datetime.now(UTC) - latest).total_seconds() / 86400,
        )
        recency_factor = max(0.0, 1.0 - (recency_days / 30.0))
        hotspot_score = min(
            1.0,
            round((count * 0.12) + (avg_severity_value / 4.0 * 0.45) + (recency_factor * 0.25), 3),
        )
        priority_score = min(
            1.0,
            round((avg_severity_value / 4.0 * 0.6) + (hotspot_score * 0.4), 3),
        )

        return {
            "complaint_count": count,
            "average_severity": _severity_label(avg_severity_value),
            "average_confidence": round(avg_confidence, 3),
            "latest_complaint_date": latest,
            "representative_complaint_id": representative.id,
            "affected_area": affected_area[:512],
            "hotspot_score": hotspot_score,
            "priority_score": priority_score,
            "coordinates": self._centroid(complaints),
            "village_names": villages,
            "village_ids": sorted({item.village_id for item in complaints}),
        }

    def create_cluster_for_complaint(self, complaint: ComplaintResponse) -> ClusterResponse:
        """Create a new cluster with a single seed complaint."""
        stats = self._compute_statistics([complaint])
        cluster = self.cluster_repo.create(
            ClusterCreate(
                title=self._build_cluster_title(complaint),
                description=self._build_cluster_description(complaint),
                theme=self._build_cluster_theme(complaint),
                category=complaint.category,
                complaint_ids=[complaint.id],
                village_ids=stats["village_ids"],
                constituency=complaint.constituency,
                district=complaint.district,
                state=complaint.state,
                metadata=DocumentMetadataCreate(created_by=CLUSTER_ACTOR, updated_by=CLUSTER_ACTOR),
            )
        )
        updated_cluster = self.cluster_repo.update(
            cluster.id,
            ClusterUpdate(
                department=self._resolve_department(complaint),
                village_name=complaint.village_name,
                coordinates=stats["coordinates"],
                representative_complaint_id=stats["representative_complaint_id"],
                average_severity=stats["average_severity"],
                latest_complaint_date=stats["latest_complaint_date"],
                average_confidence=stats["average_confidence"],
                affected_area=stats["affected_area"],
                priority_score=stats["priority_score"],
                hotspot_score=stats["hotspot_score"],
                status=ClusterStatus.OPEN,
                updated_by=CLUSTER_ACTOR,
            ),
        )
        self._link_complaint_to_cluster(
            complaint,
            updated_cluster.id,
            is_duplicate=False,
            duplicate_score=0.0,
            duplicate_reason="Seed complaint for new cluster",
            duplicate_confidence=1.0,
            matched_complaint_id=None,
            matched_cluster_id=None,
        )
        logger.info("Created cluster %s for complaint %s", updated_cluster.id, complaint.id)
        self._trigger_priority_analysis(updated_cluster.id)
        return updated_cluster

    def assign_complaint_to_cluster(
        self,
        complaint: ComplaintResponse,
        cluster_id: str,
        *,
        is_duplicate: bool,
        duplicate_score: float,
        duplicate_reason: str,
        duplicate_confidence: float,
        matched_complaint_id: str | None,
        matched_cluster_id: str | None,
    ) -> ClusterResponse:
        """Add complaint to an existing cluster and refresh statistics."""
        cluster = self.cluster_repo.get_by_id_or_raise(cluster_id)
        complaint_ids = list(cluster.complaint_ids)
        if complaint.id not in complaint_ids:
            complaint_ids.append(complaint.id)

        complaints = [self.complaint_repo.get_by_id_or_raise(cid) for cid in complaint_ids]
        if complaint.id not in [c.id for c in complaints]:
            complaints.append(complaint)

        stats = self._compute_statistics(complaints)
        village_names = sorted(
            set((cluster.village_names or []) + stats["village_names"])
        )

        updated_cluster = self.cluster_repo.update(
            cluster_id,
            ClusterUpdate(
                complaint_ids=complaint_ids,
                complaint_refs=[
                    build_document_path(CollectionNames.COMPLAINTS, cid) for cid in complaint_ids
                ],
                complaint_count=stats["complaint_count"],
                village_ids=stats["village_ids"],
                village_names=village_names,
                coordinates=stats["coordinates"],
                representative_complaint_id=stats["representative_complaint_id"],
                average_severity=stats["average_severity"],
                latest_complaint_date=stats["latest_complaint_date"],
                average_confidence=stats["average_confidence"],
                affected_area=stats["affected_area"],
                priority_score=stats["priority_score"],
                hotspot_score=stats["hotspot_score"],
                status=ClusterStatus.ANALYZING if stats["complaint_count"] > 1 else ClusterStatus.OPEN,
                updated_by=CLUSTER_ACTOR,
            ),
        )
        self._link_complaint_to_cluster(
            complaint,
            cluster_id,
            is_duplicate=is_duplicate,
            duplicate_score=duplicate_score,
            duplicate_reason=duplicate_reason,
            duplicate_confidence=duplicate_confidence,
            matched_complaint_id=matched_complaint_id,
            matched_cluster_id=matched_cluster_id,
        )
        logger.info(
            "Assigned complaint %s to cluster %s (duplicate=%s, score=%.1f)",
            complaint.id,
            cluster_id,
            is_duplicate,
            duplicate_score,
        )
        self._trigger_priority_analysis(cluster_id)
        return updated_cluster

    def _link_complaint_to_cluster(
        self,
        complaint: ComplaintResponse,
        cluster_id: str,
        *,
        is_duplicate: bool,
        duplicate_score: float,
        duplicate_reason: str,
        duplicate_confidence: float,
        matched_complaint_id: str | None,
        matched_cluster_id: str | None,
    ) -> ComplaintResponse:
        return self.complaint_repo.update(
            complaint.id,
            ComplaintUpdate(
                cluster_id=cluster_id,
                cluster_ref=build_document_path(CollectionNames.CLUSTERS, cluster_id),
                status=ComplaintStatus.CLUSTERED,
                is_duplicate=is_duplicate,
                duplicate_score=duplicate_score,
                duplicate_reason=duplicate_reason,
                duplicate_confidence=duplicate_confidence,
                matched_complaint_id=matched_complaint_id,
                matched_cluster_id=matched_cluster_id or cluster_id,
                updated_by=CLUSTER_ACTOR,
            ),
        )

    def refresh_cluster_statistics(self, cluster_id: str) -> ClusterResponse:
        """Recompute cluster statistics from linked complaints."""
        cluster = self.cluster_repo.get_by_id_or_raise(cluster_id)
        complaints = [
            self.complaint_repo.get_by_id_or_raise(cid)
            for cid in cluster.complaint_ids
            if self.complaint_repo.get_by_id(cid) is not None
        ]
        if not complaints:
            return cluster
        stats = self._compute_statistics(complaints)
        return self.cluster_repo.update(
            cluster_id,
            ClusterUpdate(
                complaint_count=stats["complaint_count"],
                representative_complaint_id=stats["representative_complaint_id"],
                average_severity=stats["average_severity"],
                latest_complaint_date=stats["latest_complaint_date"],
                average_confidence=stats["average_confidence"],
                affected_area=stats["affected_area"],
                priority_score=stats["priority_score"],
                hotspot_score=stats["hotspot_score"],
                coordinates=stats["coordinates"],
                updated_by=CLUSTER_ACTOR,
            ),
        )
