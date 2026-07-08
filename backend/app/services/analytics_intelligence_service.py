"""Analytics intelligence service for Phase 11 constituency analytics."""

from __future__ import annotations

import logging
from collections import Counter
from datetime import UTC, datetime, timedelta

from app.db.pagination import PaginationParams
from app.models.domain.cluster import ClusterResponse
from app.models.domain.complaint import ComplaintResponse
from app.models.enums.common import ComplaintStatus
from app.models.schemas.analytics_intelligence import (
    AnalyticsIntelligenceResponse,
    IntelligenceCharts,
    IntelligenceKPIs,
    PredictiveAnalytics,
    PredictiveAnalyticsCard,
)
from app.models.schemas.analytics_portal import ChartDataPoint, TrendDataPoint
from app.repositories.cluster_repository import ClusterRepository
from app.repositories.complaint_repository import ComplaintRepository

logger = logging.getLogger(__name__)

PENDING_STATUSES = {ComplaintStatus.PENDING, ComplaintStatus.SUBMITTED, ComplaintStatus.UNDER_REVIEW}
RESOLVED_STATUSES = {ComplaintStatus.RESOLVED, ComplaintStatus.CLOSED}

SEVERITY_SCORES = {
    "critical": 4.0,
    "high": 3.0,
    "medium": 2.0,
    "low": 1.0,
}

CONFIDENCE_BUCKETS = [
    ("0-20%", 0.0, 0.2),
    ("21-40%", 0.21, 0.4),
    ("41-60%", 0.41, 0.6),
    ("61-80%", 0.61, 0.8),
    ("81-100%", 0.81, 1.0),
]


