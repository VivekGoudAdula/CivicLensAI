"""Firestore collection name constants and reference helpers."""

from __future__ import annotations

from enum import StrEnum
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from google.cloud.firestore_v1 import Client as FirestoreClient
    from google.cloud.firestore_v1 import CollectionReference, DocumentReference


class CollectionNames(StrEnum):
    """Canonical Firestore collection identifiers."""

    VILLAGES = "villages"
    DEPARTMENTS = "departments"
    COMPLAINTS = "complaints"
    CLUSTERS = "clusters"
    RECOMMENDATIONS = "recommendations"
    ANALYTICS = "analytics"
    CATEGORIES = "categories"
    USERS = "users"


def get_collection_ref(
    db: FirestoreClient,
    collection: CollectionNames | str,
) -> CollectionReference:
    """Return a typed collection reference."""
    name = collection.value if isinstance(collection, CollectionNames) else collection
    return db.collection(name)


def get_document_ref(
    db: FirestoreClient,
    collection: CollectionNames | str,
    document_id: str,
) -> DocumentReference:
    """Return a typed document reference."""
    return get_collection_ref(db, collection).document(document_id)


def build_document_path(collection: CollectionNames | str, document_id: str) -> str:
    """Build a Firestore document path string."""
    name = collection.value if isinstance(collection, CollectionNames) else collection
    return f"{name}/{document_id}"


def parse_document_path(path: str) -> tuple[str, str]:
    """Parse a document path into collection name and document ID."""
    parts = path.split("/", 1)
    if len(parts) != 2 or not parts[0] or not parts[1]:
        raise ValueError(f"Invalid Firestore document path: {path}")
    return parts[0], parts[1]
