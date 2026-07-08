"""Base Firestore repository with CRUD, list, search, and pagination."""

from __future__ import annotations

import logging
import uuid
from abc import ABC, abstractmethod
from datetime import UTC, datetime
from typing import Any, Generic, TypeVar

from google.cloud import firestore
from google.cloud.firestore_v1 import Client as FirestoreClient
from google.cloud.firestore_v1.base_query import FieldFilter
from pydantic import BaseModel

from app.core.exceptions import NotFoundError
from app.db.collections import CollectionNames, build_document_path, get_collection_ref
from app.db.converters import FirestoreConverter, document_to_dict
from app.db.pagination import PaginatedResult, PaginationParams
from app.models.schemas.common import DocumentMetadata

logger = logging.getLogger(__name__)

TCreate = TypeVar("TCreate", bound=BaseModel)
TUpdate = TypeVar("TUpdate", bound=BaseModel)
TResponse = TypeVar("TResponse", bound=BaseModel)
TFilters = TypeVar("TFilters", bound=BaseModel)


class BaseRepository(ABC, Generic[TCreate, TUpdate, TResponse, TFilters]):
    """Abstract base repository for Firestore collections."""

    collection_name: CollectionNames
    response_model: type[TResponse]

    def __init__(self, db: FirestoreClient):
        self.db = db
        self.collection = get_collection_ref(db, self.collection_name)
        self.converter = FirestoreConverter(self.response_model)

    def _generate_id(self) -> str:
        return uuid.uuid4().hex

    def _build_metadata_for_create(self, created_by: str, updated_by: str) -> dict[str, Any]:
        return {
            "created_at": firestore.SERVER_TIMESTAMP,
            "updated_at": firestore.SERVER_TIMESTAMP,
            "created_by": created_by,
            "updated_by": updated_by,
            "version": 1,
        }

    def _build_metadata_for_update(
        self,
        existing: DocumentMetadata,
        updated_by: str,
    ) -> dict[str, Any]:
        return {
            "created_at": existing.created_at,
            "updated_at": firestore.SERVER_TIMESTAMP,
            "created_by": existing.created_by,
            "updated_by": updated_by,
            "version": existing.version + 1,
        }

    def _to_response(self, snapshot: firestore.DocumentSnapshot) -> TResponse:
        return self.converter.from_firestore(snapshot.to_dict(), snapshot.id)

    def create(self, data: TCreate, *, document_id: str | None = None) -> TResponse:
        """Create a new document in the collection."""
        doc_id = document_id or self._generate_id()
        doc_ref = self.collection.document(doc_id)
        payload = self._prepare_create_payload(data)
        doc_ref.set(payload)
        snapshot = doc_ref.get()
        if not snapshot.exists:
            raise NotFoundError(f"Failed to create document in {self.collection_name.value}")
        logger.info("Created %s/%s", self.collection_name.value, doc_id)
        return self._to_response(snapshot)

    @abstractmethod
    def _prepare_create_payload(self, data: TCreate) -> dict[str, Any]:
        """Transform create model into Firestore payload."""

    def get_by_id(self, document_id: str) -> TResponse | None:
        """Retrieve a document by ID."""
        snapshot = self.collection.document(document_id).get()
        if not snapshot.exists:
            return None
        return self._to_response(snapshot)

    def get_by_id_or_raise(self, document_id: str) -> TResponse:
        """Retrieve a document by ID or raise NotFoundError."""
        result = self.get_by_id(document_id)
        if result is None:
            raise NotFoundError(
                f"{self.collection_name.value} document '{document_id}' not found"
            )
        return result

    def update(self, document_id: str, data: TUpdate) -> TResponse:
        """Update an existing document."""
        doc_ref = self.collection.document(document_id)
        snapshot = doc_ref.get()
        if not snapshot.exists:
            raise NotFoundError(
                f"{self.collection_name.value} document '{document_id}' not found"
            )

        existing = self._to_response(snapshot)
        update_payload = self._prepare_update_payload(existing, data)
        if not update_payload:
            return existing

        doc_ref.update(update_payload)
        updated_snapshot = doc_ref.get()
        logger.info("Updated %s/%s", self.collection_name.value, document_id)
        return self._to_response(updated_snapshot)

    @abstractmethod
    def _prepare_update_payload(self, existing: TResponse, data: TUpdate) -> dict[str, Any]:
        """Transform update model into Firestore update payload."""

    def delete(self, document_id: str) -> bool:
        """Delete a document by ID."""
        doc_ref = self.collection.document(document_id)
        snapshot = doc_ref.get()
        if not snapshot.exists:
            return False
        doc_ref.delete()
        logger.info("Deleted %s/%s", self.collection_name.value, document_id)
        return True

    def list(
        self,
        filters: TFilters | None = None,
        pagination: PaginationParams | None = None,
    ) -> PaginatedResult[TResponse]:
        """List documents with optional filters and in-memory sorting/pagination to bypass composite index limits."""
        pagination = pagination or PaginationParams()
        query = self.collection

        if filters is not None:
            query = self._apply_filters(query, filters)

        # Stream all matching documents (bypassing Firestore order_by/limit to avoid index errors)
        snapshots = list(query.stream())
        items = [self._to_response(snapshot) for snapshot in snapshots]

        # Sort in memory
        reverse = pagination.order_direction == "desc"
        def get_sort_key(item: Any) -> Any:
            val = item
            for part in pagination.order_by.split("."):
                if val is None:
                    break
                val = getattr(val, part, None)
            if val is None:
                return datetime.min if not reverse else datetime.max
            return val

        try:
            items.sort(key=get_sort_key, reverse=reverse)
        except Exception:
            logger.exception("Error sorting items in memory")

        # Paginate in memory
        total = len(items)
        start = 0
        if pagination.cursor:
            # Find matching document index to start after
            for idx, item in enumerate(items):
                if getattr(item, "id", None) == pagination.cursor:
                    start = idx + 1
                    break

        page_items = items[start : start + pagination.limit]
        has_more = (start + pagination.limit) < total
        next_cursor = page_items[-1].id if has_more and page_items else None

        return PaginatedResult(
            items=page_items,
            limit=pagination.limit,
            has_more=has_more,
            next_cursor=next_cursor,
        )

    def search(
        self,
        query_text: str,
        filters: TFilters | None = None,
        pagination: PaginationParams | None = None,
    ) -> PaginatedResult[TResponse]:
        """Search documents using text and structured filters with in-memory sorting/pagination."""
        pagination = pagination or PaginationParams()
        normalized_query = query_text.strip()

        if not normalized_query and filters is None:
            return self.list(filters=filters, pagination=pagination)

        firestore_query = self.collection
        if filters is not None:
            firestore_query = self._apply_filters(firestore_query, filters)

        firestore_query = self._apply_text_search(firestore_query, normalized_query)

        # Stream all matching search documents to prevent index exceptions
        snapshots = list(firestore_query.stream())
        items = [self._to_response(snapshot) for snapshot in snapshots]

        if normalized_query:
            items = [
                item
                for item in items
                if self._matches_search_text(item, normalized_query)
            ]

        # Sort in memory
        reverse = pagination.order_direction == "desc"
        def get_sort_key(item: Any) -> Any:
            val = item
            for part in pagination.order_by.split("."):
                if val is None:
                    break
                val = getattr(val, part, None)
            if val is None:
                return datetime.min if not reverse else datetime.max
            return val

        try:
            items.sort(key=get_sort_key, reverse=reverse)
        except Exception:
            logger.exception("Error sorting items in memory")

        # Paginate in memory
        total = len(items)
        start = 0
        if pagination.cursor:
            for idx, item in enumerate(items):
                if getattr(item, "id", None) == pagination.cursor:
                    start = idx + 1
                    break

        page_items = items[start : start + pagination.limit]
        has_more = (start + pagination.limit) < total
        next_cursor = page_items[-1].id if has_more and page_items else None

        return PaginatedResult(
            items=page_items,
            limit=pagination.limit,
            has_more=has_more,
            next_cursor=next_cursor,
        )

    @abstractmethod
    def _apply_filters(self, query: Any, filters: TFilters) -> Any:
        """Apply collection-specific filters to a Firestore query."""

    def _apply_text_search(self, query: Any, query_text: str) -> Any:
        """Apply default prefix search on the primary searchable field."""
        if not query_text:
            return query
        search_field = self._primary_search_field()
        if not search_field:
            return query
        end = query_text[:-1] + chr(ord(query_text[-1]) + 1) if query_text else query_text
        return query.where(filter=FieldFilter(search_field, ">=", query_text)).where(
            filter=FieldFilter(search_field, "<", end)
        )

    def _primary_search_field(self) -> str | None:
        """Return the default field used for prefix search."""
        return "name"

    @abstractmethod
    def _matches_search_text(self, item: TResponse, query_text: str) -> bool:
        """Client-side text matching for fields not indexed for full-text search."""

    def count(self, filters: TFilters | None = None) -> int:
        """Count documents matching optional filters."""
        query = self.collection
        if filters is not None:
            query = self._apply_filters(query, filters)

        aggregate = query.count().get()
        if aggregate and aggregate[0]:
            return int(aggregate[0][0].value)
        return 0

    def build_ref(self, document_id: str) -> str:
        """Build a document reference path for this collection."""
        return build_document_path(self.collection_name, document_id)

    @staticmethod
    def _enum_value(value: Any) -> Any:
        return value.value if hasattr(value, "value") else value

    @staticmethod
    def _merge_update_fields(
        update_data: dict[str, Any],
        *,
        exclude: set[str] | None = None,
    ) -> dict[str, Any]:
        excluded = exclude or set()
        return {
            key: value
            for key, value in update_data.items()
            if key not in excluded and value is not None
        }

    def _extract_metadata(self, snapshot_dict: dict[str, Any]) -> DocumentMetadata:
        metadata = document_to_dict(snapshot_dict).get("metadata", {})
        return DocumentMetadata.model_validate(metadata)

    @staticmethod
    def _utc_now() -> datetime:
        return datetime.now(UTC)
