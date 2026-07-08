"""Analytics aggregation service for the MP command center dashboard."""

from __future__ import annotations

import logging
from collections import Counter, defaultdict
from datetime import UTC, datetime, timedelta

from app.db.pagination import PaginationParams
from app.models.domain.cluster import ClusterResponse
from app.models.domain.complaint import ComplaintResponse, ComplaintSearchFilters
from app.models.enums.common import ComplaintStatus
from app.models.schemas.analytics_portal import (
    ChartDataPoint,
    DashboardActivityItem,
    DashboardAIInsights,
    DashboardAnalyticsResponse,
    DashboardActivitiesResponse,
    DashboardCharts,
    DashboardClusterSummary,
    DashboardComplaintSummary,
    DashboardDepartmentSummary,
    DashboardHomeResponse,
    DashboardKPIs,
    DashboardVillageSummary,
    TrendDataPoint,
)
from app.models.schemas.priority_portal import PriorityClusterCard, PriorityRecommendationPanel
from app.repositories.cluster_repository import ClusterRepository
from app.repositories.complaint_repository import ComplaintRepository
from app.services.priority_portal_service import PriorityPortalService

logger = logging.getLogger(__name__)

OPEN_STATUSES = {
    ComplaintStatus.PENDING,
    ComplaintStatus.SUBMITTED,
    ComplaintStatus.UNDER_REVIEW,
    ComplaintStatus.CLUSTERED,
    ComplaintStatus.IN_PROGRESS,
}

RESOLVED_STATUSES = {ComplaintStatus.RESOLVED, ComplaintStatus.CLOSED}


