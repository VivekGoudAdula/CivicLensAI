"""Firebase Admin SDK and Firestore initialization."""

from __future__ import annotations

import json
import logging
import os
from pathlib import Path
from typing import TYPE_CHECKING

import firebase_admin
from firebase_admin import credentials, firestore
from google.cloud import firestore as gcloud_firestore

from app.core.config import Settings
from app.core.exceptions import ConfigurationError

if TYPE_CHECKING:
    from google.cloud.firestore_v1 import Client as FirestoreClient

logger = logging.getLogger(__name__)

_firestore_client: FirestoreClient | None = None
_firebase_initialized: bool = False


def _resolve_credentials(settings: Settings) -> credentials.Base:
    if settings.firebase_service_account_json:
        try:
            service_account_info = json.loads(settings.firebase_service_account_json)
        except json.JSONDecodeError as exc:
            raise ConfigurationError(
                "FIREBASE_SERVICE_ACCOUNT_JSON contains invalid JSON"
            ) from exc
        return credentials.Certificate(service_account_info)

    if settings.firebase_service_account_path:
        path = Path(settings.firebase_service_account_path)
        if not path.is_file():
            raise ConfigurationError(
                f"Firebase service account file not found: {path}"
            )
        return credentials.Certificate(str(path.resolve()))

    raise ConfigurationError(
        "Firebase credentials not configured. Set FIREBASE_SERVICE_ACCOUNT_PATH "
        "or FIREBASE_SERVICE_ACCOUNT_JSON, or use FIRESTORE_EMULATOR_HOST."
    )


def initialize_firebase(settings: Settings) -> FirestoreClient:
    """Initialize Firebase Admin SDK and return a Firestore client."""
    global _firestore_client, _firebase_initialized

    if _firebase_initialized and _firestore_client is not None:
        return _firestore_client

    if settings.firestore_emulator_host:
        os.environ["FIRESTORE_EMULATOR_HOST"] = settings.firestore_emulator_host
        logger.info(
            "Using Firestore emulator at %s",
            settings.firestore_emulator_host,
        )
        _firestore_client = gcloud_firestore.Client(project="civiclens-ai-dev")
        _firebase_initialized = True
        logger.info("Firestore emulator client initialized successfully")
        return _firestore_client

    cred = _resolve_credentials(settings)

    if not firebase_admin._apps:
        firebase_admin.initialize_app(cred)

    _firestore_client = firestore.client()
    _firebase_initialized = True

    logger.info("Firestore client initialized successfully")
    return _firestore_client


def get_firestore_client() -> FirestoreClient:
    """Return the initialized Firestore client."""
    if _firestore_client is None:
        raise ConfigurationError("Firestore client has not been initialized")
    return _firestore_client


def is_firestore_initialized() -> bool:
    """Check whether Firestore has been initialized."""
    return _firebase_initialized and _firestore_client is not None


def verify_firestore_connection() -> bool:
    """Perform a lightweight connectivity check against Firestore."""
    if not is_firestore_initialized():
        return False

    try:
        collections = _firestore_client.collections()
        next(collections, None)
        return True
    except Exception:
        logger.exception("Firestore connectivity check failed")
        return False


def shutdown_firebase() -> None:
    """Clean up Firebase resources on application shutdown."""
    global _firestore_client, _firebase_initialized

    if firebase_admin._apps:
        firebase_admin.delete_app(firebase_admin.get_app())

    _firestore_client = None
    _firebase_initialized = False
    logger.info("Firebase resources released")
