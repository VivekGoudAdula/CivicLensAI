"""Parse and validate Gemini duplicate matching responses."""

from __future__ import annotations

import json
import logging
from typing import Any

from pydantic import ValidationError

from app.models.schemas.ai_duplicate_matching import GeminiDuplicateMatchOutput
from app.services.ai.response_parser import AIResponseParseError, extract_json_text

logger = logging.getLogger(__name__)


class DuplicateMatchParseError(AIResponseParseError):
    """Raised when Gemini duplicate matching output is invalid."""


def parse_duplicate_match_output(raw_text: str) -> GeminiDuplicateMatchOutput:
    """Parse and validate Gemini duplicate matching JSON."""
    try:
        json_text = extract_json_text(raw_text)
        payload: dict[str, Any] = json.loads(json_text)
        return GeminiDuplicateMatchOutput.model_validate(payload)
    except json.JSONDecodeError as exc:
        raise DuplicateMatchParseError(f"Invalid JSON: {exc}") from exc
    except ValidationError as exc:
        raise DuplicateMatchParseError(f"Schema validation failed: {exc}") from exc
