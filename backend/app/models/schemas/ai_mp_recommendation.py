"""Gemini MP decision recommendation engine schemas."""

from __future__ import annotations

from pydantic import BaseModel, Field


class MpDevelopmentWorkItem(BaseModel):
    """Single AI-recommended development work for the MP."""

    priority_rank: int = Field(ge=1, le=10)
    project_title: str = Field(max_length=256)
    category: str = Field(max_length=128)
    village: str = Field(max_length=128)
    department: str = Field(max_length=256)
    reason: str = Field(max_length=2000)
    impact_score: int = Field(ge=0, le=100)
    priority_score: int = Field(ge=0, le=100)
    urgency: str = Field(max_length=32)
    estimated_beneficiaries: str = Field(max_length=512)
    estimated_budget: str = Field(max_length=256)
    estimated_resolution_time: str = Field(max_length=256)
    government_scheme: str | None = Field(default=None, max_length=512)
    expected_social_impact: str = Field(max_length=2000)
    expected_infrastructure_improvement: str = Field(max_length=2000)
    ai_confidence: float = Field(ge=0, le=1)
    risk_if_ignored: str = Field(max_length=2000)
    executive_summary: str = Field(max_length=1500)
    detailed_explanation: str = Field(max_length=5000)
    recommended_action: str = Field(max_length=2000)
    cluster_id: str | None = Field(default=None, max_length=128)


class GeminiMpRecommendationOutput(BaseModel):
    """Strict JSON output from Gemini decision engine."""

    executive_brief: str = Field(max_length=3000)
    decision_timeline_summary: str = Field(max_length=2000)
    recommendations: list[MpDevelopmentWorkItem] = Field(min_length=1, max_length=10)
