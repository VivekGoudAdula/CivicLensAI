"""Pagination models for repository list operations."""

from __future__ import annotations

from typing import Generic, TypeVar

from pydantic import BaseModel, Field

T = TypeVar("T")


class PaginationParams(BaseModel):
    """Cursor-based pagination parameters."""

    limit: int = Field(default=20, ge=1, le=1000)
    cursor: str | None = Field(
        default=None,
        description="Document ID to start after for cursor pagination",
    )
    order_by: str = Field(default="metadata.created_at")
    order_direction: str = Field(default="desc", pattern="^(asc|desc)$")


class PaginatedResult(BaseModel, Generic[T]):
    """Paginated repository response."""

    items: list[T]
    total_count: int | None = None
    limit: int
    has_more: bool = False
    next_cursor: str | None = None
