"""Cluster domain models."""

from datetime import datetime

from pydantic import BaseModel, Field

from app.models.enums.common import ClusterStatus, ComplaintCategory
from app.models.schemas.common import DocumentMetadata, DocumentMetadataCreate, GeoLocation


class ClusterAIInsights(BaseModel):
    """AI-generated insights for a complaint cluster."""

    summary: str = Field(max_length=3000)
    root_causes: list[str] = Field(default_factory=list, max_length=20)
    affected_population_estimate: int | None = Field(default=None, ge=0)
    priority_score: float = Field(ge=0, le=1)
    key_themes: list[str] = Field(default_factory=list, max_length=20)
    generated_at: datetime
    model_version: str = Field(default="gemini-2.0-flash", max_length=64)


class ClusterPriorityAnalysis(BaseModel):
    """Gemini-powered government priority intelligence for a cluster."""

    priority_score: int = Field(ge=0, le=100)
    impact_score: int = Field(ge=0, le=100)
    urgency_level: str = Field(max_length=32)
    risk_level: str = Field(max_length=32)
    affected_population_estimate: str = Field(max_length=512)
    public_safety_risk: str = Field(max_length=2000)
    infrastructure_criticality: str = Field(max_length=2000)
    environmental_impact: str = Field(max_length=2000)
    economic_impact: str = Field(max_length=2000)
    suggested_department: str = Field(max_length=256)
    recommended_action: str = Field(max_length=3000)
    estimated_resolution_time: str = Field(max_length=256)
    estimated_budget_range: str = Field(max_length=256)
    priority_rank: int | None = Field(default=None, ge=1)
    reasoning: str = Field(max_length=5000)
    confidence_score: float = Field(ge=0, le=1)
    contributing_factors: list[str] = Field(default_factory=list, max_length=20)
    expected_impact: str = Field(max_length=2000)
    estimated_beneficiaries: str = Field(max_length=512)
    why_priority_ranked_high: str = Field(max_length=2000)
    analysis_hash: str = Field(max_length=64)
    processed_at: datetime
    model_version: str = Field(default="gemini-2.5-flash", max_length=64)
    prompt_version: str = Field(default="1.0.0", max_length=16)


class ClusterBase(BaseModel):
    """Shared cluster fields."""

    title: str = Field(min_length=5, max_length=256)
    description: str = Field(min_length=10, max_length=5000)
    theme: str = Field(min_length=3, max_length=256)
    category: ComplaintCategory
    status: ClusterStatus = ClusterStatus.OPEN
    complaint_ids: list[str] = Field(default_factory=list, max_length=500)
    complaint_refs: list[str] = Field(
        default_factory=list,
        max_length=500,
        description="Firestore paths: complaints/{id}",
    )
    complaint_count: int = Field(default=0, ge=0)
    village_ids: list[str] = Field(default_factory=list, max_length=200)
    village_names: list[str] = Field(default_factory=list, max_length=200)
    village_name: str | None = Field(default=None, max_length=128)
    department: str | None = Field(default=None, max_length=256)
    coordinates: GeoLocation | None = None
    representative_complaint_id: str | None = Field(default=None, max_length=128)
    average_severity: str | None = Field(default=None, max_length=32)
    latest_complaint_date: datetime | None = None
    average_confidence: float | None = Field(default=None, ge=0, le=1)
    affected_area: str | None = Field(default=None, max_length=512)
    priority_score: float = Field(default=0.5, ge=0, le=1)
    hotspot_score: float = Field(default=0.0, ge=0, le=1)
    constituency: str = Field(max_length=128)
    district: str = Field(max_length=128)
    state: str = Field(max_length=64)
    ai_insights: ClusterAIInsights | None = None
    priority_analysis: ClusterPriorityAnalysis | None = None
    impact_score: int | None = Field(default=None, ge=0, le=100)
    urgency_level: str | None = Field(default=None, max_length=32)
    priority_rank: int | None = Field(default=None, ge=1)
    recommended_department: str | None = Field(default=None, max_length=256)
    recommended_action: str | None = Field(default=None, max_length=3000)
    estimated_budget: str | None = Field(default=None, max_length=256)
    estimated_resolution_time: str | None = Field(default=None, max_length=256)
    affected_population: str | None = Field(default=None, max_length=512)
    priority_reasoning: str | None = Field(default=None, max_length=5000)
    priority_confidence: float | None = Field(default=None, ge=0, le=1)
    priority_updated_at: datetime | None = None
    priority_analysis_hash: str | None = Field(default=None, max_length=64)


