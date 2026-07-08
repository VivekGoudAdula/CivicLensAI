"""Parse and validate Gemini Vision JSON responses."""

from __future__ import annotations

import json
import logging
from datetime import UTC, datetime
from typing import Any

from pydantic import ValidationError

from app.models.domain.complaint import ComplaintImageAnalysis
from app.models.schemas.ai_image_analysis import GeminiImageAnalysisOutput
from app.services.ai.response_parser import AIResponseParseError, extract_json_text

logger = logging.getLogger(__name__)


class VisionResponseParseError(AIResponseParseError):
    """Raised when Gemini Vision output cannot be parsed or validated."""


def parse_vision_output(raw_text: str) -> GeminiImageAnalysisOutput:
    """Parse and strictly validate Gemini Vision JSON output."""
    try:
        json_text = extract_json_text(raw_text)
        payload: dict[str, Any] = json.loads(json_text)
        if not payload.get("detected_objects"):
            payload["detected_objects"] = ["unidentified object"]
        return GeminiImageAnalysisOutput.model_validate(payload)
    except json.JSONDecodeError as exc:
        raise VisionResponseParseError(f"Invalid JSON: {exc}") from exc
    except ValidationError as exc:
        raise VisionResponseParseError(f"Schema validation failed: {exc}") from exc


def to_complaint_image_analysis(
    output: GeminiImageAnalysisOutput,
    *,
    model_version: str,
    prompt_version: str,
) -> ComplaintImageAnalysis:
    """Convert validated Gemini Vision output to persisted domain model."""
    now = datetime.now(UTC)
    return ComplaintImageAnalysis(
        primary_issue=output.primary_issue,
        secondary_issue=output.secondary_issue,
        description=output.description,
        severity=output.severity,
        confidence_score=output.confidence_score,
        visible_damage=output.visible_damage,
        estimated_area_affected=output.estimated_area_affected,
        safety_risk=output.safety_risk,
        suggested_department=output.suggested_department,
        suggested_immediate_action=output.suggested_immediate_action,
        suggested_long_term_action=output.suggested_long_term_action,
        possible_public_impact=output.possible_public_impact,
        duplicate_indicators=output.duplicate_indicators[:20],
        detected_objects=output.detected_objects[:50],
        environmental_risk=output.environmental_risk,
        road_safety_risk=output.road_safety_risk,
        human_presence=output.human_presence,
        vehicles_present=output.vehicles_present,
        requires_urgent_attention=output.requires_urgent_attention,
        reasoning=output.reasoning,
        processed_at=now,
        model_version=model_version,
        prompt_version=prompt_version,
    )