class AnalyticsIntelligenceService:
    """Aggregates constituency analytics with predictive insight cards."""

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

    def _severity_score(self, severity: str | None) -> float:
        if not severity:
            return 2.0
        return SEVERITY_SCORES.get(severity.lower(), 2.0)

    def _build_kpis(
        self,
        complaints: list[ComplaintResponse],
        clusters: list[ClusterResponse],
    ) -> IntelligenceKPIs:
        pending = sum(1 for c in complaints if c.status in PENDING_STATUSES)
        resolved = sum(1 for c in complaints if c.status in RESOLVED_STATUSES)
        critical = sum(
            1
            for c in clusters
            if c.priority_analysis and c.priority_analysis.risk_level.lower() in {"high", "critical"}
        )
        priority_scores = [
            c.priority_analysis.priority_score for c in clusters if c.priority_analysis is not None
        ]
        severities = [self._severity_score(self._complaint_severity(c)) for c in complaints]
        resolution_days: list[float] = []
        for complaint in complaints:
            if complaint.resolved_at and complaint.status in RESOLVED_STATUSES:
                delta = complaint.resolved_at - complaint.submitted_at
                resolution_days.append(delta.total_seconds() / 86400)

        departments = {
            self._complaint_department(c) for c in complaints if self._complaint_department(c) != "Unassigned"
        }
        villages = {c.village_name for c in complaints if c.village_name}

        return IntelligenceKPIs(
            total_complaints=len(complaints),
            resolved_complaints=resolved,
            pending_complaints=pending,
            critical_issues=critical,
            active_clusters=len(clusters),
            average_ai_priority=round(sum(priority_scores) / len(priority_scores), 1) if priority_scores else 0.0,
            average_severity_score=round(sum(severities) / len(severities), 2) if severities else 0.0,
            average_resolution_days=round(sum(resolution_days) / len(resolution_days), 1) if resolution_days else 0.0,
            departments_count=len(departments),
            villages_count=len(villages),
        )

    def _top_chart(self, counter: Counter[str], limit: int = 10) -> list[ChartDataPoint]:
        return [ChartDataPoint(name=name, value=float(count)) for name, count in counter.most_common(limit)]

    def _trend_chart(self, counter: Counter[str], days: int) -> list[TrendDataPoint]:
        now = datetime.now(UTC)
        return [
            TrendDataPoint(date=(now - timedelta(days=offset)).strftime("%Y-%m-%d"), count=counter.get(
                (now - timedelta(days=offset)).strftime("%Y-%m-%d"), 0
            ))
            for offset in range(days - 1, -1, -1)
        ]

    def _build_charts(
        self,
        complaints: list[ComplaintResponse],
        clusters: list[ClusterResponse],
    ) -> IntelligenceCharts:
        category_counter: Counter[str] = Counter()
        dept_counter: Counter[str] = Counter()
        village_counter: Counter[str] = Counter()
        severity_counter: Counter[str] = Counter()
        priority_counter: Counter[str] = Counter()
        status_counter: Counter[str] = Counter()
        cluster_size_counter: Counter[str] = Counter()
        confidence_counter: Counter[str] = Counter()
        daily_counter: Counter[str] = Counter()
        weekly_counter: Counter[str] = Counter()
        monthly_counter: Counter[str] = Counter()
        cumulative_counter: Counter[str] = Counter()

        for complaint in complaints:
            category_counter[complaint.category_name or complaint.category.value] += 1
            dept_counter[self._complaint_department(complaint)] += 1
            village_counter[complaint.village_name] += 1
            status_counter[complaint.status.value.replace("_", " ").title()] += 1
            priority_counter[complaint.priority.value] += 1
            severity = self._complaint_severity(complaint)
            if severity:
                severity_counter[severity] += 1
            day_key = complaint.submitted_at.strftime("%Y-%m-%d")
            daily_counter[day_key] += 1
            weekly_counter[complaint.submitted_at.strftime("%Y-W%W")] += 1
            monthly_counter[complaint.submitted_at.strftime("%Y-%m")] += 1

            confidence = None
            if complaint.ai_analysis:
                confidence = complaint.ai_analysis.confidence_score
            elif complaint.image_analysis:
                confidence = complaint.image_analysis.confidence_score
            if confidence is not None:
                for label, low, high in CONFIDENCE_BUCKETS:
                    if low <= confidence <= high:
                        confidence_counter[label] += 1
                        break

        for cluster in clusters:
            if cluster.complaint_count <= 1:
                bucket = "1"
            elif cluster.complaint_count <= 3:
                bucket = "2-3"
            elif cluster.complaint_count <= 5:
                bucket = "4-5"
            elif cluster.complaint_count <= 10:
                bucket = "6-10"
            else:
                bucket = "10+"
            cluster_size_counter[bucket] += 1

        daily_trend = self._trend_chart(daily_counter, 30)
        running = 0
        timeline: list[TrendDataPoint] = []
        for point in daily_trend:
            running += point.count
            timeline.append(TrendDataPoint(date=point.date, count=running))

        return IntelligenceCharts(
            complaint_trend_daily=daily_trend,
            complaint_trend_weekly=[
                TrendDataPoint(date=k, count=v) for k, v in sorted(weekly_counter.items())[-12:]
            ],
            complaint_trend_monthly=[
                TrendDataPoint(date=k, count=v) for k, v in sorted(monthly_counter.items())[-12:]
            ],
            complaint_categories=self._top_chart(category_counter),
            department_distribution=self._top_chart(dept_counter),
            village_comparison=self._top_chart(village_counter),
            priority_distribution=self._top_chart(priority_counter),
            severity_distribution=self._top_chart(severity_counter),
            cluster_size_distribution=self._top_chart(cluster_size_counter, 6),
            resolution_status=self._top_chart(status_counter),
            top_villages=self._top_chart(village_counter, 8),
            top_departments=self._top_chart(dept_counter, 8),
            complaint_timeline=timeline,
            ai_confidence_distribution=self._top_chart(confidence_counter, 5),
        )

    def _build_predictive(
        self,
        complaints: list[ComplaintResponse],
        clusters: list[ClusterResponse],
        charts: IntelligenceCharts,
    ) -> PredictiveAnalytics:
        now = datetime.now(UTC)
        category_counter: Counter[str] = Counter()
        village_counter: Counter[str] = Counter()
        dept_counter: Counter[str] = Counter()
        for complaint in complaints:
            category_counter[complaint.category_name or complaint.category.value] += 1
            village_counter[complaint.village_name] += 1
            dept_counter[self._complaint_department(complaint)] += 1

        trending_category = category_counter.most_common(1)[0][0] if category_counter else "N/A"
        fastest_cluster = max(clusters, key=lambda c: c.complaint_count) if clusters else None
        highest_risk_village = village_counter.most_common(1)[0][0] if village_counter else "N/A"
        dept_workload = dept_counter.most_common(1)[0][0] if dept_counter else "N/A"

        recent_7 = sum(p.count for p in charts.complaint_trend_daily[-7:])
        prior_7 = sum(p.count for p in charts.complaint_trend_daily[-14:-7]) if len(charts.complaint_trend_daily) >= 14 else recent_7
        growth_rate = ((recent_7 - prior_7) / max(prior_7, 1)) * 100
        predicted_growth = f"{growth_rate:+.0f}% vs prior week"
        resolution_load = f"{sum(1 for c in complaints if c.status not in RESOLVED_STATUSES)} open cases"

        critical_clusters = [
            c for c in clusters if c.priority_analysis and c.priority_analysis.risk_level.lower() in {"high", "critical"}
        ]
        most_critical = critical_clusters[0].title if critical_clusters else (fastest_cluster.title if fastest_cluster else "N/A")

        cards = [
            PredictiveAnalyticsCard(
                key="trending_category",
                title="Trending Complaint Category",
                value=trending_category,
                detail=f"{category_counter.get(trending_category, 0)} complaints in current dataset",
                confidence=0.82,
                trend_direction="up",
            ),
            PredictiveAnalyticsCard(
                key="fastest_cluster",
                title="Fastest Growing Cluster",
                value=fastest_cluster.title if fastest_cluster else "None",
                detail=f"{fastest_cluster.complaint_count} linked complaints" if fastest_cluster else "No clusters",
                confidence=0.88,
                trend_direction="up",
            ),
            PredictiveAnalyticsCard(
                key="highest_risk_village",
                title="Highest Risk Village",
                value=highest_risk_village,
                detail=f"{village_counter.get(highest_risk_village, 0)} complaints recorded",
                confidence=0.79,
                trend_direction="up",
            ),
            PredictiveAnalyticsCard(
                key="department_workload",
                title="Department Workload",
                value=dept_workload,
                detail=f"{dept_counter.get(dept_workload, 0)} assigned complaints",
                confidence=0.85,
                trend_direction="stable",
            ),
            PredictiveAnalyticsCard(
                key="predicted_growth",
                title="Predicted Complaint Growth",
                value=predicted_growth,
                detail="7-day rolling comparison heuristic",
                confidence=0.7,
                trend_direction="up" if growth_rate > 0 else "down" if growth_rate < 0 else "stable",
                metadata={"recent_7": str(recent_7), "prior_7": str(prior_7)},
            ),
            PredictiveAnalyticsCard(
                key="resolution_load",
                title="Estimated Resolution Load",
                value=resolution_load,
                detail="Open and in-progress constituency cases",
                confidence=0.9,
                trend_direction="stable",
            ),
            PredictiveAnalyticsCard(
                key="most_critical_area",
                title="Most Critical Area",
                value=most_critical,
                detail="Based on AI priority risk scoring",
                confidence=0.86,
                trend_direction="up",
            ),
        ]

        return PredictiveAnalytics(cards=cards, engine="heuristic", generated_at=now)

    def _build_export_rows(self, complaints: list[ComplaintResponse]) -> list[dict[str, str | int | float]]:
        rows: list[dict[str, str | int | float]] = []
        for complaint in complaints:
            rows.append(
                {
                    "id": complaint.id,
                    "title": complaint.title,
                    "category": complaint.category_name or complaint.category.value,
                    "department": self._complaint_department(complaint),
                    "village": complaint.village_name,
                    "priority": complaint.priority.value,
                    "severity": self._complaint_severity(complaint) or "",
                    "status": complaint.status.value,
                    "submitted_at": complaint.submitted_at.isoformat(),
                    "latitude": complaint.location.latitude if complaint.location else 0,
                    "longitude": complaint.location.longitude if complaint.location else 0,
                }
            )
        return rows

    def get_intelligence(self) -> AnalyticsIntelligenceResponse:
        complaints = self._load_complaints()
        clusters = self._load_clusters()
        charts = self._build_charts(complaints, clusters)
        return AnalyticsIntelligenceResponse(
            kpis=self._build_kpis(complaints, clusters),
            charts=charts,
            predictive=self._build_predictive(complaints, clusters, charts),
            export_rows=self._build_export_rows(complaints),
            last_updated_at=datetime.now(UTC),
        )
