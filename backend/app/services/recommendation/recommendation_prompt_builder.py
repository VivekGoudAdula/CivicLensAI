"""Prompt templates for MP decision recommendation engine."""

from __future__ import annotations

import json

from app.services.recommendation.recommendation_context_builder import RecommendationContext

RECOMMENDATION_PROMPT_VERSION = "1.0.0"

SYSTEM_ROLE = (
    "You are the Chief Development Planning Officer assisting a Member of Parliament "
    "in making constituency development decisions."
)

OUTPUT_SCHEMA = {
    "executive_brief": "string — 2-3 sentence MP morning briefing",
    "decision_timeline_summary": "string — suggested 30-day action timeline",
    "recommendations": [
        {
            "priority_rank": "integer 1-10",
            "project_title": "string",
            "category": "string",
            "village": "string",
            "department": "string",
            "reason": "string",
            "impact_score": "integer 0-100",
            "priority_score": "integer 0-100",
            "urgency": "low|medium|high|critical",
            "estimated_beneficiaries": "string",
            "estimated_budget": "string — INR range",
            "estimated_resolution_time": "string",
            "government_scheme": "string or null",
            "expected_social_impact": "string",
            "expected_infrastructure_improvement": "string",
            "ai_confidence": "float 0-1",
            "risk_if_ignored": "string",
            "executive_summary": "string",
            "detailed_explanation": "string",
            "recommended_action": "string",
            "cluster_id": "string or null",
        }
    ],
}


def build_recommendation_prompt(context: RecommendationContext) -> str:
    return f"""{SYSTEM_ROLE}

Answer the fundamental question: "What should the MP prioritize today?"

Use ONLY the constituency intelligence below. Recommendations must be explainable, practical, and grounded in evidence.

CONSTITUENCY INTELLIGENCE (JSON):
{json.dumps(context.payload, indent=2, default=str)}

INSTRUCTIONS:
1. Return exactly 10 recommended development works ranked by priority_rank (1 = highest).
2. Each recommendation must cite villages, departments, and complaint/cluster evidence from the data.
3. Budget estimates must be realistic INR ranges for rural Uttar Pradesh constituency works.
4. If a government scheme applies (Jal Jeevan Mission, PMGSY, MGNREGA, etc.), include it.
5. recommended_action must be a concrete next step the MP office can take this week.

Return STRICT JSON matching this schema:
{json.dumps(OUTPUT_SCHEMA, indent=2)}
"""


def build_recommendation_retry_prompt(error_message: str) -> str:
    return f"""

PREVIOUS RESPONSE WAS INVALID: {error_message}

Return corrected STRICT JSON only. Ensure exactly 10 recommendations with priority_rank 1 through 10.
"""
