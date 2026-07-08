"""Strict JSON schema for Gemini complaint analysis responses."""

from pydantic import BaseModel, Field, field_validator


class GeminiComplaintAnalysisOutput(BaseModel):
    """Validated structured output expected from Gemini."""

    category: str = Field(min_length=2, max_length=128)
    sub_category: str = Field(min_length=2, max_length=128)
    responsible_department: str = Field(min_length=2, max_length=256)
    urgency: str = Field(min_length=3, max_length=32)
    severity: str = Field(min_length=3, max_length=32)
    priority_level: str = Field(min_length=3, max_length=32)
    summary: str = Field(min_length=10, max_length=2000)
    detailed_explanation: str = Field(min_length=20, max_length=5000)
    keywords: list[str] = Field(min_length=1, max_length=20)
    affected_infrastructure: str = Field(min_length=3, max_length=1000)
    affected_citizens_estimate: str | None = Field(default=None, max_length=256)
    government_scheme: str | None = Field(default=None, max_length=512)
    suggested_immediate_action: str = Field(min_length=10, max_length=2000)
    suggested_long_term_action: str = Field(min_length=10, max_length=2000)
    required_department: str = Field(min_length=2, max_length=256)
    required_team: str = Field(min_length=2, max_length=256)
    confidence_score: float = Field(ge=0, le=1)
    reasoning: str = Field(min_length=20, max_length=3000)
    duplicate_possibility: float = Field(ge=0, le=1)
    tags: list[str] = Field(default_factory=list, max_length=15)
    language_detected: str = Field(min_length=2, max_length=32)
    translated_english: str | None = Field(default=None, max_length=5000)
    voice_transcript: str | None = Field(default=None, max_length=5000)
    sentiment: str = Field(default="neutral", max_length=32)

    @field_validator("keywords", "tags")
    @classmethod
    def normalize_string_lists(cls, value: list[str]) -> list[str]:
        cleaned = [item.strip() for item in value if item and item.strip()]
        if not cleaned and cls.__name__ == "GeminiComplaintAnalysisOutput":
            return cleaned
        return cleaned

    @field_validator("urgency", "severity", "priority_level", "sentiment")
    @classmethod
    def normalize_level(cls, value: str) -> str:
        return value.strip().lower()
