"""Strict JSON schema for Gemini duplicate matching output."""

from __future__ import annotations

from pydantic import BaseModel, Field, field_validator


class GeminiDuplicateMatchOutput(BaseModel):
    """Validated Gemini duplicate detection response."""

    is_duplicate: bool
    similarity_score: int = Field(ge=0, le=100)
    matching_reason: str = Field(min_length=5, max_length=2000)
    existing_cluster_id: str | None = Field(default=None, max_length=128)
    matched_complaint_id: str | None = Field(default=None, max_length=128)
    confidence: float = Field(ge=0.0, le=1.0)
    explanation: str = Field(min_length=10, max_length=3000)

    @field_validator("existing_cluster_id", "matched_complaint_id", mode="before")
    @classmethod
    def normalize_optional_ids(cls, value: str | None) -> str | None:
        if value is None:
            return None
        cleaned = str(value).strip()
        if not cleaned or cleaned.lower() in {"null", "none", "n/a"}:
            return None
        return cleaned
