"""Recommendation portal API schemas."""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field

from app.models.schemas.ai_mp_recommendation import MpDevelopmentWorkItem


class RecommendationCenterResponse(BaseModel):
    """AI Decision Recommendation Center payload."""

    success: bool = True
    executive_brief: str
    decision_timeline_summary: str
    recommendations: list[MpDevelopmentWorkItem]
    total_recommendations: int
    engine: str
    model_version: str
    prompt_version: str
    context_hash: str
    generated_at: datetime
    from_cache: bool = False


class RecommendationGenerateResponse(BaseModel):
    success: bool
    message: str
    center: RecommendationCenterResponse | None = None


class RecommendationListItem(BaseModel):
    id: str
    title: str
    description: str
    status: str
    priority: str
    department_name: str
    village_names: list[str] = Field(default_factory=list)
    estimated_budget_inr: float | None = None
    estimated_timeline_days: int | None = None
    confidence_score: float | None = None
    created_at: datetime


class RecommendationListResponse(BaseModel):
    success: bool = True
    items: list[RecommendationListItem]
    total: int
