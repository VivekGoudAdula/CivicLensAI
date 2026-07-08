"""Production prompt templates for Gemini duplicate matching."""

from __future__ import annotations

import json

from app.models.domain.complaint import ComplaintResponse
from app.services.clustering.similarity_engine import CandidateScore

CLUSTERING_PROMPT_VERSION = "1.0.0"


def _complaint_snapshot(complaint: ComplaintResponse) -> dict:
    snapshot = {
        "id": complaint.id,
        "title": complaint.title,
        "description": complaint.description,
        "category": complaint.category.value,
        "village_name": complaint.village_name,
        "landmark": complaint.landmark,
        "cluster_id": complaint.cluster_id,
        "submitted_at": complaint.submitted_at.isoformat(),
    }
    if complaint.location:
        snapshot["location"] = {
            "latitude": complaint.location.latitude,
            "longitude": complaint.location.longitude,
            "address": complaint.location.address,
        }
    if complaint.ai_analysis:
        snapshot["ai_analysis"] = {
            "summary": complaint.ai_analysis.summary,
            "keywords": complaint.ai_analysis.keywords[:15],
            "category": complaint.ai_analysis.category,
            "sub_category": complaint.ai_analysis.sub_category,
            "severity": complaint.ai_analysis.severity,
            "responsible_department": complaint.ai_analysis.responsible_department,
            "confidence_score": complaint.ai_analysis.confidence_score,
        }
    if complaint.image_analysis:
        snapshot["image_analysis"] = {
            "primary_issue": complaint.image_analysis.primary_issue,
            "secondary_issue": complaint.image_analysis.secondary_issue,
            "severity": complaint.image_analysis.severity,
            "detected_objects": complaint.image_analysis.detected_objects[:15],
            "duplicate_indicators": complaint.image_analysis.duplicate_indicators[:10],
            "confidence_score": complaint.image_analysis.confidence_score,
        }
    return snapshot


def build_duplicate_matching_prompt(
    source: ComplaintResponse,
    candidates: list[CandidateScore],
) -> str:
    """Build Gemini prompt for duplicate detection against ranked candidates."""
    candidate_payload = []
    for item in candidates:
        snapshot = _complaint_snapshot(item.complaint)
        snapshot["heuristic_score"] = item.heuristic_score
        snapshot["distance_km"] = item.distance_km
        snapshot["keyword_overlap"] = item.keyword_overlap
        candidate_payload.append(snapshot)

    return f"""You are an Intelligent Civic Complaint Matching Engine for a government grievance system.

Your task is to determine whether the NEW complaint is a duplicate of any CANDIDATE complaint.

## NEW Complaint
{json.dumps(_complaint_snapshot(source), indent=2)}

## CANDIDATE Complaints (pre-filtered by category, location, department, and heuristic similarity)
{json.dumps(candidate_payload, indent=2)}

## Matching Criteria
Consider:
- Title and description semantic similarity
- AI summary, keywords, and category alignment
- Image analysis primary issue, detected objects, and duplicate indicators
- Severity alignment
- Geographic proximity (distance_km) and shared landmark/ward context
- Same responsible department
- Whether candidates already belong to a cluster (cluster_id)

## Rules
1. Only mark is_duplicate=true when evidence strongly indicates the same underlying civic issue.
2. similarity_score is 0-100 (integer) reflecting overall duplicate likelihood.
3. If duplicate, set matched_complaint_id to the best matching candidate ID.
4. If the matched candidate has cluster_id, set existing_cluster_id to that cluster_id.
5. If no strong duplicate exists, set is_duplicate=false, similarity_score below 50, and null IDs.
6. Be conservative — when uncertain, prefer is_duplicate=false with lower confidence.
7. Never hallucinate facts not present in the complaint data.

## Output Format
Return STRICT JSON ONLY. No markdown. No commentary.

Schema:
{{
  "is_duplicate": true,
  "similarity_score": 85,
  "matching_reason": "Both complaints describe the same pothole location with matching keywords and GPS proximity.",
  "existing_cluster_id": "cluster_abc123",
  "matched_complaint_id": "complaint_xyz789",
  "confidence": 0.91,
  "explanation": "Detailed evidence-based explanation referencing specific matching fields."
}}"""


def build_matching_retry_prompt(last_error: str) -> str:
    return f"""

RETRY: Previous response rejected. Error: {last_error}
Return ONLY valid JSON matching the required schema. No markdown fences."""
