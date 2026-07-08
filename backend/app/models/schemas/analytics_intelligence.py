"""Analytics intelligence API schemas for Phase 11 constituency analytics."""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field

from app.models.schemas.analytics_portal import ChartDataPoint, TrendDataPoint


class IntelligenceKPIs(BaseModel):
    """Extended KPI metrics for the analytics intelligence page."""

    total_complaints: int = 0
    resolved_complaints: int = 0
    pending_complaints: int = 0
    critical_issues: int = 0
    active_clusters: int = 0
    average_ai_priority: float = 0.0
    average_severity_score: float = 0.0
    average_resolution_days: float = 0.0
    departments_count: int = 0
    villages_count: int = 0


class IntelligenceCharts(BaseModel):
    """Fourteen professional analytics charts."""

    complaint_trend_daily: list[TrendDataPoint] = Field(default_factory=list)
    complaint_trend_weekly: list[TrendDataPoint] = Field(default_factory=list)
    complaint_trend_monthly: list[TrendDataPoint] = Field(default_factory=list)
    complaint_categories: list[ChartDataPoint] = Field(default_factory=list)
    department_distribution: list[ChartDataPoint] = Field(default_factory=list)
    village_comparison: list[ChartDataPoint] = Field(default_factory=list)
    priority_distribution: list[ChartDataPoint] = Field(default_factory=list)
    severity_distribution: list[ChartDataPoint] = Field(default_factory=list)
    cluster_size_distribution: list[ChartDataPoint] = Field(default_factory=list)
    resolution_status: list[ChartDataPoint] = Field(default_factory=list)
    top_villages: list[ChartDataPoint] = Field(default_factory=list)
    top_departments: list[ChartDataPoint] = Field(default_factory=list)
    complaint_timeline: list[TrendDataPoint] = Field(default_factory=list)
    ai_confidence_distribution: list[ChartDataPoint] = Field(default_factory=list)


class PredictiveAnalyticsCard(BaseModel):
    """AI-ready predictive insight card with extensible metadata."""

    key: str
    title: str
    value: str
    detail: str
    confidence: float = Field(ge=0, le=1, default=0.75)
    trend_direction: str = "stable"
    model_version: str = "heuristic-v1"
    metadata: dict[str, str] = Field(default_factory=dict)


class PredictiveAnalytics(BaseModel):
    """Predictive analytics panel — pluggable for future ML models."""

    cards: list[PredictiveAnalyticsCard] = Field(default_factory=list)
    engine: str = "heuristic"
    generated_at: datetime


class AnalyticsIntelligenceResponse(BaseModel):
    """Full constituency analytics intelligence payload."""

    success: bool = True
    kpis: IntelligenceKPIs
    charts: IntelligenceCharts
    predictive: PredictiveAnalytics
    export_rows: list[dict[str, str | int | float]] = Field(default_factory=list)
    last_updated_at: datetime