class ClusterCreate(BaseModel):
    """Fields required to create a cluster."""

    title: str = Field(min_length=5, max_length=256)
    description: str = Field(min_length=10, max_length=5000)
    theme: str = Field(min_length=3, max_length=256)
    category: ComplaintCategory
    complaint_ids: list[str] = Field(default_factory=list, max_length=500)
    village_ids: list[str] = Field(default_factory=list, max_length=200)
    constituency: str = Field(max_length=128)
    district: str = Field(max_length=128)
    state: str = Field(max_length=64)
    metadata: DocumentMetadataCreate = Field(default_factory=DocumentMetadataCreate)


class ClusterUpdate(BaseModel):
    """Fields allowed on cluster update."""

    title: str | None = Field(default=None, min_length=5, max_length=256)
    description: str | None = Field(default=None, min_length=10, max_length=5000)
    theme: str | None = Field(default=None, min_length=3, max_length=256)
    category: ComplaintCategory | None = None
    status: ClusterStatus | None = None
    complaint_ids: list[str] | None = None
    complaint_refs: list[str] | None = None
    complaint_count: int | None = Field(default=None, ge=0)
    village_ids: list[str] | None = None
    village_names: list[str] | None = None
    village_name: str | None = Field(default=None, max_length=128)
    department: str | None = Field(default=None, max_length=256)
    coordinates: GeoLocation | None = None
    representative_complaint_id: str | None = Field(default=None, max_length=128)
    average_severity: str | None = Field(default=None, max_length=32)
    latest_complaint_date: datetime | None = None
    average_confidence: float | None = Field(default=None, ge=0, le=1)
    affected_area: str | None = Field(default=None, max_length=512)
    priority_score: float | None = Field(default=None, ge=0, le=1)
    hotspot_score: float | None = Field(default=None, ge=0, le=1)
    priority_analysis: ClusterPriorityAnalysis | None = None
    impact_score: int | None = Field(default=None, ge=0, le=100)
    urgency_level: str | None = Field(default=None, max_length=32)
    priority_rank: int | None = Field(default=None, ge=1)
    recommended_department: str | None = Field(default=None, max_length=256)
    recommended_action: str | None = Field(default=None, max_length=3000)
    estimated_budget: str | None = Field(default=None, max_length=256)
    estimated_resolution_time: str | None = Field(default=None, max_length=256)
    affected_population: str | None = Field(default=None, max_length=512)
    priority_reasoning: str | None = None
    priority_confidence: float | None = Field(default=None, ge=0, le=1)
    priority_updated_at: datetime | None = None
    priority_analysis_hash: str | None = Field(default=None, max_length=64)
    ai_insights: ClusterAIInsights | None = None
    updated_by: str = Field(default="system", max_length=128)


class ClusterResponse(ClusterBase):
    """Cluster document returned from Firestore."""

    id: str
    metadata: DocumentMetadata
    recommendation_ids: list[str] = Field(default_factory=list, max_length=100)


class ClusterSearchFilters(BaseModel):
    """Filter parameters for cluster queries."""

    constituency: str | None = None
    district: str | None = None
    state: str | None = None
    village_id: str | None = None
    category: ComplaintCategory | None = None
    status: ClusterStatus | None = None
    min_complaint_count: int | None = Field(default=None, ge=0)
    theme_prefix: str | None = Field(default=None, max_length=256)
