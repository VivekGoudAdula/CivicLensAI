"""Cluster portal API schemas."""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field

from app.models.domain.cluster import ClusterAIInsights, ClusterPriorityAnalysis
from app.models.enums.common import ClusterStatus, ComplaintCategory
from app.models.schemas.common import DocumentMetadata, GeoLocation


class ClusterListItem(BaseModel):
    """Summary cluster for dashboard list views."""

    id: str
    title: str
    theme: str
    category: ComplaintCategory
    status: ClusterStatus
    department: str | None = None
    village_name: str | None = None
    complaint_count: int
    average_severity: str | None = None
    latest_complaint_date: datetime | None = None
    representative_complaint_id: str | None = None
    priority_score: float = 0.5
    hotspot_score: float = 0.0
    average_confidence: float | None = None
    affected_area: str | None = None
    impact_score: int | None = None
    urgency_level: str | None = None
    priority_rank: int | None = None
    recommended_department: str | None = None
    recommended_action: str | None = None
    priority_confidence: float | None = None
    priority_updated_at: datetime | None = None


class ClusterComplaintSummary(BaseModel):
    """Lightweight complaint summary for cluster detail views."""

    id: str
    title: str
    status: str
    village_name: str
    submitted_at: datetime
    is_duplicate: bool = False
    duplicate_score: float | None = None
    priority: str


class ClusterDetailResponse(BaseModel):
    """Full cluster detail for dashboard."""

    id: str
    title: str
    description: str
    theme: str
    category: ComplaintCategory
    status: ClusterStatus
    department: str | None = None
    village_name: str | None = None
    village_names: list[str] = Field(default_factory=list)
    coordinates: GeoLocation | None = None
    complaint_ids: list[str] = Field(default_factory=list)
    complaint_count: int = 0
    representative_complaint_id: str | None = None
    average_severity: str | None = None
    latest_complaint_date: datetime | None = None
    average_confidence: float | None = None
    affected_area: str | None = None
    priority_score: float = 0.5
    hotspot_score: float = 0.0
    constituency: str
    district: str
    state: str
    ai_insights: ClusterAIInsights | None = None
    priority_analysis: ClusterPriorityAnalysis | None = None
    impact_score: int | None = None
    urgency_level: str | None = None
    priority_rank: int | None = None
    recommended_department: str | None = None
    recommended_action: str | None = None
    estimated_budget: str | None = None
    estimated_resolution_time: str | None = None
    affected_population: str | None = None
    priority_reasoning: str | None = None
    priority_confidence: float | None = None
    priority_updated_at: datetime | None = None
    metadata: DocumentMetadata
    related_complaints: list[ClusterComplaintSummary] = Field(default_factory=list)


class ClusterListResponse(BaseModel):
    """Paginated cluster list response."""

    success: bool = True
    items: list[ClusterListItem]
    total: int
    page: int
    page_size: int
    has_more: bool


class ClusterDashboardSummary(BaseModel):
    """Aggregate cluster metrics for dashboard KPIs."""

    success: bool = True
    total_clusters: int
    open_clusters: int
    total_clustered_complaints: int
    average_cluster_size: float
    top_hotspots: list[ClusterListItem] = Field(default_factory=list)


class ClusterProcessResponse(BaseModel):
    """Response after triggering complaint clustering."""

    success: bool = True
    message: str
    complaint_id: str
    cluster_id: str | None = None
    is_duplicate: bool = False
    duplicate_score: float | None = None