class AnalyticsPortalService:
    """Aggregates live constituency intelligence for the MP dashboard."""

    def __init__(
        self,
        complaint_repo: ComplaintRepository,
        cluster_repo: ClusterRepository,
        priority_portal: PriorityPortalService,
    ):
        self.complaint_repo = complaint_repo
        self.cluster_repo = cluster_repo
        self.priority_portal = priority_portal

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

    def _complaint_severity(self, complaint: ComplaintResponse) -> str | None:
        if complaint.image_analysis:
            return complaint.image_analysis.severity
        if complaint.ai_analysis:
            return complaint.ai_analysis.severity
        return None

    def _complaint_department(self, complaint: ComplaintResponse) -> str:
        if complaint.ai_analysis and complaint.ai_analysis.responsible_department:
            return complaint.ai_analysis.responsible_department
        if complaint.image_analysis and complaint.image_analysis.suggested_department:
            return complaint.image_analysis.suggested_department
        return "Unassigned"

    def _build_kpis(
        self,
        complaints: list[ComplaintResponse],
        clusters: list[ClusterResponse],
    ) -> DashboardKPIs:
        today = datetime.now(UTC).date()
        open_count = sum(1 for c in complaints if c.status in OPEN_STATUSES)
        resolved_count = sum(1 for c in complaints if c.status in RESOLVED_STATUSES)
        critical = sum(
            1
            for c in clusters
            if c.priority_analysis
            and c.priority_analysis.risk_level.lower() in {"high", "critical"}
        )
        priority_scores = [
            c.priority_analysis.priority_score
            for c in clusters
            if c.priority_analysis is not None
        ]
        departments = {
            self._complaint_department(c)
            for c in complaints
            if self._complaint_department(c) != "Unassigned"
        }
        villages = {c.village_name for c in complaints if c.village_name}
        todays_complaints = sum(1 for c in complaints if c.submitted_at.date() == today)
        todays_ai = sum(
            1
            for c in complaints
            if c.analysis_completed_at and c.analysis_completed_at.date() == today
        )

        return DashboardKPIs(
            total_complaints=len(complaints),
            open_complaints=open_count,
            resolved_complaints=resolved_count,
            active_clusters=len(clusters),
            critical_issues=critical,
            average_ai_priority_score=round(sum(priority_scores) / len(priority_scores), 1)
            if priority_scores
            else 0.0,
            departments_involved=len(departments),
            villages_covered=len(villages),
            todays_complaints=todays_complaints,
            todays_ai_analyses=todays_ai,
        )

    def _build_charts(
        self,
        complaints: list[ComplaintResponse],
        clusters: list[ClusterResponse],
    ) -> DashboardCharts:
        category_counter: Counter[str] = Counter()
        dept_counter: Counter[str] = Counter()
        village_counter: Counter[str] = Counter()
        severity_counter: Counter[str] = Counter()
        priority_counter: Counter[str] = Counter()
        daily_counter: Counter[str] = Counter()
        weekly_counter: Counter[str] = Counter()
        monthly_counter: Counter[str] = Counter()

        now = datetime.now(UTC)
        for complaint in complaints:
            category_counter[complaint.category_name or complaint.category.value] += 1
            dept_counter[self._complaint_department(complaint)] += 1
            village_counter[complaint.village_name] += 1
            severity = self._complaint_severity(complaint)
            if severity:
                severity_counter[severity] += 1
            day_key = complaint.submitted_at.strftime("%Y-%m-%d")
            daily_counter[day_key] += 1
            week_key = complaint.submitted_at.strftime("%Y-W%W")
            weekly_counter[week_key] += 1
            month_key = complaint.submitted_at.strftime("%Y-%m")
            monthly_counter[month_key] += 1

        for cluster in clusters:
            if cluster.priority_analysis:
                bucket = f"{cluster.priority_analysis.priority_score // 10 * 10}-{cluster.priority_analysis.priority_score // 10 * 10 + 9}"
                priority_counter[bucket] += 1
            elif cluster.urgency_level:
                priority_counter[cluster.urgency_level] += 1

        def top_chart(counter: Counter[str], limit: int = 10) -> list[ChartDataPoint]:
            return [
                ChartDataPoint(name=name, value=count)
                for name, count in counter.most_common(limit)
            ]

        def trend_chart(counter: Counter[str], days: int) -> list[TrendDataPoint]:
            points: list[TrendDataPoint] = []
            for offset in range(days - 1, -1, -1):
                day = (now - timedelta(days=offset)).strftime("%Y-%m-%d")
                points.append(TrendDataPoint(date=day, count=counter.get(day, 0)))
            return points

        return DashboardCharts(
            complaints_by_category=top_chart(category_counter),
            complaints_by_department=top_chart(dept_counter),
            priority_distribution=top_chart(priority_counter, 8),
            severity_distribution=top_chart(severity_counter, 6),
            village_wise_complaints=top_chart(village_counter),
            department_workload=top_chart(dept_counter),
            complaint_trend_daily=trend_chart(daily_counter, 14),
            complaint_trend_weekly=[
                TrendDataPoint(date=key, count=count)
                for key, count in sorted(weekly_counter.items())[-8:]
            ],
            complaint_trend_monthly=[
                TrendDataPoint(date=key, count=count)
                for key, count in sorted(monthly_counter.items())[-6:]
            ],
            top_categories=top_chart(category_counter, 5),
            top_villages=top_chart(village_counter, 5),
            top_departments=top_chart(dept_counter, 5),
        )

    def _build_activities(
        self,
        complaints: list[ComplaintResponse],
        clusters: list[ClusterResponse],
        *,
        limit: int = 50,
    ) -> list[DashboardActivityItem]:
        events: list[DashboardActivityItem] = []

        for complaint in complaints:
            events.append(
                DashboardActivityItem(
                    id=f"submit-{complaint.id}",
                    type="complaint_submitted",
                    title="Complaint Submitted",
                    description=complaint.title,
                    entity_id=complaint.id,
                    entity_type="complaint",
                    occurred_at=complaint.submitted_at,
                    metadata={"village": complaint.village_name, "status": complaint.status.value},
                )
            )
            if complaint.analysis_completed_at:
                events.append(
                    DashboardActivityItem(
                        id=f"ai-{complaint.id}",
                        type="ai_analysis_completed",
                        title="AI Analysis Completed",
                        description=complaint.title,
                        entity_id=complaint.id,
                        entity_type="complaint",
                        occurred_at=complaint.analysis_completed_at,
                    )
                )
            if complaint.vision_completed_at:
                events.append(
                    DashboardActivityItem(
                        id=f"vision-{complaint.id}",
                        type="image_analysis_completed",
                        title="Image Analysis Completed",
                        description=complaint.title,
                        entity_id=complaint.id,
                        entity_type="complaint",
                        occurred_at=complaint.vision_completed_at,
                    )
                )

        for cluster in clusters:
            events.append(
                DashboardActivityItem(
                    id=f"cluster-create-{cluster.id}",
                    type="cluster_created",
                    title="Cluster Created",
                    description=cluster.title,
                    entity_id=cluster.id,
                    entity_type="cluster",
                    occurred_at=cluster.metadata.created_at,
                    metadata={"complaint_count": str(cluster.complaint_count)},
                )
            )
            if cluster.priority_updated_at:
                events.append(
                    DashboardActivityItem(
                        id=f"priority-{cluster.id}",
                        type="priority_updated",
                        title="Priority Updated",
                        description=cluster.title,
                        entity_id=cluster.id,
                        entity_type="cluster",
                        occurred_at=cluster.priority_updated_at,
                        metadata={
                            "priority_score": str(
                                cluster.priority_analysis.priority_score
                                if cluster.priority_analysis
                                else int((cluster.priority_score or 0) * 100)
                            )
                        },
                    )
                )
            if cluster.metadata.updated_at > cluster.metadata.created_at:
                events.append(
                    DashboardActivityItem(
                        id=f"cluster-update-{cluster.id}",
                        type="cluster_updated",
                        title="Cluster Updated",
                        description=cluster.title,
                        entity_id=cluster.id,
                        entity_type="cluster",
                        occurred_at=cluster.metadata.updated_at,
                    )
                )

        events.sort(key=lambda item: item.occurred_at, reverse=True)
        return events[:limit]

    def _build_ai_insights(
        self,
        complaints: list[ComplaintResponse],
        clusters: list[ClusterResponse],
        charts: DashboardCharts,
    ) -> DashboardAIInsights:
        highest_risk = "No analyzed clusters yet"
        ranked = [
            c
            for c in clusters
            if c.priority_analysis is not None
        ]
        if ranked:
            top = max(ranked, key=lambda c: c.priority_analysis.priority_score if c.priority_analysis else 0)
            highest_risk = f"{top.title} ({top.village_name or 'Unknown village'})"

        most_common = charts.top_categories[0].name if charts.top_categories else "No data"
        dept_overload = charts.top_departments[0].name if charts.top_departments else "No data"

        trending = [point.date for point in charts.complaint_trend_daily[-3:] if point.count > 0]
        fastest_cluster = None
        if clusters:
            fastest = max(clusters, key=lambda c: c.complaint_count)
            fastest_cluster = f"{fastest.title} ({fastest.complaint_count} complaints)"

        suggested_actions = [
            cluster.priority_analysis.recommended_action
            for cluster in ranked[:3]
            if cluster.priority_analysis and cluster.priority_analysis.recommended_action
        ]
        highlights = [
            f"{charts.complaint_trend_daily[-1].count} complaints submitted today"
            if charts.complaint_trend_daily
            else "No complaints today",
            f"{len(ranked)} clusters with AI priority scores",
            f"{len({c.village_name for c in complaints})} villages covered",
        ]

        return DashboardAIInsights(
            highest_risk_area=highest_risk,
            most_common_issue=most_common,
            department_overload=dept_overload,
            trending_complaints=trending,
            fastest_growing_cluster=fastest_cluster,
            suggested_actions=suggested_actions[:5],
            todays_highlights=highlights,
        )

    def _complaint_summary(self, complaint: ComplaintResponse) -> DashboardComplaintSummary:
        priority_score = None
        if complaint.duplicate_score:
            priority_score = complaint.duplicate_score
        return DashboardComplaintSummary(
            id=complaint.id,
            title=complaint.title,
            category_name=complaint.category_name or complaint.category.value,
            status=complaint.status.value,
            village_name=complaint.village_name,
            priority_score=priority_score,
            severity=self._complaint_severity(complaint),
            submitted_at=complaint.submitted_at,
            has_ai_analysis=complaint.ai_analysis is not None,
            cluster_id=complaint.cluster_id,
        )

    def _cluster_summary(self, cluster: ClusterResponse) -> DashboardClusterSummary:
        score = (
            cluster.priority_analysis.priority_score
            if cluster.priority_analysis
            else int((cluster.priority_score or 0) * 100)
        )
        return DashboardClusterSummary(
            id=cluster.id,
            title=cluster.title,
            complaint_count=cluster.complaint_count,
            average_severity=cluster.average_severity,
            priority_score=score,
            village_name=cluster.village_name,
            department=cluster.department or cluster.recommended_department,
            latest_complaint_date=cluster.latest_complaint_date,
            representative_complaint_id=cluster.representative_complaint_id,
        )

    def _department_summary(
        self,
        complaints: list[ComplaintResponse],
        clusters: list[ClusterResponse],
    ) -> list[DashboardDepartmentSummary]:
        dept_complaints: Counter[str] = Counter()
        dept_clusters: Counter[str] = Counter()
        dept_priority: dict[str, list[int]] = defaultdict(list)

        for complaint in complaints:
            dept = self._complaint_department(complaint)
            dept_complaints[dept] += 1

        for cluster in clusters:
            dept = cluster.recommended_department or cluster.department or "Unassigned"
            dept_clusters[dept] += 1
            if cluster.priority_analysis:
                dept_priority[dept].append(cluster.priority_analysis.priority_score)

        departments = set(dept_complaints) | set(dept_clusters)
        items = [
            DashboardDepartmentSummary(
                department=dept,
                complaint_count=dept_complaints.get(dept, 0),
                cluster_count=dept_clusters.get(dept, 0),
                average_priority_score=round(
                    sum(dept_priority.get(dept, [0])) / max(len(dept_priority.get(dept, [0])), 1),
                    1,
                ),
            )
            for dept in departments
        ]
        items.sort(key=lambda item: item.complaint_count, reverse=True)
        return items[:10]

    def _village_summary(
        self,
        complaints: list[ComplaintResponse],
        clusters: list[ClusterResponse],
    ) -> list[DashboardVillageSummary]:
        village_complaints: Counter[str] = Counter()
        village_clusters: Counter[str] = Counter()
        village_priority: dict[str, list[int]] = defaultdict(list)

        for complaint in complaints:
            village_complaints[complaint.village_name] += 1
        for cluster in clusters:
            village = cluster.village_name or (cluster.village_names[0] if cluster.village_names else "Unknown")
            village_clusters[village] += 1
            if cluster.priority_analysis:
                village_priority[village].append(cluster.priority_analysis.priority_score)

        villages = set(village_complaints) | set(village_clusters)
        items = [
            DashboardVillageSummary(
                village_name=village,
                complaint_count=village_complaints.get(village, 0),
                cluster_count=village_clusters.get(village, 0),
                average_priority_score=round(
                    sum(village_priority.get(village, [0])) / max(len(village_priority.get(village, [0])), 1),
                    1,
                ),
            )
            for village in villages
        ]
        items.sort(key=lambda item: item.complaint_count, reverse=True)
        return items[:10]

    def get_home_dashboard(self) -> DashboardHomeResponse:
        complaints = self._load_complaints()
        clusters = self._load_clusters()
        kpis = self._build_kpis(complaints, clusters)
        charts = self._build_charts(complaints, clusters)
        priority_dashboard = self.priority_portal.get_dashboard()

        return DashboardHomeResponse(
            kpis=kpis,
            top_priorities=priority_dashboard.top_priorities[:10],
            recommendations=priority_dashboard.recommendations[:5],
            recent_complaints=[self._complaint_summary(c) for c in complaints[:8]],
            cluster_summary=[self._cluster_summary(c) for c in clusters[:8]],
            department_summary=self._department_summary(complaints, clusters),
            village_summary=self._village_summary(complaints, clusters),
            recent_activities=self._build_activities(complaints, clusters, limit=12),
            ai_insights=self._build_ai_insights(complaints, clusters, charts),
            charts=charts,
            last_updated_at=datetime.now(UTC),
        )

    def get_activities(self, *, limit: int = 100) -> DashboardActivitiesResponse:
        complaints = self._load_complaints()
        clusters = self._load_clusters()
        items = self._build_activities(complaints, clusters, limit=limit)
        return DashboardActivitiesResponse(items=items, total=len(items))

    def get_analytics_overview(self) -> DashboardAnalyticsResponse:
        complaints = self._load_complaints()
        clusters = self._load_clusters()
        charts = self._build_charts(complaints, clusters)
        return DashboardAnalyticsResponse(
            charts=charts,
            kpis=self._build_kpis(complaints, clusters),
            ai_insights=self._build_ai_insights(complaints, clusters, charts),
        )
