"""Analytics dashboard API schemas."""

from __future__ import annotations

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field

from app.models.schemas.priority_portal import PriorityClusterCard, PriorityRecommendationPanel


ActivityType = Literal[
    "complaint_submitted",
    "ai_analysis_completed",
    "image_analysis_completed",
    "cluster_created",
    "cluster_updated",
    "priority_updated",
    "recommendation_generated",
]


class DashboardKPIs(BaseModel):
    """Executive KPI metrics for the MP command center."""

    total_complaints: int = 0
    open_complaints: int = 0
    resolved_complaints: int = 0
    active_clusters: int = 0
    critical_issues: int = 0
    average_ai_priority_score: float = 0.0
    departments_involved: int = 0
    villages_covered: int = 0
    todays_complaints: int = 0
    todays_ai_analyses: int = 0


class ChartDataPoint(BaseModel):
    name: str
    value: float


class TrendDataPoint(BaseModel):
    date: str
    count: int


class DashboardCharts(BaseModel):
    complaints_by_category: list[ChartDataPoint] = Field(default_factory=list)
    complaints_by_department: list[ChartDataPoint] = Field(default_factory=list)
    priority_distribution: list[ChartDataPoint] = Field(default_factory=list)
    severity_distribution: list[ChartDataPoint] = Field(default_factory=list)
    village_wise_complaints: list[ChartDataPoint] = Field(default_factory=list)
    department_workload: list[ChartDataPoint] = Field(default_factory=list)
    complaint_trend_daily: list[TrendDataPoint] = Field(default_factory=list)
    complaint_trend_weekly: list[TrendDataPoint] = Field(default_factory=list)
    complaint_trend_monthly: list[TrendDataPoint] = Field(default_factory=list)
    top_categories: list[ChartDataPoint] = Field(default_factory=list)
    top_villages: list[ChartDataPoint] = Field(default_factory=list)
    top_departments: list[ChartDataPoint] = Field(default_factory=list)


class DashboardActivityItem(BaseModel):
    id: str
    type: ActivityType
    title: str
    description: str
    entity_id: str
    entity_type: str
    occurred_at: datetime
    metadata: dict[str, str] = Field(default_factory=dict)


class DashboardComplaintSummary(BaseModel):
    id: str
    title: str
    category_name: str
    status: str
    village_name: str
    priority_score: float | None = None
    severity: str | None = None
    submitted_at: datetime
    has_ai_analysis: bool = False
    cluster_id: str | None = None


class DashboardClusterSummary(BaseModel):
    id: str
    title: str
    complaint_count: int
    average_severity: str | None = None
    priority_score: int = 0
    village_name: str | None = None
    department: str | None = None
    latest_complaint_date: datetime | None = None
    representative_complaint_id: str | None = None


class DashboardDepartmentSummary(BaseModel):
    department: str
    complaint_count: int
    cluster_count: int
    average_priority_score: float


class DashboardVillageSummary(BaseModel):
    village_name: str
    complaint_count: int
    cluster_count: int
    average_priority_score: float


class DashboardAIInsights(BaseModel):
    highest_risk_area: str
    most_common_issue: str
    department_overload: str
    trending_complaints: list[str] = Field(default_factory=list)
    fastest_growing_cluster: str | None = None
    suggested_actions: list[str] = Field(default_factory=list)
    todays_highlights: list[str] = Field(default_factory=list)


class DashboardHomeResponse(BaseModel):
    """Unified MP command center dashboard payload."""

    success: bool = True
    kpis: DashboardKPIs
    top_priorities: list[PriorityClusterCard] = Field(default_factory=list)
    recommendations: list[PriorityRecommendationPanel] = Field(default_factory=list)
    recent_complaints: list[DashboardComplaintSummary] = Field(default_factory=list)
    cluster_summary: list[DashboardClusterSummary] = Field(default_factory=list)
    department_summary: list[DashboardDepartmentSummary] = Field(default_factory=list)
    village_summary: list[DashboardVillageSummary] = Field(default_factory=list)
    recent_activities: list[DashboardActivityItem] = Field(default_factory=list)
    ai_insights: DashboardAIInsights
    charts: DashboardCharts
    last_updated_at: datetime


class DashboardActivitiesResponse(BaseModel):
    success: bool = True
    items: list[DashboardActivityItem]
    total: int


class DashboardAnalyticsResponse(BaseModel):
    success: bool = True
    charts: DashboardCharts
    kpis: DashboardKPIs
    ai_insights: DashboardAIInsights
