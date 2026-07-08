"""Recommendation domain models."""

from datetime import datetime

from pydantic import BaseModel, Field

from app.models.enums.common import RecommendationPriority, RecommendationStatus
from app.models.schemas.common import DocumentMetadata, DocumentMetadataCreate


class RecommendationAIContent(BaseModel):
    """AI-generated recommendation content."""

    rationale: str = Field(max_length=4000)
    action_items: list[str] = Field(default_factory=list, max_length=30)
    expected_impact: str = Field(max_length=2000)
    risk_assessment: str = Field(max_length=2000)
    confidence_score: float = Field(ge=0, le=1)
    generated_at: datetime
    model_version: str = Field(default="gemini-2.0-flash", max_length=64)


class RecommendationBase(BaseModel):
    """Shared recommendation fields."""

    title: str = Field(min_length=5, max_length=256)
    description: str = Field(min_length=10, max_length=5000)
    status: RecommendationStatus = RecommendationStatus.DRAFT
    priority: RecommendationPriority = RecommendationPriority.MEDIUM
    cluster_ids: list[str] = Field(default_factory=list, max_length=100)
    cluster_refs: list[str] = Field(
        default_factory=list,
        max_length=100,
        description="Firestore paths: clusters/{id}",
    )
    department_id: str = Field(min_length=1, max_length=128)
    department_ref: str = Field(description="Firestore path: departments/{id}")
    department_name: str = Field(max_length=256)
    department_code: str = Field(max_length=32)
    village_ids: list[str] = Field(default_factory=list, max_length=200)
    constituency: str = Field(max_length=128)
    district: str = Field(max_length=128)
    state: str = Field(max_length=64)
    estimated_budget_inr: float | None = Field(default=None, ge=0)
    estimated_timeline_days: int | None = Field(default=None, ge=1)
    ai_recommendation: RecommendationAIContent | None = None
    assigned_official: str | None = Field(default=None, max_length=128)
    due_date: datetime | None = None
    completed_at: datetime | None = None


class RecommendationCreate(BaseModel):
    """Fields required to create a recommendation."""

    title: str = Field(min_length=5, max_length=256)
    description: str = Field(min_length=10, max_length=5000)
    priority: RecommendationPriority = RecommendationPriority.MEDIUM
    cluster_ids: list[str] = Field(default_factory=list, max_length=100)
    department_id: str = Field(min_length=1, max_length=128)
    department_name: str = Field(max_length=256)
    department_code: str = Field(max_length=32)
    village_ids: list[str] = Field(default_factory=list, max_length=200)
    constituency: str = Field(max_length=128)
    district: str = Field(max_length=128)
    state: str = Field(max_length=64)
    estimated_budget_inr: float | None = Field(default=None, ge=0)
    estimated_timeline_days: int | None = Field(default=None, ge=1)
    ai_recommendation: RecommendationAIContent | None = None
    assigned_official: str | None = Field(default=None, max_length=128)
    due_date: datetime | None = None
    metadata: DocumentMetadataCreate = Field(default_factory=DocumentMetadataCreate)


class RecommendationUpdate(BaseModel):
    """Fields allowed on recommendation update."""

    title: str | None = Field(default=None, min_length=5, max_length=256)
    description: str | None = Field(default=None, min_length=10, max_length=5000)
    status: RecommendationStatus | None = None
    priority: RecommendationPriority | None = None
    cluster_ids: list[str] | None = None
    cluster_refs: list[str] | None = None
    department_id: str | None = Field(default=None, max_length=128)
    department_ref: str | None = None
    department_name: str | None = Field(default=None, max_length=256)
    department_code: str | None = Field(default=None, max_length=32)
    village_ids: list[str] | None = None
    estimated_budget_inr: float | None = Field(default=None, ge=0)
    estimated_timeline_days: int | None = Field(default=None, ge=1)
    ai_recommendation: RecommendationAIContent | None = None
    assigned_official: str | None = Field(default=None, max_length=128)
    due_date: datetime | None = None
    completed_at: datetime | None = None
    updated_by: str = Field(default="system", max_length=128)


class RecommendationResponse(RecommendationBase):
    """Recommendation document returned from Firestore."""

    id: str
    metadata: DocumentMetadata


class RecommendationSearchFilters(BaseModel):
    """Filter parameters for recommendation queries."""

    constituency: str | None = None
    district: str | None = None
    state: str | None = None
    department_id: str | None = None
    cluster_id: str | None = None
    village_id: str | None = None
    status: RecommendationStatus | None = None
    priority: RecommendationPriority | None = None
    due_before: datetime | None = None
    due_after: datetime | None = None
