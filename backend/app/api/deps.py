"""FastAPI dependency injection."""

from collections.abc import Generator
from typing import Annotated

from fastapi import Depends, Header
from google.cloud.firestore_v1 import Client as FirestoreClient
from google.generativeai import GenerativeModel

from app.core.config import Settings, get_settings
from app.services.firebase import get_firestore_client
from app.services.gemini import get_gemini_model


def get_app_settings() -> Settings:
    """Dependency for application settings."""
    return get_settings()


def get_db() -> Generator[FirestoreClient, None, None]:
    """Dependency for Firestore database client."""
    yield get_firestore_client()


def get_ai_model() -> Generator[GenerativeModel, None, None]:
    """Dependency for Gemini generative model."""
    yield get_gemini_model()


SettingsDep = Annotated[Settings, Depends(get_app_settings)]
FirestoreDep = Annotated[FirestoreClient, Depends(get_db)]
GeminiDep = Annotated[GenerativeModel, Depends(get_ai_model)]


def get_current_user_email(
    settings: Settings = Depends(get_app_settings),
    authorization: str | None = Header(default=None),
) -> str | None:
    """Dependency to retrieve the email of the currently authenticated user."""
    return get_user_from_auth_header(authorization, settings)


def get_user_from_auth_header(auth_header: str | None, settings: Settings) -> str | None:
    if not auth_header:
        return None
    try:
        parts = auth_header.split()
        if len(parts) != 2 or parts[0].lower() != "bearer":
            return None
        token = parts[1]
        import jwt
        payload = jwt.decode(token, settings.jwt_secret, algorithms=["HS256"])
        return payload.get("sub")
    except Exception:
        return None

