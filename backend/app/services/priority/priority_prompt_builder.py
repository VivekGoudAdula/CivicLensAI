"""Production prompt templates for Gemini cluster priority analysis."""

from __future__ import annotations

import json

from app.services.priority.priority_calculator import ClusterPriorityContext

PRIORITY_PROMPT_VERSION = "1.0.0"


def _complaint_snapshot(complaint) -> dict:
    snapshot = {
        "id": complaint.id,
        "title": complaint.title,
        "description": complaint.description[:500],
        "category": complaint.category.value,
        "village_name": complaint.village_name,
        "landmark": complaint.landmark,
        "priority": complaint.priority.value,
        "is_duplicate": complaint.is_duplicate,
        "duplicate_score": complaint.duplicate_score,
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
            "keywords": complaint.ai_analysis.keywords[:12],
            "category": complaint.ai_analysis.category,
            "severity": complaint.ai_analysis.severity,
            "urgency": complaint.ai_analysis.urgency,
            "responsible_department": complaint.ai_analysis.responsible_department,
            "confidence_score": complaint.ai_analysis.confidence_score,
            "affected_infrastructure": complaint.ai_analysis.affected_infrastructure,
        }
    if complaint.image_analysis:
        snapshot["image_analysis"] = {
            "primary_issue": complaint.image_analysis.primary_issue,
            "severity": complaint.image_analysis.severity,
            "safety_risk": complaint.image_analysis.safety_risk,
            "road_safety_risk": complaint.image_analysis.road_safety_risk,
            "environmental_risk": complaint.image_analysis.environmental_risk,
            "requires_urgent_attention": complaint.image_analysis.requires_urgent_attention,
            "confidence_score": complaint.image_analysis.confidence_score,
        }
    return snapshot


def build_priority_analysis_prompt(context: ClusterPriorityContext) -> str:
    """Build the primary Gemini cluster priority analysis prompt."""
    cluster = context.cluster
    cluster_payload = {
        "id": cluster.id,
        "title": cluster.title,
        "description": cluster.description,
        "theme": cluster.theme,
        "category": cluster.category.value,
        "department": cluster.department,
        "village_name": cluster.village_name,
        "village_names": cluster.village_names,
        "constituency": cluster.constituency,
        "district": cluster.district,
        "state": cluster.state,
        "complaint_count": cluster.complaint_count,
        "average_severity": cluster.average_severity,
        "hotspot_score": cluster.hotspot_score,
        "affected_area": cluster.affected_area,
        "coordinates": (
            {
                "latitude": cluster.coordinates.latitude,
                "longitude": cluster.coordinates.longitude,
            }
            if cluster.coordinates
            else None
        ),
        "first_complaint_at": (
            context.first_complaint_at.isoformat() if context.first_complaint_at else None
        ),
        "latest_complaint_date": (
            cluster.latest_complaint_date.isoformat() if cluster.latest_complaint_date else None
        ),
        "days_since_first_complaint": context.days_since_first,
        "days_since_latest_complaint": context.days_since_latest,
        "duplicate_complaint_count": context.duplicate_complaint_count,
        "max_duplicate_score": context.max_duplicate_score,
        "avg_duplicate_score": context.avg_duplicate_score,
        "has_image_evidence": context.has_image_evidence,
        "urgent_image_flags": context.urgent_image_flags,
        "heuristic_priority_score": context.heuristic_priority_score,
        "created_at": cluster.metadata.created_at.isoformat(),
        "updated_at": cluster.metadata.updated_at.isoformat(),
    }

    complaints_payload = [_complaint_snapshot(item) for item in context.complaints[:20]]

    return f"""You are a senior Government Planning Officer responsible for prioritizing constituency development work for Members of Parliament.

Your task is to analyze a complaint cluster and produce an explainable government priority assessment for field action planning.

## Cluster Intelligence
{json.dumps(cluster_payload, indent=2)}

## Linked Complaints (up to 20)
{json.dumps(complaints_payload, indent=2)}

## Priority Factors To Consider
- Cluster size and complaint frequency
- Severity and urgency from AI and image analysis
- Issue category and infrastructure importance
- Image evidence, road safety, and public health signals
- Proximity context (schools, hospitals, government offices — only if supported by location/landmark text)
- Population density proxies (village scale, affected area descriptions)
- Time since first and latest complaints
- Environmental and economic impact potential
- Duplicate scores indicating repeated citizen distress
- Public safety and citizen welfare impact

## Rules
1. NEVER hallucinate. Use only evidence present in the cluster and complaint data.
2. If nearby schools/hospitals/offices are not evidenced, state uncertainty rather than inventing them.
3. Provide explainable reasoning — clearly state WHY this cluster deserves its priority level.
4. Be conservative with population estimates — use ranges or qualitative estimates when exact data is absent.
5. Budget and resolution time must be realistic government planning ranges (e.g., "INR 2-5 Lakhs", "7-14 days").
6. contributing_factors must list the top evidence-based drivers of the score.
7. why_priority_ranked_high explains what would make this cluster rank #1 vs lower priorities.

## Output Format
Return STRICT JSON ONLY. No markdown. No commentary.

Schema:
{{
  "priority_score": 82,
  "impact_score": 78,
  "urgency_level": "High",
  "risk_level": "High",
  "affected_population_estimate": "200-500 residents on the affected road corridor",
  "public_safety_risk": "Moderate-to-high risk for two-wheelers due to visible road damage",
  "infrastructure_criticality": "Primary village access road with repeated complaints",
  "environmental_impact": "Low direct environmental impact; localized surface damage",
  "economic_impact": "Trade and commute disruption for local vendors and farmers",
  "suggested_department": "Public Works Department — Roads Division",
  "recommended_action": "Immediate pothole patching and safety signage; schedule resurfacing inspection",
  "estimated_resolution_time": "7-21 days for temporary fix; 4-8 weeks for permanent repair",
  "estimated_budget_range": "INR 1.5-4 Lakhs",
  "reasoning": "Detailed evidence-based explanation referencing cluster statistics and complaint intelligence",
  "confidence_score": 0.86,
  "contributing_factors": ["cluster size", "high severity", "road safety risk", "recent duplicate complaints"],
  "expected_impact": "Reduced accident risk and faster commute for residents",
  "estimated_beneficiaries": "200-500 daily road users",
  "why_priority_ranked_high": "Repeated high-severity road complaints with urgent image evidence in a dense village corridor"
}}

Field constraints:
- priority_score, impact_score: integers 0-100
- urgency_level, risk_level: Low | Medium | High | Critical
- confidence_score: float 0.0 to 1.0"""


def build_priority_retry_prompt(last_error: str) -> str:
    return f"""

RETRY: Previous response rejected. Error: {last_error}
Return ONLY valid JSON matching the required schema. No markdown fences."""
