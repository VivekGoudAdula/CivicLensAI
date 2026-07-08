"""Global search API schemas."""

from __future__ import annotations

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field

SearchEntityType = Literal["complaint", "cluster", "recommendation"]
SearchSortOption = Literal[
    "newest",
    "oldest",
    "highest_priority",
    "highest_severity",
    "most_complaints",
    "alphabetical",
]


class GlobalSearchFilters(BaseModel):
    category: str | None = None
    department: str | None = None
    village: str | None = None
    priority: str | None = None
    severity: str | None = None
    status: str | None = None
    cluster_id: str | None = None
    date_from: str | None = None
    date_to: str | None = None
    ai_confidence_min: float | None = Field(default=None, ge=0, le=1)
    recommendation_status: str | None = None
    urgency: str | None = None
    resolved: bool | None = None


class GlobalSearchResultItem(BaseModel):
    id: str
    type: SearchEntityType
    title: str
    subtitle: str
    description: str
    category: str | None = None
    department: str | None = None
    village: str | None = None
    priority: str | None = None
    severity: str | None = None
    status: str | None = None
    score: float = 0.0
    highlight: str | None = None
    url_path: str
    occurred_at: datetime | None = None


class GlobalSearchResponse(BaseModel):
    success: bool = True
    query: str
    items: list[GlobalSearchResultItem]
    total: int
    suggestions: list[str] = Field(default_factory=list)
    took_ms: int
