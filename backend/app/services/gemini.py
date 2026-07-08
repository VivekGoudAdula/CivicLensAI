"""Google Gemini AI client initialization."""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

import google.generativeai as genai

from app.core.config import Settings
from app.core.exceptions import ConfigurationError

if TYPE_CHECKING:
    from google.generativeai import GenerativeModel

logger = logging.getLogger(__name__)

_gemini_model: GenerativeModel | None = None
_gemini_initialized: bool = False
_configured_model_name: str = ""


def initialize_gemini(settings: Settings) -> GenerativeModel:
    """Configure and return the Gemini generative model."""
    global _gemini_model, _gemini_initialized, _configured_model_name

    if not settings.gemini_api_key:
        raise ConfigurationError("GEMINI_API_KEY is not configured")

    if _gemini_initialized and _gemini_model is not None:
        return _gemini_model

    genai.configure(api_key=settings.gemini_api_key)
    _gemini_model = genai.GenerativeModel(settings.gemini_model)
    _configured_model_name = settings.gemini_model
    _gemini_initialized = True

    logger.info("Gemini client initialized with model: %s", settings.gemini_model)
    return _gemini_model


def get_gemini_model() -> GenerativeModel:
    """Return the initialized Gemini model."""
    if _gemini_model is None:
        raise ConfigurationError("Gemini client has not been initialized")
    return _gemini_model


def is_gemini_initialized() -> bool:
    """Check whether Gemini has been initialized."""
    return _gemini_initialized and _gemini_model is not None


def get_configured_model_name() -> str:
    """Return the configured Gemini model name."""
    return _configured_model_name


def verify_gemini_connection() -> bool:
    """Verify Gemini client is configured and ready."""
    return is_gemini_initialized()
