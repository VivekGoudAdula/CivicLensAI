"""Parse and validate Gemini cluster priority responses."""

from __future__ import annotations

import json
import logging
from datetime import UTC, datetime
from typing import Any

from pydantic import ValidationError

from app.models.domain.cluster import ClusterPriorityAnalysis
from app.models.schemas.ai_cluster_priority import GeminiClusterPriorityOutput
from app.services.ai.response_parser import AIResponseParseError, extract_json_text

logger = logging.getLogger(__name__)


class PriorityResponseParseError(AIResponseParseError):
    """Raised when Gemini priority output cannot be parsed or validated."""


def parse_priority_output(raw_text: str) -> GeminiClusterPriorityOutput:
    """Parse and strictly validate Gemini priority JSON output."""
    try:
        json_text = extract_json_text(raw_text)
        payload: dict[str, Any] = json.loads(json_text)
        return GeminiClusterPriorityOutput.model_validate(payload)
    except json.JSONDecodeError as exc:
        raise PriorityResponseParseError(f"Invalid JSON: {exc}") from exc
    except ValidationError as exc:
        raise PriorityResponseParseError(f"Schema validation failed: {exc}") from exc


def to_cluster_priority_analysis(
    output: GeminiClusterPriorityOutput,
    *,
    analysis_hash: str,
    model_version: str,
    prompt_version: str,
    priority_rank: int | None = None,
) -> ClusterPriorityAnalysis:
    """Convert validated Gemini output to persisted domain model."""
    return ClusterPriorityAnalysis(
        priority_score=output.priority_score,
        impact_score=output.impact_score,
        urgency_level=output.urgency_level,
        risk_level=output.risk_level,
        affected_population_estimate=output.affected_population_estimate,
        public_safety_risk=output.public_safety_risk,
        infrastructure_criticality=output.infrastructure_criticality,
        environmental_impact=output.environmental_impact,
        economic_impact=output.economic_impact,
        suggested_department=output.suggested_department,
        recommended_action=output.recommended_action,
        estimated_resolution_time=output.estimated_resolution_time,
        estimated_budget_range=output.estimated_budget_range,
        priority_rank=priority_rank,
        reasoning=output.reasoning,
        confidence_score=output.confidence_score,
        contributing_factors=output.contributing_factors[:20],
        expected_impact=output.expected_impact,
        estimated_beneficiaries=output.estimated_beneficiaries,
        why_priority_ranked_high=output.why_priority_ranked_high,
        analysis_hash=analysis_hash,
        processed_at=datetime.now(UTC),
        model_version=model_version,
        prompt_version=prompt_version,
    )
