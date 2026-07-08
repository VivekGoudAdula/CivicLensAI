"""Pydantic model ↔ Firestore document conversion utilities."""

from __future__ import annotations

from datetime import UTC, datetime
from enum import Enum
from typing import Any, Generic, TypeVar

from google.cloud.firestore_v1._helpers import DatetimeWithNanoseconds
from pydantic import BaseModel

T = TypeVar("T", bound=BaseModel)


def _serialize_value(value: Any) -> Any:
    if value is None:
        return None
    if isinstance(value, Enum):
        return value.value
    if isinstance(value, datetime):
        return value.astimezone(UTC) if value.tzinfo else value.replace(tzinfo=UTC)
    if isinstance(value, BaseModel):
        return model_to_firestore(value)
    if isinstance(value, list):
        return [_serialize_value(item) for item in value]
    if isinstance(value, dict):
        return {key: _serialize_value(item) for key, item in value.items()}
    return value


def model_to_firestore(
    model: BaseModel,
    *,
    exclude_none: bool = True,
    exclude: set[str] | None = None,
) -> dict[str, Any]:
    """Convert a Pydantic model to a Firestore-compatible dictionary."""
    data = model.model_dump(exclude_none=exclude_none, exclude=exclude)
    return {key: _serialize_value(value) for key, value in data.items()}


def _deserialize_value(value: Any) -> Any:
    if isinstance(value, DatetimeWithNanoseconds):
        return value.replace(tzinfo=UTC)
    if isinstance(value, datetime) and value.tzinfo is None:
        return value.replace(tzinfo=UTC)
    if isinstance(value, dict):
        return {key: _deserialize_value(item) for key, item in value.items()}
    if isinstance(value, list):
        return [_deserialize_value(item) for item in value]
    return value


def document_to_dict(data: dict[str, Any] | None) -> dict[str, Any]:
    """Normalize a Firestore document dictionary for Pydantic parsing."""
    if not data:
        return {}
    return {key: _deserialize_value(value) for key, value in data.items()}


class FirestoreConverter(Generic[T]):
    """Generic converter between Pydantic models and Firestore documents."""

    def __init__(self, model_class: type[T]):
        self.model_class = model_class

    def to_firestore(
        self,
        model: BaseModel,
        *,
        exclude_none: bool = True,
        exclude: set[str] | None = None,
    ) -> dict[str, Any]:
        return model_to_firestore(model, exclude_none=exclude_none, exclude=exclude)

    def from_firestore(self, data: dict[str, Any] | None, document_id: str) -> T:
        normalized = document_to_dict(data)
        normalized["id"] = document_id
        return self.model_class.model_validate(normalized)
