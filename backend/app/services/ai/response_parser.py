"""Parse and validate Gemini JSON responses for complaint analysis."""

from __future__ import annotations

import json
import logging
import re
from datetime import UTC, datetime
from typing import Any

from pydantic import ValidationError

from app.models.domain.complaint import ComplaintAIAnalysis
from app.models.enums.common import ComplaintPriority, SentimentLabel
from app.models.schemas.ai_complaint_analysis import GeminiComplaintAnalysisOutput

logger = logging.getLogger(__name__)

URGENCY_SCORE_MAP = {
    "low": 0.25,
    "medium": 0.5,
    "high": 0.75,
    "critical": 0.95,
}

PRIORITY_MAP = {
    "low": ComplaintPriority.LOW,
    "medium": ComplaintPriority.MEDIUM,
    "high": ComplaintPriority.HIGH,
    "critical": ComplaintPriority.CRITICAL,
}

SENTIMENT_MAP = {
    "positive": SentimentLabel.POSITIVE,
    "neutral": SentimentLabel.NEUTRAL,
    "negative": SentimentLabel.NEGATIVE,
    "mixed": SentimentLabel.MIXED,
}


class AIResponseParseError(ValueError):
    """Raised when Gemini output cannot be parsed or validated."""


def extract_json_text(raw_text: str) -> str:
    """Extract JSON object from model text, stripping markdown fences if present."""
    text = raw_text.strip()
    if text.startswith("```"):
        text = re.sub(r"^```(?:json)?\s*", "", text)
        text = re.sub(r"\s*```$", "", text)
    start = text.find("{")
    end = text.rfind("}")
    if start == -1 or end == -1 or end <= start:
        raise AIResponseParseError("No JSON object found in model response")
    return text[start : end + 1]


def parse_gemini_output(raw_text: str) -> GeminiComplaintAnalysisOutput:
    """Parse and strictly validate Gemini JSON output."""
    try:
        json_text = extract_json_text(raw_text)
        payload: dict[str, Any] = json.loads(json_text)
        if "keywords" in payload and not payload["keywords"]:
            payload["keywords"] = ["civic issue"]
        return GeminiComplaintAnalysisOutput.model_validate(payload)
    except json.JSONDecodeError as exc:
        raise AIResponseParseError(f"Invalid JSON: {exc}") from exc
    except ValidationError as exc:
        raise AIResponseParseError(f"Schema validation failed: {exc}") from exc


def map_priority_level(value: str) -> ComplaintPriority:
    """Map AI priority string to domain enum."""
    return PRIORITY_MAP.get(value.lower().strip(), ComplaintPriority.MEDIUM)


def map_sentiment(value: str) -> SentimentLabel:
    """Map AI sentiment string to domain enum."""
    return SENTIMENT_MAP.get(value.lower().strip(), SentimentLabel.NEUTRAL)


def map_urgency_score(urgency: str, severity: str) -> float:
    """Derive numeric urgency score from categorical urgency and severity."""
    urgency_score = URGENCY_SCORE_MAP.get(urgency.lower().strip(), 0.5)
    severity_score = URGENCY_SCORE_MAP.get(severity.lower().strip(), 0.5)
    return round(min(1.0, (urgency_score * 0.6) + (severity_score * 0.4)), 3)


def to_complaint_ai_analysis(
    output: GeminiComplaintAnalysisOutput,
    *,
    model_version: str,
    prompt_version: str,
) -> ComplaintAIAnalysis:
    """Convert validated Gemini output to persisted domain model."""
    now = datetime.now(UTC)
    language = output.language_detected[:16]
    return ComplaintAIAnalysis(
        category=output.category,
        sub_category=output.sub_category,
        responsible_department=output.responsible_department,
        urgency=output.urgency,
        severity=output.severity,
        priority_level=output.priority_level,
        summary=output.summary,
        detailed_explanation=output.detailed_explanation,
        keywords=output.keywords[:50],
        affected_infrastructure=output.affected_infrastructure,
        affected_citizens_estimate=output.affected_citizens_estimate,
        government_scheme=output.government_scheme,
        suggested_immediate_action=output.suggested_immediate_action,
        suggested_long_term_action=output.suggested_long_term_action,
        required_department=output.required_department,
        required_team=output.required_team,
        confidence_score=output.confidence_score,
        reasoning=output.reasoning,
        duplicate_possibility=output.duplicate_possibility,
        tags=output.tags[:20],
        language_detected=output.language_detected,
        translated_english=output.translated_english,
        voice_transcript=output.voice_transcript,
        sentiment=map_sentiment(output.sentiment),
        urgency_score=map_urgency_score(output.urgency, output.severity),
        language=language,
        processed_at=now,
        model_version=model_version,
        prompt_version=prompt_version,
    )
