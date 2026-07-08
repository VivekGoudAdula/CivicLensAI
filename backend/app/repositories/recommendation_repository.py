"""Recommendation Firestore repository."""

from __future__ import annotations

from typing import Any

from google.cloud.firestore_v1.base_query import FieldFilter

from app.db.collections import CollectionNames, build_document_path
from app.db.converters import model_to_firestore
from app.models.domain.recommendation import (
    RecommendationCreate,
    RecommendationResponse,
    RecommendationSearchFilters,
    RecommendationUpdate,
)
from app.repositories.base import BaseRepository


class RecommendationRepository(
    BaseRepository[
        RecommendationCreate,
        RecommendationUpdate,
        RecommendationResponse,
        RecommendationSearchFilters,
    ]
):
    """Repository for the recommendations collection."""

    collection_name = CollectionNames.RECOMMENDATIONS
    response_model = RecommendationResponse

    def _prepare_create_payload(self, data: RecommendationCreate) -> dict[str, Any]:
        payload = model_to_firestore(data, exclude={"metadata"})
        payload["status"] = "draft"
        payload["department_ref"] = build_document_path(
            CollectionNames.DEPARTMENTS,
            data.department_id,
        )
        payload["cluster_refs"] = [
            build_document_path(CollectionNames.CLUSTERS, cluster_id)
            for cluster_id in data.cluster_ids
        ]
        payload["completed_at"] = None
        payload["metadata"] = self._build_metadata_for_create(
            data.metadata.created_by,
            data.metadata.updated_by,
        )
        return payload

    def _prepare_update_payload(
        self,
        existing: RecommendationResponse,
        data: RecommendationUpdate,
    ) -> dict[str, Any]:
        update_fields = self._merge_update_fields(
            model_to_firestore(data, exclude={"updated_by"}),
        )
        if data.cluster_ids is not None:
            update_fields["cluster_refs"] = [
                build_document_path(CollectionNames.CLUSTERS, cluster_id)
                for cluster_id in data.cluster_ids
            ]
        if data.department_id is not None:
            update_fields["department_ref"] = build_document_path(
                CollectionNames.DEPARTMENTS,
                data.department_id,
            )
        if not update_fields:
            return {}
        update_fields["metadata"] = self._build_metadata_for_update(
            existing.metadata,
            data.updated_by,
        )
        return update_fields

    def _apply_filters(self, query: Any, filters: RecommendationSearchFilters) -> Any:
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
        if filters.cluster_id:
            query = query.where(
                filter=FieldFilter("cluster_ids", "array_contains", filters.cluster_id)
            )
        if filters.village_id:
            query = query.where(
                filter=FieldFilter("village_ids", "array_contains", filters.village_id)
            )
        if filters.status:
            query = query.where(
                filter=FieldFilter("status", "==", self._enum_value(filters.status))
            )
        if filters.priority:
            query = query.where(
                filter=FieldFilter("priority", "==", self._enum_value(filters.priority))
            )
        if filters.due_after:
            query = query.where(filter=FieldFilter("due_date", ">=", filters.due_after))
        if filters.due_before:
            query = query.where(filter=FieldFilter("due_date", "<=", filters.due_before))
        return query

    def _primary_search_field(self) -> str | None:
        return "title"

    def _matches_search_text(self, item: RecommendationResponse, query_text: str) -> bool:
        lowered = query_text.lower()
        action_match = (
            item.ai_recommendation is not None
            and any(
                lowered in action.lower()
                for action in item.ai_recommendation.action_items
            )
        )
        return (
            lowered in item.title.lower()
            or lowered in item.description.lower()
            or lowered in item.department_name.lower()
            or action_match
        )

    def list_by_department(
        self,
        department_id: str,
        filters: RecommendationSearchFilters | None = None,
        pagination: Any | None = None,
    ) -> Any:
        """List recommendations assigned to a department."""
        combined_filters = filters or RecommendationSearchFilters()
        combined_filters.department_id = department_id
        return self.list(filters=combined_filters, pagination=pagination)
