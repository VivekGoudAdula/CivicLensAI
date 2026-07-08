"""Production prompt templates for Gemini Vision civic image analysis."""

from __future__ import annotations

from app.models.domain.complaint import ComplaintResponse
from app.models.schemas.ai_image_analysis import SUPPORTED_CIVIC_ISSUE_TYPES

VISION_PROMPT_VERSION = "1.0.0"

ISSUE_TYPE_LIST = "\n".join(f"- {issue}" for issue in SUPPORTED_CIVIC_ISSUE_TYPES[:-1])

JSON_SCHEMA_EXAMPLE = """{
  "primary_issue": "Pothole",
  "secondary_issue": "Broken Road",
  "description": "Visible crater in asphalt lane with loose debris at the road edge.",
  "severity": "High",
  "confidence_score": 0.87,
  "visible_damage": "Deep pothole approximately 40-60 cm wide with broken asphalt edges.",
  "estimated_area_affected": "Roughly 0.5 square meters of road surface.",
  "safety_risk": "Moderate risk to two-wheeler riders due to depth and location in travel lane.",
  "suggested_department": "Public Works Department - Roads Division",
  "suggested_immediate_action": "Place warning signage and temporary barricade; dispatch patch crew.",
  "suggested_long_term_action": "Resurface affected road section after root-cause inspection.",
  "possible_public_impact": "Traffic slowdown and potential vehicle damage if unaddressed.",
  "duplicate_indicators": ["similar pothole pattern", "asphalt edge cracking"],
  "detected_objects": ["pothole", "asphalt", "road", "debris"],
  "environmental_risk": "Low — localized road surface damage only.",
  "road_safety_risk": "High for two-wheelers at night without lighting.",
  "human_presence": false,
  "vehicles_present": false,
  "requires_urgent_attention": true,
  "reasoning": "The depression and fractured asphalt are clearly visible. Severity is high due to depth and lane position. No speculation beyond visible evidence."
}"""


def build_vision_analysis_prompt(complaint: ComplaintResponse) -> str:
    """Build the primary Gemini Vision analysis prompt."""
    category = complaint.category_name or complaint.category.value
    location_hint = ""
    if complaint.location and complaint.location.address:
        location_hint = complaint.location.address
    elif complaint.landmark:
        location_hint = complaint.landmark

    return f"""You are an expert Government Infrastructure Inspection Officer responsible for analyzing civic issue photographs submitted by citizens.

Your task is to inspect the attached photograph and produce a structured assessment of the visible civic infrastructure issue.

## Complaint Context (secondary — prioritize visual evidence)
- Title: {complaint.title}
- Citizen description: {complaint.description}
- Selected category: {category}
- Location hint: {location_hint or "Not provided"}

## Supported Primary Issue Types
Select primary_issue from this list ONLY. If no type clearly matches visible evidence, use "Unknown".
{ISSUE_TYPE_LIST}
- Unknown

secondary_issue may be another type from the same list, or null if not applicable.

## Severity Levels
Low | Medium | High | Critical

## Core Rules
1. NEVER hallucinate. Describe ONLY what is clearly visible in the photograph.
2. If the image is blurry, dark, unrelated, or insufficient, set primary_issue to "Unknown", lower confidence_score, and explain uncertainty in reasoning.
3. Do NOT infer causes, dates, or off-frame conditions unless directly supported by visible evidence.
4. Use conservative severity when evidence is ambiguous.
5. detected_objects must list concrete visible objects (e.g., "pothole", "garbage bags", "streetlight pole").
6. duplicate_indicators should list visual patterns that could match other complaints (e.g., "standard municipal bin", "identical road marking").
7. confidence_score is 0.0–1.0 reflecting visual certainty of primary_issue classification.
8. requires_urgent_attention is true only when visible evidence shows imminent safety hazard.

## Output Format
Return STRICT JSON ONLY. No markdown, no commentary, no code fences.

Required JSON schema:
{JSON_SCHEMA_EXAMPLE}

Field constraints:
- severity: one of Low, Medium, High, Critical
- confidence_score: float 0.0 to 1.0
- duplicate_indicators: array of strings (empty array if none)
- detected_objects: non-empty array of strings
- human_presence, vehicles_present, requires_urgent_attention: boolean
- All string fields must be substantive and evidence-based"""


def build_vision_retry_prompt(last_error: str) -> str:
    """Append retry instructions when prior response failed validation."""
    return f"""

RETRY INSTRUCTION: Your previous response was rejected.
Error: {last_error}

Return ONLY a valid JSON object matching the required schema. No markdown fences. No extra text."""
