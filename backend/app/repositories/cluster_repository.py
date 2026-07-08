"""Cluster Firestore repository."""

from __future__ import annotations

from typing import Any

from google.cloud.firestore_v1.base_query import FieldFilter

from app.db.collections import CollectionNames, build_document_path
from app.db.converters import model_to_firestore
from app.models.domain.cluster import (
    ClusterCreate,
    ClusterResponse,
    ClusterSearchFilters,
    ClusterUpdate,
)
from app.db.pagination import PaginatedResult, PaginationParams
from app.repositories.base import BaseRepository


class ClusterRepository(
    BaseRepository[ClusterCreate, ClusterUpdate, ClusterResponse, ClusterSearchFilters]
):
    """Repository for the clusters collection."""

    collection_name = CollectionNames.CLUSTERS
    response_model = ClusterResponse

    def _prepare_create_payload(self, data: ClusterCreate) -> dict[str, Any]:
        payload = model_to_firestore(data, exclude={"metadata"})
        payload["status"] = "open"
        payload["complaint_refs"] = [
            build_document_path(CollectionNames.COMPLAINTS, complaint_id)
            for complaint_id in data.complaint_ids
        ]
        payload["complaint_count"] = len(data.complaint_ids)
        payload["village_names"] = []
        payload["village_name"] = None
        payload["department"] = None
        payload["coordinates"] = None
        payload["representative_complaint_id"] = None
        payload["average_severity"] = None
        payload["latest_complaint_date"] = None
        payload["average_confidence"] = None
        payload["affected_area"] = None
        payload["priority_score"] = 0.5
        payload["hotspot_score"] = 0.0
        payload["priority_analysis"] = None
        payload["impact_score"] = None
        payload["urgency_level"] = None
        payload["priority_rank"] = None
        payload["recommended_department"] = None
        payload["recommended_action"] = None
        payload["estimated_budget"] = None
        payload["estimated_resolution_time"] = None
        payload["affected_population"] = None
        payload["priority_reasoning"] = None
        payload["priority_confidence"] = None
        payload["priority_updated_at"] = None
        payload["priority_analysis_hash"] = None
        payload["ai_insights"] = None
        payload["recommendation_ids"] = []
        payload["metadata"] = self._build_metadata_for_create(
            data.metadata.created_by,
            data.metadata.updated_by,
        )
        return payload

    def _prepare_update_payload(
        self,
        existing: ClusterResponse,
        data: ClusterUpdate,
    ) -> dict[str, Any]:
        update_fields = self._merge_update_fields(
            model_to_firestore(data, exclude={"updated_by"}),
        )
        if data.complaint_ids is not None:
            update_fields["complaint_refs"] = [
                build_document_path(CollectionNames.COMPLAINTS, complaint_id)
                for complaint_id in data.complaint_ids
            ]
            update_fields["complaint_count"] = len(data.complaint_ids)
        if not update_fields:
            return {}
        update_fields["metadata"] = self._build_metadata_for_update(
            existing.metadata,
            data.updated_by,
        )
        return update_fields

    def _apply_filters(self, query: Any, filters: ClusterSearchFilters) -> Any:
        if filters.constituency:
            query = query.where(
                filter=FieldFilter("constituency", "==", filters.constituency)
            )
        if filters.district:
            query = query.where(filter=FieldFilter("district", "==", filters.district))
        if filters.state:
            query = query.where(filter=FieldFilter("state", "==", filters.state))
        if filters.village_id:
            query = query.where(
                filter=FieldFilter("village_ids", "array_contains", filters.village_id)
            )
        if filters.category:
            query = query.where(
                filter=FieldFilter("category", "==", self._enum_value(filters.category))
            )
        if filters.status:
            query = query.where(
                filter=FieldFilter("status", "==", self._enum_value(filters.status))
            )
        if filters.min_complaint_count is not None:
            query = query.where(
                filter=FieldFilter(
                    "complaint_count",
                    ">=",
                    filters.min_complaint_count,
                )
            )
        if filters.theme_prefix:
            end = filters.theme_prefix[:-1] + chr(ord(filters.theme_prefix[-1]) + 1)
            query = query.where(
                filter=FieldFilter("theme", ">=", filters.theme_prefix)
            ).where(filter=FieldFilter("theme", "<", end))
        return query

    def _primary_search_field(self) -> str | None:
        return "title"

    def _matches_search_text(self, item: ClusterResponse, query_text: str) -> bool:
        lowered = query_text.lower()
        theme_match = (
            item.ai_insights is not None
            and any(
                lowered in theme.lower() for theme in item.ai_insights.key_themes
            )
        )
        return (
            lowered in item.title.lower()
            or lowered in item.description.lower()
            or lowered in item.theme.lower()
            or theme_match
        )

    def list_by_complaint(
        self,
        complaint_id: str,
        pagination: PaginationParams | None = None,
    ) -> PaginatedResult[ClusterResponse]:
        """List clusters containing a specific complaint."""
        from google.cloud import firestore

        from app.db.pagination import PaginatedResult, PaginationParams

        pagination_params = pagination or PaginationParams()
        query = self.collection.where(
            filter=FieldFilter("complaint_ids", "array_contains", complaint_id)
        )
        direction = (
            firestore.Query.ASCENDING
            if pagination_params.order_direction == "asc"
            else firestore.Query.DESCENDING
        )
        query = query.order_by(pagination_params.order_by, direction=direction)
        query = query.limit(pagination_params.limit + 1)
        snapshots = list(query.stream())
        has_more = len(snapshots) > pagination_params.limit
        page_snapshots = snapshots[: pagination_params.limit]
        items = [self._to_response(snapshot) for snapshot in page_snapshots]
        return PaginatedResult(
            items=items,
            limit=pagination_params.limit,
            has_more=has_more,
            next_cursor=page_snapshots[-1].id if has_more and page_snapshots else None,
        )
