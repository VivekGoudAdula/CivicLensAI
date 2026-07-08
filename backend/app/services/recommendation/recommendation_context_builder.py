"""Build structured context for MP decision recommendation prompts."""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from datetime import UTC, datetime

from app.models.domain.cluster import ClusterResponse
from app.models.domain.complaint import ComplaintResponse
from app.models.schemas.analytics_intelligence import AnalyticsIntelligenceResponse
from app.models.schemas.gis_portal import GisMapResponse
from app.models.schemas.priority_portal import PriorityDashboardResponse


@dataclass(frozen=True)
class RecommendationContext:
    """Aggregated constituency intelligence for Gemini decision engine."""

    constituency: str
    district: str
    state: str
    generated_at: datetime
    context_hash: str
    payload: dict


class RecommendationContextBuilder:
    """Assembles all available intelligence into a single decision context."""

    def build(
        self,
        complaints: list[ComplaintResponse],
        clusters: list[ClusterResponse],
        priority_dashboard: PriorityDashboardResponse,
        analytics: AnalyticsIntelligenceResponse,
        gis_map: GisMapResponse,
    ) -> RecommendationContext:
        constituency = complaints[0].constituency if complaints else "Amethi"
        district = complaints[0].district if complaints else "Amethi"
        state = complaints[0].state if complaints else "Uttar Pradesh"

        top_clusters = [
            {
                "id": c.id,
                "title": c.title,
                "complaint_count": c.complaint_count,
                "village": c.village_name,
                "department": c.recommended_department or c.department,
                "priority_score": (
                    c.priority_analysis.priority_score
                    if c.priority_analysis
                    else int((c.priority_score or 0) * 100)
                ),
                "urgency": c.urgency_level,
                "severity": c.average_severity,
            }
            for c in sorted(
                clusters,
                key=lambda item: (
                    item.priority_analysis.priority_score
                    if item.priority_analysis
                    else int((item.priority_score or 0) * 100)
                ),
                reverse=True,
            )[:15]
        ]

        recent_complaints = [
            {
                "id": c.id,
                "title": c.title,
                "category": c.category_name or c.category.value,
                "village": c.village_name,
                "status": c.status.value,
                "priority": c.priority.value,
                "severity": (
                    c.image_analysis.severity
                    if c.image_analysis
                    else c.ai_analysis.severity if c.ai_analysis else None
                ),
                "department": (
                    c.ai_analysis.responsible_department
                    if c.ai_analysis
                    else c.image_analysis.suggested_department if c.image_analysis else None
                ),
                "ai_summary": c.ai_analysis.summary if c.ai_analysis else None,
                "submitted_at": c.submitted_at.isoformat(),
            }
            for c in complaints[:25]
        ]

        payload = {
            "constituency": constituency,
            "district": district,
            "state": state,
            "kpis": analytics.kpis.model_dump(),
            "predictive_analytics": [card.model_dump() for card in analytics.predictive.cards],
            "top_villages": [p.model_dump() for p in analytics.charts.top_villages[:8]],
            "top_departments": [p.model_dump() for p in analytics.charts.top_departments[:8]],
            "complaint_trends": {
                "daily": [p.model_dump() for p in analytics.charts.complaint_trend_daily[-14:]],
                "weekly": [p.model_dump() for p in analytics.charts.complaint_trend_weekly[-8:]],
            },
            "priority_dashboard": {
                "critical_clusters": priority_dashboard.critical_clusters,
                "average_priority_score": priority_dashboard.average_priority_score,
                "top_priorities": [c.model_dump() for c in priority_dashboard.top_priorities[:10]],
            },
            "gis_intelligence": {
                "mapped_complaints": gis_map.total_complaints,
                "mapped_clusters": gis_map.total_clusters,
                "hotspots": [
                    {
                        "title": c.title,
                        "complaint_count": c.complaint_count,
                        "heat_weight": c.heat_weight,
                        "village": c.village_name,
                    }
                    for c in sorted(gis_map.clusters, key=lambda x: x.heat_weight, reverse=True)[:10]
                ],
            },
            "top_clusters": top_clusters,
            "recent_complaints": recent_complaints,
        }

        canonical = json.dumps(payload, sort_keys=True, default=str)
        context_hash = hashlib.sha256(canonical.encode()).hexdigest()[:16]

        return RecommendationContext(
            constituency=constituency,
            district=district,
            state=state,
            generated_at=datetime.now(UTC),
            context_hash=context_hash,
            payload=payload,
        )
