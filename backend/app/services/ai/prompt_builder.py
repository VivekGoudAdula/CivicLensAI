"""Production prompt templates for Gemini civic complaint analysis."""

from __future__ import annotations

from app.models.domain.complaint import ComplaintResponse

SYSTEM_ROLE = (
    "You are an expert Government Civic Intelligence Officer responsible for analyzing "
    "citizen grievances submitted to Members of Parliament in India."
)

OUTPUT_RULES = """\
Return STRICT JSON only. No markdown, no prose outside JSON.
Use lowercase for urgency, severity, priority_level, and sentiment values.
confidence_score and duplicate_possibility must be between 0 and 1.
keywords: 3-10 concise civic issue terms.
tags: 2-8 classification tags.
If input is not English, fill translated_english with a faithful English translation.
If audio is attached, transcribe it into voice_transcript.
Estimate affected_citizens_estimate when reasonable (e.g. "50-100 households").
government_scheme: name applicable central/state scheme or null.
Map priority using citizen impact and infrastructure criticality."""

JSON_FIELD_SPEC = """\
Required JSON fields:
category, sub_category, responsible_department, urgency, severity, priority_level,
summary, detailed_explanation, keywords, affected_infrastructure,
affected_citizens_estimate, government_scheme, suggested_immediate_action,
suggested_long_term_action, required_department, required_team, confidence_score,
reasoning, duplicate_possibility, tags, language_detected, translated_english,
voice_transcript, sentiment"""


def build_complaint_analysis_prompt(complaint: ComplaintResponse) -> str:
    """Build an optimized analysis prompt from complaint context."""
    location_line = "Not provided"
    if complaint.location:
        location_line = (
            f"lat={complaint.location.latitude:.6f}, "
            f"lng={complaint.location.longitude:.6f}, "
            f"address={complaint.location.address or 'N/A'}"
        )

    user_category = complaint.category_name or complaint.category.value
    media_notes: list[str] = []
    if complaint.image_base64:
        media_notes.append("Photo evidence is attached — inspect visible civic damage.")
    if complaint.audio_base64:
        media_notes.append(
            "Voice recording is attached — transcribe and factor into analysis."
        )
    media_section = "\n".join(media_notes) if media_notes else "No media attachments."

    return f"""{SYSTEM_ROLE}

Analyze this citizen complaint for Amethi constituency civic operations.

{OUTPUT_RULES}

{JSON_FIELD_SPEC}

COMPLAINT
Title: {complaint.title}
Description: {complaint.description}
User Category: {user_category}
Submitter Category Slug: {complaint.category_slug or complaint.category.value}
Location: {location_line}
Landmark: {complaint.landmark or "N/A"}
Constituency: {complaint.constituency}, {complaint.district}, {complaint.state}
Media: {media_section}

Analyze department ownership, urgency, severity, routing, and actionable recommendations.
Be factual, concise, and government-ready."""


def build_retry_prompt(previous_error: str) -> str:
    """Append retry instruction when JSON validation fails."""
    return (
        f"\n\nPREVIOUS RESPONSE INVALID: {previous_error}\n"
        "Return corrected STRICT JSON matching the required schema exactly."
    )
