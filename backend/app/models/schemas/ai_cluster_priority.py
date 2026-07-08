"""Strict JSON schema for Gemini cluster priority analysis output."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field, field_validator

UrgencyLevel = Literal["Low", "Medium", "High", "Critical"]
RiskLevel = Literal["Low", "Medium", "High", "Critical"]


def _normalize_level(value: str) -> str:
    cleaned = value.strip().lower()
    mapping = {
        "low": "Low",
        "medium": "Medium",
        "high": "High",
        "critical": "Critical",
    }
    return mapping.get(cleaned, "Medium")


class GeminiClusterPriorityOutput(BaseModel):
    """Validated Gemini priority engine JSON response."""

    priority_score: int = Field(ge=0, le=100)
    impact_score: int = Field(ge=0, le=100)
    urgency_level: UrgencyLevel
    risk_level: RiskLevel
    affected_population_estimate: str = Field(min_length=1, max_length=512)
    public_safety_risk: str = Field(min_length=1, max_length=2000)
    infrastructure_criticality: str = Field(min_length=1, max_length=2000)
    environmental_impact: str = Field(min_length=1, max_length=2000)
    economic_impact: str = Field(min_length=1, max_length=2000)
    suggested_department: str = Field(min_length=1, max_length=256)
    recommended_action: str = Field(min_length=1, max_length=3000)
    estimated_resolution_time: str = Field(min_length=1, max_length=256)
    estimated_budget_range: str = Field(min_length=1, max_length=256)
    reasoning: str = Field(min_length=20, max_length=5000)
    confidence_score: float = Field(ge=0.0, le=1.0)
    contributing_factors: list[str] = Field(min_length=1, max_length=20)
    expected_impact: str = Field(min_length=1, max_length=2000)
    estimated_beneficiaries: str = Field(min_length=1, max_length=512)
    why_priority_ranked_high: str = Field(min_length=10, max_length=2000)

    @field_validator("urgency_level", "risk_level", mode="before")
    @classmethod
    def validate_levels(cls, value: str) -> str:
        return _normalize_level(str(value))

    @field_validator("contributing_factors", mode="before")
    @classmethod
    def validate_factors(cls, value: list | None) -> list[str]:
        if not value:
            return ["Cluster size and severity"]
        return [str(item).strip() for item in value if str(item).strip()]
