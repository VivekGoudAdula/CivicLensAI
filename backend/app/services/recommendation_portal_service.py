"""Recommendation portal aggregation service."""

from __future__ import annotations

from datetime import UTC, datetime

from app.db.pagination import PaginationParams
from app.models.schemas.recommendation_portal import (
    RecommendationCenterResponse,
    RecommendationListItem,
    RecommendationListResponse,
)
from app.repositories.recommendation_repository import RecommendationRepository
from app.services.recommendation.recommendation_engine_repository import RecommendationEngineRepository
from app.services.recommendation.recommendation_prompt_builder import RECOMMENDATION_PROMPT_VERSION
from app.services.gemini import get_configured_model_name


class RecommendationPortalService:
    """Portal service for the AI Decision Recommendation Center."""

    def __init__(
        self,
        recommendation_repo: RecommendationRepository,
        engine_repo: RecommendationEngineRepository,
    ):
        self.recommendation_repo = recommendation_repo
        self.engine_repo = engine_repo

    def get_center(self) -> RecommendationCenterResponse:
        cached = self.engine_repo._last_output
        if cached is None:
            result = self.recommendation_repo.list(
                pagination=PaginationParams(limit=10, order_by="metadata.created_at", order_direction="desc"),
            )
            if not result.items:
                return RecommendationCenterResponse(
                    executive_brief="No AI recommendations generated yet. Run the recommendation engine to produce MP decision intelligence.",
                    decision_timeline_summary="Generate recommendations to view the decision timeline.",
                    recommendations=[],
                    total_recommendations=0,
                    engine="none",
                    model_version="n/a",
                    prompt_version=RECOMMENDATION_PROMPT_VERSION,
                    context_hash="",
                    generated_at=datetime.now(UTC),
                )
            from app.models.schemas.ai_mp_recommendation import MpDevelopmentWorkItem

            items = [
                MpDevelopmentWorkItem(
                    priority_rank=index,
                    project_title=rec.title,
                    category="General",
                    village=rec.constituency,
                    department=rec.department_name,
                    reason=rec.ai_recommendation.rationale if rec.ai_recommendation else rec.description[:200],
                    impact_score=70,
                    priority_score=70,
                    urgency=rec.priority.value,
                    estimated_beneficiaries="Constituency citizens",
                    estimated_budget=f"₹{rec.estimated_budget_inr:,.0f}" if rec.estimated_budget_inr else "TBD",
                    estimated_resolution_time=f"{rec.estimated_timeline_days or 30} days",
                    government_scheme=None,
                    expected_social_impact=rec.ai_recommendation.expected_impact if rec.ai_recommendation else "",
                    expected_infrastructure_improvement="Infrastructure improvement",
                    ai_confidence=rec.ai_recommendation.confidence_score if rec.ai_recommendation else 0.7,
                    risk_if_ignored=rec.ai_recommendation.risk_assessment if rec.ai_recommendation else "",
                    executive_summary=rec.title,
                    detailed_explanation=rec.description,
                    recommended_action=(
                        rec.ai_recommendation.action_items[0]
                        if rec.ai_recommendation and rec.ai_recommendation.action_items
                        else "Review with department"
                    ),
                    cluster_id=rec.cluster_ids[0] if rec.cluster_ids else None,
                )
                for index, rec in enumerate(result.items[:10], start=1)
            ]
            return RecommendationCenterResponse(
                executive_brief="Latest persisted constituency development recommendations.",
                decision_timeline_summary="Review top-ranked works with departmental heads this week.",
                recommendations=items,
                total_recommendations=len(items),
                engine="persisted",
                model_version=get_configured_model_name() or "gemini-2.5-flash",
                prompt_version=RECOMMENDATION_PROMPT_VERSION,
                context_hash=self.engine_repo.last_context_hash or "",
                generated_at=datetime.now(UTC),
            )

        return RecommendationCenterResponse(
            executive_brief=cached.executive_brief,
            decision_timeline_summary=cached.decision_timeline_summary,
            recommendations=sorted(cached.recommendations, key=lambda r: r.priority_rank),
            total_recommendations=len(cached.recommendations),
            engine="gemini" if get_configured_model_name() else "heuristic",
            model_version=get_configured_model_name() or "heuristic-v1",
            prompt_version=RECOMMENDATION_PROMPT_VERSION,
            context_hash=self.engine_repo.last_context_hash or "",
            generated_at=self.engine_repo._last_generated_at or datetime.now(UTC),
            from_cache=True,
        )

    def list_recommendations(self, *, limit: int = 50) -> RecommendationListResponse:
        result = self.recommendation_repo.list(
            pagination=PaginationParams(limit=limit, order_by="metadata.created_at", order_direction="desc"),
        )
        items = [
            RecommendationListItem(
                id=rec.id,
                title=rec.title,
                description=rec.description[:300],
                status=rec.status.value,
                priority=rec.priority.value,
                department_name=rec.department_name,
                estimated_budget_inr=rec.estimated_budget_inr,
                estimated_timeline_days=rec.estimated_timeline_days,
                confidence_score=rec.ai_recommendation.confidence_score if rec.ai_recommendation else None,
                created_at=rec.metadata.created_at,
            )
            for rec in result.items
        ]
        return RecommendationListResponse(items=items, total=len(items))
