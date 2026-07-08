"""Strict JSON schema for Gemini Vision civic image analysis output."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field, field_validator

SUPPORTED_CIVIC_ISSUE_TYPES: tuple[str, ...] = (
    "Pothole",
    "Broken Road",
    "Garbage Dump",
    "Overflowing Garbage Bin",
    "Water Leakage",
    "Sewage Leakage",
    "Broken Streetlight",
    "Damaged Footpath",
    "Illegal Dumping",
    "Air Pollution",
    "Smoke",
    "Open Drain",
    "Encroachment",
    "Fallen Tree",
    "Public Property Damage",
    "Construction Debris",
    "Unknown",
)

SeverityLevel = Literal["Low", "Medium", "High", "Critical"]
IssueType = Literal[
    "Pothole",
    "Broken Road",
    "Garbage Dump",
    "Overflowing Garbage Bin",
    "Water Leakage",
    "Sewage Leakage",
    "Broken Streetlight",
    "Damaged Footpath",
    "Illegal Dumping",
    "Air Pollution",
    "Smoke",
    "Open Drain",
    "Encroachment",
    "Fallen Tree",
    "Public Property Damage",
    "Construction Debris",
    "Unknown",
]


def _normalize_issue_type(value: str) -> str:
    cleaned = value.strip()
    if not cleaned:
        return "Unknown"
    for issue in SUPPORTED_CIVIC_ISSUE_TYPES:
        if issue.lower() == cleaned.lower():
            return issue
    return "Unknown"


def _normalize_severity(value: str) -> str:
    cleaned = value.strip().lower()
    mapping = {
        "low": "Low",
        "medium": "Medium",
        "high": "High",
        "critical": "Critical",
    }
    return mapping.get(cleaned, "Medium")


class GeminiImageAnalysisOutput(BaseModel):
    """Validated Gemini Vision JSON response for civic image intelligence."""

    primary_issue: IssueType
    secondary_issue: IssueType | None = None
    description: str = Field(min_length=10, max_length=3000)
    severity: SeverityLevel
    confidence_score: float = Field(ge=0.0, le=1.0)
    visible_damage: str = Field(min_length=1, max_length=2000)
    estimated_area_affected: str = Field(min_length=1, max_length=512)
    safety_risk: str = Field(min_length=1, max_length=2000)
    suggested_department: str = Field(min_length=1, max_length=256)
    suggested_immediate_action: str = Field(min_length=1, max_length=2000)
    suggested_long_term_action: str = Field(min_length=1, max_length=2000)
    possible_public_impact: str = Field(min_length=1, max_length=2000)
    duplicate_indicators: list[str] = Field(default_factory=list, max_length=20)
    detected_objects: list[str] = Field(min_length=1, max_length=50)
    environmental_risk: str = Field(min_length=1, max_length=2000)
    road_safety_risk: str = Field(min_length=1, max_length=2000)
    human_presence: bool
    vehicles_present: bool
    requires_urgent_attention: bool
    reasoning: str = Field(min_length=10, max_length=3000)

    @field_validator("primary_issue", mode="before")
    @classmethod
    def validate_primary_issue(cls, value: str) -> str:
        return _normalize_issue_type(str(value))

    @field_validator("secondary_issue", mode="before")
    @classmethod
    def validate_secondary_issue(cls, value: str | None) -> str | None:
        if value is None or not str(value).strip():
            return None
        return _normalize_issue_type(str(value))

    @field_validator("severity", mode="before")
    @classmethod
    def validate_severity(cls, value: str) -> str:
        return _normalize_severity(str(value))

    @field_validator("duplicate_indicators", "detected_objects", mode="before")
    @classmethod
    def ensure_string_lists(cls, value: list | None) -> list[str]:
        if not value:
            return []
        return [str(item).strip() for item in value if str(item).strip()]
