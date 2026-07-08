"""Category Firestore repository."""

from __future__ import annotations

from typing import Any

from google.cloud import firestore
from google.cloud.firestore_v1.base_query import FieldFilter

from app.db.collections import CollectionNames
from app.db.converters import model_to_firestore
from app.db.pagination import PaginatedResult, PaginationParams
from app.models.domain.category import (
    CategoryCreate,
    CategoryResponse,
    CategoryUpdate,
)
from app.repositories.base import BaseRepository


class CategorySearchFilters:
  pass


class CategoryRepository(
    BaseRepository[CategoryCreate, CategoryUpdate, CategoryResponse, CategorySearchFilters]
):
    """Repository for the categories collection."""

    collection_name = CollectionNames.CATEGORIES
    response_model = CategoryResponse

    def _prepare_create_payload(self, data: CategoryCreate) -> dict[str, Any]:
        payload = model_to_firestore(data, exclude={"metadata"})
        payload["metadata"] = self._build_metadata_for_create(
            data.metadata.created_by,
            data.metadata.updated_by,
        )
        return payload

    def _prepare_update_payload(
        self,
        existing: CategoryResponse,
        data: CategoryUpdate,
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

    def _apply_filters(self, query: Any, filters: CategorySearchFilters) -> Any:
        return query

    def _matches_search_text(self, item: CategoryResponse, query_text: str) -> bool:
        lowered = query_text.lower()
        return lowered in item.name.lower() or lowered in item.slug.lower()

    def list_active(self) -> list[CategoryResponse]:
        """Return all active categories ordered by display_order."""
        snapshots = list(
            self.collection.where(filter=FieldFilter("is_active", "==", True))
            .order_by("display_order")
            .stream()
        )
        return [self._to_response(snapshot) for snapshot in snapshots]

    def get_by_slug(self, slug: str) -> CategoryResponse | None:
        """Retrieve a category by slug."""
        snapshots = list(
            self.collection.where(filter=FieldFilter("slug", "==", slug))
            .limit(1)
            .stream()
        )
        if not snapshots:
            return None
        return self._to_response(snapshots[0])
