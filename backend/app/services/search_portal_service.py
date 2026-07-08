"""Unified global search across complaints, clusters, and recommendations."""

from __future__ import annotations

import logging
import time
from datetime import UTC, datetime

from app.db.pagination import PaginationParams
from app.models.domain.cluster import ClusterSearchFilters
from app.models.domain.complaint import ComplaintSearchFilters
from app.models.domain.recommendation import RecommendationSearchFilters
from app.models.enums.common import ComplaintStatus
from app.models.schemas.search_portal import (
    GlobalSearchFilters,
    GlobalSearchResponse,
    GlobalSearchResultItem,
    SearchSortOption,
)
from app.repositories.cluster_repository import ClusterRepository
from app.repositories.complaint_repository import ComplaintRepository
from app.repositories.recommendation_repository import RecommendationRepository

logger = logging.getLogger(__name__)

RESOLVED_STATUSES = {ComplaintStatus.RESOLVED, ComplaintStatus.CLOSED}


class SearchPortalService:
    """Enterprise global search with pagination and client-side ranking."""

    def __init__(
        self,
        complaint_repo: ComplaintRepository,
        cluster_repo: ClusterRepository,
        recommendation_repo: RecommendationRepository,
    ):
        self.complaint_repo = complaint_repo
        self.cluster_repo = cluster_repo
        self.recommendation_repo = recommendation_repo

    def _highlight(self, text: str, query: str) -> str:
        if not query:
            return text[:120]
        lower = text.lower()
        idx = lower.find(query.lower())
        if idx < 0:
            return text[:120]
        start = max(0, idx - 30)
        return text[start : start + 120]

    def _complaint_department(self, complaint) -> str | None:
        if complaint.ai_analysis and complaint.ai_analysis.responsible_department:
            return complaint.ai_analysis.responsible_department
        if complaint.image_analysis and complaint.image_analysis.suggested_department:
            return complaint.image_analysis.suggested_department
        return None

    def _complaint_severity(self, complaint) -> str | None:
        if complaint.image_analysis:
            return complaint.image_analysis.severity
        if complaint.ai_analysis:
            return complaint.ai_analysis.severity
        return None

    def _score_match(self, haystack: str, query: str) -> float:
        if not query:
            return 0.5
        lower = haystack.lower()
        q = query.lower()
        if lower == q:
            return 1.0
        if lower.startswith(q):
            return 0.9
        if q in lower:
            return 0.75
        return 0.0

    def _apply_complaint_filters(self, complaint, filters: GlobalSearchFilters) -> bool:
        if filters.village and filters.village.lower() not in complaint.village_name.lower():
            return False
        if filters.category:
            cat = complaint.category_name or complaint.category.value
            if filters.category.lower() not in cat.lower():
                return False
        if filters.department:
            dept = self._complaint_department(complaint) or ""
            if filters.department.lower() not in dept.lower():
                return False
        if filters.priority and complaint.priority.value != filters.priority.lower():
            return False
        if filters.severity:
            sev = self._complaint_severity(complaint) or ""
            if filters.severity.lower() not in sev.lower():
                return False
        if filters.status and complaint.status.value != filters.status.lower():
            return False
        if filters.cluster_id and complaint.cluster_id != filters.cluster_id:
            return False
        if filters.resolved is True and complaint.status not in RESOLVED_STATUSES:
            return False
        if filters.resolved is False and complaint.status in RESOLVED_STATUSES:
            return False
        if filters.date_from and complaint.submitted_at < datetime.fromisoformat(filters.date_from):
            return False
        if filters.date_to:
            end = datetime.fromisoformat(filters.date_to).replace(hour=23, minute=59, second=59)
            if complaint.submitted_at > end:
                return False
        if filters.ai_confidence_min is not None and complaint.ai_analysis:
            if complaint.ai_analysis.confidence_score < filters.ai_confidence_min:
                return False
        return True

    def _sort_items(
        self,
        items: list[GlobalSearchResultItem],
        sort: SearchSortOption,
    ) -> list[GlobalSearchResultItem]:
        if sort == "oldest":
            return sorted(items, key=lambda i: i.occurred_at or datetime.min.replace(tzinfo=UTC))
        if sort == "alphabetical":
            return sorted(items, key=lambda i: i.title.lower())
        if sort == "highest_priority":
            return sorted(items, key=lambda i: i.score, reverse=True)
        if sort == "highest_severity":
            severity_rank = {"critical": 4, "high": 3, "medium": 2, "low": 1}
            return sorted(
                items,
                key=lambda i: severity_rank.get((i.severity or "").lower(), 0),
                reverse=True,
            )
        if sort == "most_complaints":
            return sorted(
                items,
                key=lambda i: float(i.description) if i.type == "cluster" and i.description.isdigit() else 0,
                reverse=True,
            )
        return sorted(items, key=lambda i: i.occurred_at or datetime.min.replace(tzinfo=UTC), reverse=True)

    def search(
        self,
        query: str,
        *,
        filters: GlobalSearchFilters | None = None,
        sort: SearchSortOption = "newest",
        limit: int = 50,
    ) -> GlobalSearchResponse:
        started = time.perf_counter()
        filters = filters or GlobalSearchFilters()
        normalized = query.strip()
        items: list[GlobalSearchResultItem] = []

        complaint_filters = ComplaintSearchFilters(
            status=ComplaintStatus(filters.status) if filters.status else None,
            cluster_id=filters.cluster_id,
        )
        complaints = self.complaint_repo.search(
            normalized,
            filters=complaint_filters if any(vars(complaint_filters).values()) else None,
            pagination=PaginationParams(limit=200, order_by="submitted_at", order_direction="desc"),
        ).items

        for complaint in complaints:
            if not self._apply_complaint_filters(complaint, filters):
                continue
            haystack = " ".join(
                [
                    complaint.title,
                    complaint.description,
                    complaint.village_name,
                    complaint.category_name or "",
                    self._complaint_department(complaint) or "",
                    complaint.ai_analysis.summary if complaint.ai_analysis else "",
                    " ".join(complaint.ai_analysis.keywords) if complaint.ai_analysis else "",
                    complaint.location.address if complaint.location and complaint.location.address else "",
                ]
            )
            score = self._score_match(haystack, normalized) if normalized else 0.6
            if normalized and score <= 0:
                continue
            items.append(
                GlobalSearchResultItem(
                    id=complaint.id,
                    type="complaint",
                    title=complaint.title,
                    subtitle=complaint.village_name,
                    description=complaint.description[:200],
                    category=complaint.category_name or complaint.category.value,
                    department=self._complaint_department(complaint),
                    village=complaint.village_name,
                    priority=complaint.priority.value,
                    severity=self._complaint_severity(complaint),
                    status=complaint.status.value,
                    score=score,
                    highlight=self._highlight(haystack, normalized),
                    url_path=f"/complaints/{complaint.id}",
                    occurred_at=complaint.submitted_at,
                )
            )

        clusters = self.cluster_repo.search(
            normalized,
            pagination=PaginationParams(limit=100, order_by="complaint_count", order_direction="desc"),
        ).items
        for cluster in clusters:
            haystack = f"{cluster.title} {cluster.description} {cluster.village_name or ''}"
            score = self._score_match(haystack, normalized) if normalized else 0.55
            if normalized and score <= 0:
                continue
            items.append(
                GlobalSearchResultItem(
                    id=cluster.id,
                    type="cluster",
                    title=cluster.title,
                    subtitle=f"{cluster.complaint_count} complaints",
                    description=str(cluster.complaint_count),
                    category=cluster.category.value,
                    department=cluster.recommended_department or cluster.department,
                    village=cluster.village_name,
                    priority=str(
                        cluster.priority_analysis.priority_score
                        if cluster.priority_analysis
                        else int((cluster.priority_score or 0) * 100)
                    ),
                    severity=cluster.average_severity,
                    status=cluster.status.value,
                    score=score,
                    highlight=self._highlight(haystack, normalized),
                    url_path=f"/civic-insights/clusters/{cluster.id}",
                    occurred_at=cluster.latest_complaint_date,
                )
            )

        recommendations = self.recommendation_repo.search(
            normalized,
            pagination=PaginationParams(limit=50, order_by="metadata.created_at", order_direction="desc"),
        ).items
        for rec in recommendations:
            haystack = f"{rec.title} {rec.description} {rec.department_name}"
            score = self._score_match(haystack, normalized) if normalized else 0.5
            if normalized and score <= 0:
                continue
            items.append(
                GlobalSearchResultItem(
                    id=rec.id,
                    type="recommendation",
                    title=rec.title,
                    subtitle=rec.department_name,
                    description=rec.description[:200],
                    department=rec.department_name,
                    priority=rec.priority.value,
                    status=rec.status.value,
                    score=score,
                    highlight=self._highlight(haystack, normalized),
                    url_path="/recommendations",
                    occurred_at=rec.metadata.created_at,
                )
            )

        items = self._sort_items(items, sort)[:limit]
        suggestions = list({item.title.split(" ")[0] for item in items[:5] if item.title})

        took_ms = int((time.perf_counter() - started) * 1000)
        return GlobalSearchResponse(
            query=normalized,
            items=items,
            total=len(items),
            suggestions=suggestions,
            took_ms=took_ms,
        )
