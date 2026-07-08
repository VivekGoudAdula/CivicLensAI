"""Parse and validate Gemini MP recommendation responses."""

from __future__ import annotations

import logging

from pydantic import ValidationError

from app.models.schemas.ai_mp_recommendation import GeminiMpRecommendationOutput
from app.services.ai.response_parser import extract_json_text

logger = logging.getLogger(__name__)


class RecommendationResponseParseError(ValueError):
    """Raised when Gemini recommendation output cannot be parsed."""


def parse_recommendation_output(raw_text: str) -> GeminiMpRecommendationOutput:
    try:
        payload = extract_json_text(raw_text)
        output = GeminiMpRecommendationOutput.model_validate(payload)
        ranks = sorted(item.priority_rank for item in output.recommendations)
        if len(output.recommendations) != 10:
            raise RecommendationResponseParseError(
                f"Expected 10 recommendations, got {len(output.recommendations)}"
            )
        return output
    except (ValidationError, ValueError, TypeError) as exc:
        logger.warning("Recommendation parse failed: %s", exc)
        raise RecommendationResponseParseError(str(exc)) from exc
