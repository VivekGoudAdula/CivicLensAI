"""Priority dashboard API schemas."""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field

from app.models.domain.cluster import ClusterPriorityAnalysis
from app.models.enums.common import ClusterStatus, ComplaintCategory


class PriorityClusterCard(BaseModel):
    """Priority-ranked cluster summary for dashboard cards."""

    id: str
    title: str
    category: ComplaintCategory
    status: ClusterStatus
    village_name: str | None = None
    department: str | None = None
    complaint_count: int
    priority_score: int = 0
    impact_score: int = 0
    urgency_level: str | None = None
    risk_level: str | None = None
    priority_rank: int | None = None
    recommended_department: str | None = None
    recommended_action: str | None = None
    affected_population: str | None = None
    priority_confidence: float | None = None
    latest_complaint_date: datetime | None = None
    priority_updated_at: datetime | None = None


class PriorityRecommendationPanel(BaseModel):
    """Explainable AI recommendation for a priority cluster."""

    cluster_id: str
    cluster_title: str
    priority_rank: int
    priority_score: int
    impact_score: int
    why_priority_ranked_high: str
    contributing_factors: list[str] = Field(default_factory=list)
    expected_impact: str
    estimated_beneficiaries: str
    recommended_action: str
    estimated_resolution_time: str | None = None
    estimated_budget: str | None = None
    confidence_score: float
    reasoning: str


class PriorityBreakdownItem(BaseModel):
    """Grouped priority metrics."""

    label: str
    count: int
    average_priority_score: float
    average_impact_score: float


class PriorityDashboardResponse(BaseModel):
    """Full priority intelligence dashboard payload."""

    success: bool = True
    total_analyzed_clusters: int
    critical_clusters: int
    high_urgency_clusters: int
    average_priority_score: float
    average_impact_score: float
    top_priorities: list[PriorityClusterCard] = Field(default_factory=list)
    leaderboard: list[PriorityClusterCard] = Field(default_factory=list)
    critical_issues: list[PriorityClusterCard] = Field(default_factory=list)
    highest_impact_areas: list[PriorityClusterCard] = Field(default_factory=list)
    department_breakdown: list[PriorityBreakdownItem] = Field(default_factory=list)
    village_breakdown: list[PriorityBreakdownItem] = Field(default_factory=list)
    recommendations: list[PriorityRecommendationPanel] = Field(default_factory=list)
    last_updated_at: datetime | None = None


class PriorityAnalyzeResponse(BaseModel):
    """Response after analyzing a single cluster."""

    success: bool = True
    message: str
    cluster_id: str
    priority_analysis: ClusterPriorityAnalysis | None = None


class PriorityRerankResponse(BaseModel):
    """Response after batch priority recalculation."""

    success: bool = True
    message: str
    clusters_analyzed: int
    clusters_skipped: int
    ranks_updated: int
    errors: list[str] = Field(default_factory=list)
