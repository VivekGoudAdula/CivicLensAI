"""Analytics Firestore repository."""

from __future__ import annotations

from typing import Any

from google.cloud import firestore
from google.cloud.firestore_v1.base_query import FieldFilter

from app.db.collections import CollectionNames
from app.db.converters import model_to_firestore
from app.models.domain.analytics import (
    AnalyticsCreate,
    AnalyticsResponse,
    AnalyticsSearchFilters,
    AnalyticsUpdate,
)
from app.repositories.base import BaseRepository


class AnalyticsRepository(
    BaseRepository[
        AnalyticsCreate,
        AnalyticsUpdate,
        AnalyticsResponse,
        AnalyticsSearchFilters,
    ]
):
    """Repository for the analytics collection."""

    collection_name = CollectionNames.ANALYTICS
    response_model = AnalyticsResponse

    def _prepare_create_payload(self, data: AnalyticsCreate) -> dict[str, Any]:
        payload = model_to_firestore(data, exclude={"metadata"})
        payload["generated_at"] = self._utc_now()
        payload["metadata"] = self._build_metadata_for_create(
            data.metadata.created_by,
            data.metadata.updated_by,
        )
        return payload

    def _prepare_update_payload(
        self,
        existing: AnalyticsResponse,
        data: AnalyticsUpdate,
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

    def _apply_filters(self, query: Any, filters: AnalyticsSearchFilters) -> Any:
        if filters.report_type:
            query = query.where(
                filter=FieldFilter(
                    "report_type",
                    "==",
                    self._enum_value(filters.report_type),
                )
            )
        if filters.constituency:
            query = query.where(
                filter=FieldFilter("constituency", "==", filters.constituency)
            )
        if filters.district:
            query = query.where(filter=FieldFilter("district", "==", filters.district))
        if filters.state:
            query = query.where(filter=FieldFilter("state", "==", filters.state))
        if filters.department_id:
            query = query.where(
                filter=FieldFilter("department_id", "==", filters.department_id)
            )
        if filters.village_id:
            query = query.where(filter=FieldFilter("village_id", "==", filters.village_id))
        if filters.period_start_after:
            query = query.where(
                filter=FieldFilter("period_start", ">=", filters.period_start_after)
            )
        if filters.period_end_before:
            query = query.where(
                filter=FieldFilter("period_end", "<=", filters.period_end_before)
            )
        return query

    def _primary_search_field(self) -> str | None:
        return None

    def _matches_search_text(self, item: AnalyticsResponse, query_text: str) -> bool:
        lowered = query_text.lower()
        return (
            lowered in item.constituency.lower()
            or (item.district is not None and lowered in item.district.lower())
            or lowered in item.report_type.value.lower()
        )

    def get_latest_constituency_snapshot(
        self,
        constituency: str,
    ) -> AnalyticsResponse | None:
        """Retrieve the most recent constituency snapshot report."""
        snapshots = list(
            self.collection.where(filter=FieldFilter("constituency", "==", constituency))
            .where(filter=FieldFilter("report_type", "==", "constituency_snapshot"))
            .order_by("generated_at", direction=firestore.Query.DESCENDING)
            .limit(1)
            .stream()
        )
        if not snapshots:
            return None
        return self._to_response(snapshots[0])
