"""GIS aggregation service for constituency map visualization."""

from __future__ import annotations

import logging
from datetime import UTC, datetime

from app.db.pagination import PaginationParams
from app.models.domain.cluster import ClusterResponse
from app.models.domain.complaint import ComplaintResponse
from app.models.enums.common import ComplaintStatus
from app.models.schemas.gis_portal import GisBounds, GisClusterMarker, GisComplaintPin, GisMapResponse
from app.repositories.cluster_repository import ClusterRepository
from app.repositories.complaint_repository import ComplaintRepository

logger = logging.getLogger(__name__)

AMETHI_CENTER = (26.1539, 81.8139)

PRIORITY_HEAT = {
    "critical": 1.0,
    "high": 0.8,
    "medium": 0.5,
    "low": 0.3,
}

SEVERITY_HEAT = {
    "critical": 1.0,
    "high": 0.85,
    "medium": 0.55,
    "low": 0.3,
}


class GisPortalService:
    """Builds geo-intelligence payloads for the interactive constituency map."""

    def __init__(
        self,
        complaint_repo: ComplaintRepository,
        cluster_repo: ClusterRepository,
    ):
        self.complaint_repo = complaint_repo
        self.cluster_repo = cluster_repo

    def _load_complaints(self, *, limit: int = 500) -> list[ComplaintResponse]:
        result = self.complaint_repo.list(
            pagination=PaginationParams(limit=limit, order_by="submitted_at", order_direction="desc"),
        )
        return result.items

    def _load_clusters(self, *, limit: int = 500) -> list[ClusterResponse]:
        result = self.cluster_repo.list(
            pagination=PaginationParams(limit=limit, order_by="complaint_count", order_direction="desc"),
        )
        return result.items

    def _complaint_department(self, complaint: ComplaintResponse) -> str:
        if complaint.ai_analysis and complaint.ai_analysis.responsible_department:
            return complaint.ai_analysis.responsible_department
        if complaint.image_analysis and complaint.image_analysis.suggested_department:
            return complaint.image_analysis.suggested_department
        return "Unassigned"

    def _complaint_severity(self, complaint: ComplaintResponse) -> str | None:
        if complaint.image_analysis:
            return complaint.image_analysis.severity
        if complaint.ai_analysis:
            return complaint.ai_analysis.severity
        return None

    def _ai_confidence(self, complaint: ComplaintResponse) -> float | None:
        if complaint.ai_analysis:
            return complaint.ai_analysis.confidence_score
        if complaint.image_analysis:
            return complaint.image_analysis.confidence_score
        return None

    def _heat_weight_complaint(self, complaint: ComplaintResponse) -> float:
        if complaint.status in {ComplaintStatus.RESOLVED, ComplaintStatus.CLOSED}:
            return 0.2
        priority = complaint.priority.value if hasattr(complaint.priority, "value") else str(complaint.priority)
        base = PRIORITY_HEAT.get(priority.lower(), 0.5)
        severity = self._complaint_severity(complaint)
        if severity:
            base = max(base, SEVERITY_HEAT.get(severity.lower(), base))
        confidence = self._ai_confidence(complaint)
        if confidence:
            base = min(1.0, base * (0.7 + confidence * 0.3))
        return round(base, 3)

    def _cluster_lookup(self, clusters: list[ClusterResponse]) -> dict[str, ClusterResponse]:
        return {cluster.id: cluster for cluster in clusters}

    def _build_bounds(
        self,
        complaints: list[GisComplaintPin],
        clusters: list[GisClusterMarker],
    ) -> GisBounds | None:
        lats: list[float] = []
        lngs: list[float] = []
        for pin in complaints:
            lats.append(pin.latitude)
            lngs.append(pin.longitude)
        for marker in clusters:
            lats.append(marker.latitude)
            lngs.append(marker.longitude)

        if not lats:
            return GisBounds(
                south=AMETHI_CENTER[0] - 0.15,
                west=AMETHI_CENTER[1] - 0.15,
                north=AMETHI_CENTER[0] + 0.15,
                east=AMETHI_CENTER[1] + 0.15,
                center_lat=AMETHI_CENTER[0],
                center_lng=AMETHI_CENTER[1],
            )

        south, north = min(lats), max(lats)
        west, east = min(lngs), max(lngs)
        padding = 0.02
        return GisBounds(
            south=south - padding,
            west=west - padding,
            north=north + padding,
            east=east + padding,
            center_lat=(south + north) / 2,
            center_lng=(west + east) / 2,
        )

    def _to_complaint_pin(
        self,
        complaint: ComplaintResponse,
        cluster_lookup: dict[str, ClusterResponse],
    ) -> GisComplaintPin | None:
        if not complaint.location:
            return None
        cluster = cluster_lookup.get(complaint.cluster_id) if complaint.cluster_id else None
        priority = complaint.priority.value if hasattr(complaint.priority, "value") else str(complaint.priority)
        return GisComplaintPin(
            id=complaint.id,
            title=complaint.title,
            description=complaint.description[:500],
            latitude=complaint.location.latitude,
            longitude=complaint.location.longitude,
            category=complaint.category_name or complaint.category.value,
            department=self._complaint_department(complaint),
            priority=priority,
            severity=self._complaint_severity(complaint),
            status=complaint.status.value,
            village_name=complaint.village_name,
            cluster_id=complaint.cluster_id,
            cluster_title=cluster.title if cluster else None,
            ai_summary=complaint.ai_analysis.summary if complaint.ai_analysis else None,
            ai_confidence=self._ai_confidence(complaint),
            has_image=bool(complaint.image_base64),
            address=complaint.location.address,
            submitted_at=complaint.submitted_at,
            heat_weight=self._heat_weight_complaint(complaint),
        )

    def _to_cluster_marker(self, cluster: ClusterResponse) -> GisClusterMarker | None:
        if not cluster.coordinates:
            return None
        avg_priority = (
            cluster.priority_analysis.priority_score
            if cluster.priority_analysis
            else int((cluster.priority_score or 0) * 100)
        )
        cluster_score = avg_priority
        heat_weight = min(
            1.0,
            (cluster.hotspot_score or 0) * 0.5 + (cluster.complaint_count / 20) * 0.3 + avg_priority / 100 * 0.2,
        )
        return GisClusterMarker(
            id=cluster.id,
            title=cluster.title,
            latitude=cluster.coordinates.latitude,
            longitude=cluster.coordinates.longitude,
            complaint_count=cluster.complaint_count,
            average_priority=float(avg_priority),
            highest_severity=cluster.average_severity,
            representative_complaint_id=cluster.representative_complaint_id,
            cluster_score=float(cluster_score),
            department=cluster.recommended_department or cluster.department,
            village_name=cluster.village_name,
            hotspot_score=cluster.hotspot_score or 0.0,
            heat_weight=round(heat_weight, 3),
        )

    def get_map_data(self) -> GisMapResponse:
        complaints_raw = self._load_complaints()
        clusters_raw = self._load_clusters()
        cluster_lookup = self._cluster_lookup(clusters_raw)

        complaints = [
            pin
            for complaint in complaints_raw
            if (pin := self._to_complaint_pin(complaint, cluster_lookup)) is not None
        ]
        clusters = [
            marker
            for cluster in clusters_raw
            if (marker := self._to_cluster_marker(cluster)) is not None
        ]

        return GisMapResponse(
            complaints=complaints,
            clusters=clusters,
            bounds=self._build_bounds(complaints, clusters),
            total_complaints=len(complaints),
            total_clusters=len(clusters),
            last_updated_at=datetime.now(UTC),
        )
