"""Village Firestore repository."""

from __future__ import annotations

from typing import Any

from google.cloud.firestore_v1.base_query import FieldFilter

from app.db.collections import CollectionNames
from app.db.converters import model_to_firestore
from app.models.domain.village import (
    VillageCreate,
    VillageResponse,
    VillageSearchFilters,
    VillageUpdate,
)
from app.repositories.base import BaseRepository


class VillageRepository(
    BaseRepository[VillageCreate, VillageUpdate, VillageResponse, VillageSearchFilters]
):
    """Repository for the villages collection."""

    collection_name = CollectionNames.VILLAGES
    response_model = VillageResponse

    def _prepare_create_payload(self, data: VillageCreate) -> dict[str, Any]:
        payload = model_to_firestore(data, exclude={"metadata"})
        payload["metadata"] = self._build_metadata_for_create(
            data.metadata.created_by,
            data.metadata.updated_by,
        )
        payload["complaint_count"] = 0
        payload["open_complaint_count"] = 0
        return payload

    def _prepare_update_payload(
        self,
        existing: VillageResponse,
        data: VillageUpdate,
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

    def _apply_filters(self, query: Any, filters: VillageSearchFilters) -> Any:
        if filters.constituency:
            query = query.where(
                filter=FieldFilter("constituency", "==", filters.constituency)
            )
        if filters.district:
            query = query.where(filter=FieldFilter("district", "==", filters.district))
        if filters.state:
            query = query.where(filter=FieldFilter("state", "==", filters.state))
        if filters.block:
            query = query.where(filter=FieldFilter("block", "==", filters.block))
        if filters.is_active is not None:
            query = query.where(filter=FieldFilter("is_active", "==", filters.is_active))
        if filters.name_prefix:
            end = filters.name_prefix[:-1] + chr(ord(filters.name_prefix[-1]) + 1)
            query = query.where(
                filter=FieldFilter("name", ">=", filters.name_prefix)
            ).where(filter=FieldFilter("name", "<", end))
        return query

    def _primary_search_field(self) -> str | None:
        return "name"

    def _matches_search_text(self, item: VillageResponse, query_text: str) -> bool:
        lowered = query_text.lower()
        return (
            lowered in item.name.lower()
            or lowered in item.constituency.lower()
            or lowered in item.district.lower()
            or (item.block is not None and lowered in item.block.lower())
        )
