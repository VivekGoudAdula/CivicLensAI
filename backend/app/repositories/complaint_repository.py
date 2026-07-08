"""Complaint Firestore repository."""

from __future__ import annotations

from typing import Any

from google.cloud.firestore_v1.base_query import FieldFilter

from app.db.collections import CollectionNames, build_document_path
from app.db.converters import model_to_firestore
from app.models.enums.common import AnalysisStatus
from app.models.domain.complaint import (
    ComplaintCreate,
    ComplaintResponse,
    ComplaintSearchFilters,
    ComplaintUpdate,
)
from app.repositories.base import BaseRepository


class ComplaintRepository(
    BaseRepository[
        ComplaintCreate,
        ComplaintUpdate,
        ComplaintResponse,
        ComplaintSearchFilters,
    ]
):
    """Repository for the complaints collection."""

    collection_name = CollectionNames.COMPLAINTS
    response_model = ComplaintResponse

    def _prepare_create_payload(self, data: ComplaintCreate) -> dict[str, Any]:
        payload = model_to_firestore(data, exclude={"metadata"})
        payload["village_ref"] = build_document_path(CollectionNames.VILLAGES, data.village_id)
        payload["status"] = self._enum_value(data.status)
        payload["cluster_id"] = None
        payload["cluster_ref"] = None
        payload["ai_analysis"] = None
        payload["analysis_status"] = self._enum_value(AnalysisStatus.PENDING)
        payload["analysis_started_at"] = None
        payload["analysis_completed_at"] = None
        payload["analysis_model_name"] = None
        payload["analysis_processing_time_ms"] = None
        payload["analysis_prompt_version"] = None
        payload["analysis_error_message"] = None
        payload["analysis_retry_count"] = 0
        payload["image_analysis"] = None
        if data.image_base64 and data.image_mime_type:
            payload["image_analysis_status"] = self._enum_value(AnalysisStatus.PENDING)
        else:
            payload["image_analysis_status"] = None
        payload["vision_model"] = None
        payload["vision_processing_time_ms"] = None
        payload["vision_completed_at"] = None
        payload["vision_started_at"] = None
        payload["vision_prompt_version"] = None
        payload["vision_error_message"] = None
        payload["vision_retry_count"] = 0
        payload["is_duplicate"] = False
        payload["duplicate_score"] = None
        payload["duplicate_reason"] = None
        payload["duplicate_confidence"] = None
        payload["matched_complaint_id"] = None
        payload["matched_cluster_id"] = None
        payload["submitted_at"] = self._utc_now()
        payload["resolved_at"] = None
        payload["metadata"] = self._build_metadata_for_create(
            data.metadata.created_by,
            data.metadata.updated_by,
        )
        return payload

    def _prepare_update_payload(
        self,
        existing: ComplaintResponse,
        data: ComplaintUpdate,
    ) -> dict[str, Any]:
        update_fields = self._merge_update_fields(
            model_to_firestore(data, exclude={"updated_by"}),
        )
        if data.cluster_id is not None:
            update_fields["cluster_ref"] = build_document_path(
                CollectionNames.CLUSTERS,
                data.cluster_id,
            )
        if not update_fields:
            return {}
        update_fields["metadata"] = self._build_metadata_for_update(
            existing.metadata,
            data.updated_by,
        )
        return update_fields

    def _apply_filters(self, query: Any, filters: ComplaintSearchFilters) -> Any:
        if filters.citizen_email:
            query = query.where(
                filter=FieldFilter("citizen_email", "==", filters.citizen_email)
            )
        if filters.constituency:
            query = query.where(
                filter=FieldFilter("constituency", "==", filters.constituency)
            )
        if filters.district:
            query = query.where(filter=FieldFilter("district", "==", filters.district))
        if filters.state:
            query = query.where(filter=FieldFilter("state", "==", filters.state))
        if filters.village_id:
            query = query.where(filter=FieldFilter("village_id", "==", filters.village_id))
        if filters.cluster_id:
            query = query.where(filter=FieldFilter("cluster_id", "==", filters.cluster_id))
        if filters.category_id:
            query = query.where(
                filter=FieldFilter("category_id", "==", filters.category_id)
            )
        if filters.category:
            query = query.where(
                filter=FieldFilter("category", "==", self._enum_value(filters.category))
            )
        if filters.status:
            query = query.where(
                filter=FieldFilter("status", "==", self._enum_value(filters.status))
            )
        if filters.priority:
            query = query.where(
                filter=FieldFilter("priority", "==", self._enum_value(filters.priority))
            )
        if filters.submitted_after:
            query = query.where(
                filter=FieldFilter("submitted_at", ">=", filters.submitted_after)
            )
        if filters.submitted_before:
            query = query.where(
                filter=FieldFilter("submitted_at", "<=", filters.submitted_before)
            )
        if filters.keyword:
            query = query.where(
                filter=FieldFilter(
                    "ai_analysis.keywords",
                    "array_contains",
                    filters.keyword.lower(),
                )
            )
        return query

    def _primary_search_field(self) -> str | None:
        return "title"

    def _matches_search_text(self, item: ComplaintResponse, query_text: str) -> bool:
        lowered = query_text.lower()
        keyword_match = (
            item.ai_analysis is not None
            and any(lowered in keyword.lower() for keyword in item.ai_analysis.keywords)
        )
        return (
            lowered in item.title.lower()
            or lowered in item.description.lower()
            or lowered in item.village_name.lower()
            or keyword_match
        )

    def list_by_village(
        self,
        village_id: str,
        pagination: Any | None = None,
    ) -> Any:
        """List complaints for a specific village."""
        return self.list(
            filters=ComplaintSearchFilters(village_id=village_id),
            pagination=pagination,
        )
