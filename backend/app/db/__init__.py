"""Firestore database utilities and helpers."""

from app.db.collections import CollectionNames, get_collection_ref, get_document_ref
from app.db.converters import FirestoreConverter, document_to_dict, model_to_firestore
from app.db.pagination import PaginatedResult, PaginationParams
from app.db.timestamps import server_timestamp, utc_now
from app.db.transactions import run_batch_write, run_transaction

__all__ = [
    "CollectionNames",
    "FirestoreConverter",
    "PaginatedResult",
    "PaginationParams",
    "document_to_dict",
    "get_collection_ref",
    "get_document_ref",
    "model_to_firestore",
    "run_batch_write",
    "run_transaction",
    "server_timestamp",
    "utc_now",
]
