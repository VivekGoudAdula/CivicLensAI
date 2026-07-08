"""Timestamp helpers for Firestore documents."""

from __future__ import annotations

from datetime import UTC, datetime

from google.cloud import firestore


def server_timestamp() -> firestore.SERVER_TIMESTAMP:
    """Return Firestore server timestamp sentinel."""
    return firestore.SERVER_TIMESTAMP


def utc_now() -> datetime:
    """Return the current UTC datetime."""
    return datetime.now(UTC)


def ensure_utc(value: datetime) -> datetime:
    """Ensure a datetime is timezone-aware in UTC."""
    if value.tzinfo is None:
        return value.replace(tzinfo=UTC)
    return value.astimezone(UTC)
