"""Build cluster context snapshots and cache fingerprints for priority analysis."""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from datetime import UTC, datetime

from app.models.domain.cluster import ClusterResponse
from app.models.domain.complaint import ComplaintResponse


@dataclass(frozen=True)
class ClusterPriorityContext:
    """Aggregated cluster intelligence payload for Gemini priority analysis."""

    cluster: ClusterResponse
    complaints: list[ComplaintResponse]
    analysis_hash: str
    first_complaint_at: datetime | None
    days_since_first: float | None
    days_since_latest: float | None
    duplicate_complaint_count: int
    max_duplicate_score: float
    avg_duplicate_score: float
    has_image_evidence: bool
    urgent_image_flags: int
    heuristic_priority_score: int


class PriorityCalculator:
    """Prepares cluster evidence and deterministic pre-scores for the priority engine."""

    def build_context(
        self,
        cluster: ClusterResponse,
        complaints: list[ComplaintResponse],
    ) -> ClusterPriorityContext:
        analysis_hash = self.compute_analysis_hash(cluster, complaints)
        now = datetime.now(UTC)

        submitted_dates = [item.submitted_at for item in complaints]
        first_at = min(submitted_dates) if submitted_dates else None
        latest_at = max(submitted_dates) if submitted_dates else cluster.latest_complaint_date

        days_since_first = None
        days_since_latest = None
        if first_at:
            days_since_first = round((now - first_at).total_seconds() / 86400, 2)
        if latest_at:
            days_since_latest = round((now - latest_at).total_seconds() / 86400, 2)

        duplicate_scores = [
            item.duplicate_score
            for item in complaints
            if item.is_duplicate and item.duplicate_score is not None
        ]
        max_duplicate = max(duplicate_scores) if duplicate_scores else 0.0
        avg_duplicate = (
            sum(duplicate_scores) / len(duplicate_scores) if duplicate_scores else 0.0
        )

        has_image = any(item.image_analysis for item in complaints)
        urgent_flags = sum(
            1
            for item in complaints
            if item.image_analysis and item.image_analysis.requires_urgent_attention
        )

        heuristic = self._heuristic_priority_score(
            cluster,
            duplicate_count=len(duplicate_scores),
            max_duplicate=max_duplicate,
            urgent_flags=urgent_flags,
            days_since_latest=days_since_latest,
        )

        return ClusterPriorityContext(
            cluster=cluster,
            complaints=complaints,
            analysis_hash=analysis_hash,
            first_complaint_at=first_at,
            days_since_first=days_since_first,
            days_since_latest=days_since_latest,
            duplicate_complaint_count=len(duplicate_scores),
            max_duplicate_score=max_duplicate,
            avg_duplicate_score=round(avg_duplicate, 2),
            has_image_evidence=has_image,
            urgent_image_flags=urgent_flags,
            heuristic_priority_score=heuristic,
        )

    def compute_analysis_hash(
        self,
        cluster: ClusterResponse,
        complaints: list[ComplaintResponse],
    ) -> str:
        """Fingerprint cluster state to skip redundant Gemini calls."""
        payload = {
            "cluster_id": cluster.id,
            "complaint_ids": sorted(cluster.complaint_ids),
            "complaint_count": cluster.complaint_count,
            "average_severity": cluster.average_severity,
            "hotspot_score": cluster.hotspot_score,
            "latest_complaint_date": (
                cluster.latest_complaint_date.isoformat() if cluster.latest_complaint_date else None
            ),
            "complaints": [
                {
                    "id": item.id,
                    "analysis_status": str(item.analysis_status),
                    "severity": (
                        item.image_analysis.severity
                        if item.image_analysis
                        else item.ai_analysis.severity if item.ai_analysis else None
                    ),
                    "is_duplicate": item.is_duplicate,
                    "duplicate_score": item.duplicate_score,
                    "priority": str(item.priority),
                }
                for item in sorted(complaints, key=lambda c: c.id)
            ],
        }
        digest = hashlib.sha256(
            json.dumps(payload, sort_keys=True, default=str).encode("utf-8")
        ).hexdigest()
        return digest[:32]

    def _heuristic_priority_score(
        self,
        cluster: ClusterResponse,
        *,
        duplicate_count: int,
        max_duplicate: float,
        urgent_flags: int,
        days_since_latest: float | None,
    ) -> int:
        """Deterministic baseline score used as guidance in the Gemini prompt."""
        score = 30.0
        score += min(25.0, cluster.complaint_count * 4.0)
        score += cluster.hotspot_score * 20.0
        score += min(15.0, duplicate_count * 3.0)
        score += min(10.0, max_duplicate / 10.0)
        score += urgent_flags * 5.0

        severity = (cluster.average_severity or "Medium").lower()
        severity_bonus = {"low": 0, "medium": 5, "high": 12, "critical": 20}
        score += severity_bonus.get(severity, 5)

        if days_since_latest is not None and days_since_latest <= 3:
            score += 8.0
        elif days_since_latest is not None and days_since_latest <= 7:
            score += 4.0

        return int(min(100, round(score)))
