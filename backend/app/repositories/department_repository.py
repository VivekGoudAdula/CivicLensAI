"""Department Firestore repository."""

from __future__ import annotations

from typing import Any

from google.cloud.firestore_v1.base_query import FieldFilter

from app.core.exceptions import ConflictError
from app.db.collections import CollectionNames
from app.db.converters import model_to_firestore
from app.models.domain.department import (
    DepartmentCreate,
    DepartmentResponse,
    DepartmentSearchFilters,
    DepartmentUpdate,
)
from app.repositories.base import BaseRepository


class DepartmentRepository(
    BaseRepository[
        DepartmentCreate,
        DepartmentUpdate,
        DepartmentResponse,
        DepartmentSearchFilters,
    ]
):
    """Repository for the departments collection."""

    collection_name = CollectionNames.DEPARTMENTS
    response_model = DepartmentResponse

    def _prepare_create_payload(self, data: DepartmentCreate) -> dict[str, Any]:
        existing = self.get_by_code(data.code)
        if existing:
            raise ConflictError(f"Department with code '{data.code}' already exists")

        payload = model_to_firestore(data, exclude={"metadata"})
        payload["metadata"] = self._build_metadata_for_create(
            data.metadata.created_by,
            data.metadata.updated_by,
        )
        payload["assigned_recommendation_count"] = 0
        payload["active_recommendation_count"] = 0
        return payload

    def _prepare_update_payload(
        self,
        existing: DepartmentResponse,
        data: DepartmentUpdate,
    ) -> dict[str, Any]:
        update_fields = self._merge_update_fields(
            model_to_firestore(data, exclude={"updated_by"}),
        )
        if not update_fields:
            return {}
        update_fields["metadata"] = self._build_metadata_for_update(
            existing.metadata,
            data.updated_by,
        )
        return update_fields

    def get_by_code(self, code: str) -> DepartmentResponse | None:
        """Retrieve a department by its unique code."""
        snapshots = list(
            self.collection.where(filter=FieldFilter("code", "==", code.upper()))
            .limit(1)
            .stream()
        )
        if not snapshots:
            return None
        return self._to_response(snapshots[0])

    def _apply_filters(self, query: Any, filters: DepartmentSearchFilters) -> Any:
        if filters.category:
            query = query.where(
                filter=FieldFilter("category", "==", self._enum_value(filters.category))
            )
        if filters.constituency:
            query = query.where(
                filter=FieldFilter("constituency", "==", filters.constituency)
            )
        if filters.is_active is not None:
            query = query.where(filter=FieldFilter("is_active", "==", filters.is_active))
        if filters.code:
            query = query.where(filter=FieldFilter("code", "==", filters.code.upper()))
        if filters.name_prefix:
            end = filters.name_prefix[:-1] + chr(ord(filters.name_prefix[-1]) + 1)
            query = query.where(
                filter=FieldFilter("name", ">=", filters.name_prefix)
            ).where(filter=FieldFilter("name", "<", end))
        return query

    def _primary_search_field(self) -> str | None:
        return "name"

    def _matches_search_text(self, item: DepartmentResponse, query_text: str) -> bool:
        lowered = query_text.lower()
        return (
            lowered in item.name.lower()
            or lowered in item.code.lower()
            or (item.description is not None and lowered in item.description.lower())
        )
