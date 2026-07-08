"""Gemini-powered MP decision recommendation engine."""

from __future__ import annotations

import logging
import time

import google.generativeai as genai
from google.generativeai import GenerativeModel

from app.core.config import Settings
from app.core.exceptions import BadRequestError
from app.db.pagination import PaginationParams
from app.models.schemas.ai_mp_recommendation import GeminiMpRecommendationOutput, MpDevelopmentWorkItem
from app.repositories.cluster_repository import ClusterRepository
from app.repositories.complaint_repository import ComplaintRepository
from app.services.analytics_intelligence_service import AnalyticsIntelligenceService
from app.services.gemini import get_configured_model_name
from app.services.gis_portal_service import GisPortalService
from app.services.priority_portal_service import PriorityPortalService
from app.services.recommendation.recommendation_context_builder import (
    RecommendationContext,
    RecommendationContextBuilder,
)
from app.services.recommendation.recommendation_engine_repository import RecommendationEngineRepository
from app.services.recommendation.recommendation_prompt_builder import (
    RECOMMENDATION_PROMPT_VERSION,
    build_recommendation_prompt,
    build_recommendation_retry_prompt,
)
from app.services.recommendation.recommendation_response_parser import (
    RecommendationResponseParseError,
    parse_recommendation_output,
)

logger = logging.getLogger(__name__)


class RecommendationEngineService:
    """Orchestrates Gemini MP decision recommendations with caching and persistence."""

    def __init__(
        self,
        complaint_repo: ComplaintRepository,
        cluster_repo: ClusterRepository,
        priority_portal: PriorityPortalService,
        analytics_service: AnalyticsIntelligenceService,
        gis_service: GisPortalService,
        engine_repo: RecommendationEngineRepository,
        context_builder: RecommendationContextBuilder,
        model: GenerativeModel,
        settings: Settings,
    ):
        self.complaint_repo = complaint_repo
        self.cluster_repo = cluster_repo
        self.priority_portal = priority_portal
        self.analytics_service = analytics_service
        self.gis_service = gis_service
        self.engine_repo = engine_repo
        self.context_builder = context_builder
        self.model = model
        self.settings = settings

    def _load_complaints(self):
        return self.complaint_repo.list(
            pagination=PaginationParams(limit=500, order_by="submitted_at", order_direction="desc"),
        ).items

    def _load_clusters(self):
        return self.cluster_repo.list(
            pagination=PaginationParams(limit=500, order_by="complaint_count", order_direction="desc"),
        ).items

    def build_context(self) -> RecommendationContext:
        complaints = self._load_complaints()
        clusters = self._load_clusters()
        return self.context_builder.build(
            complaints=complaints,
            clusters=clusters,
            priority_dashboard=self.priority_portal.get_dashboard(),
            analytics=self.analytics_service.get_intelligence(),
            gis_map=self.gis_service.get_map_data(),
        )

    def _heuristic_fallback(self, context: RecommendationContext) -> GeminiMpRecommendationOutput:
        """Deterministic recommendations when Gemini is unavailable."""
        items: list[MpDevelopmentWorkItem] = []
        clusters = context.payload.get("top_clusters", [])
        predictive = context.payload.get("predictive_analytics", [])
        for index, cluster in enumerate(clusters[:10], start=1):
            pred = predictive[index % len(predictive)] if predictive else {}
            items.append(
                MpDevelopmentWorkItem(
                    priority_rank=index,
                    project_title=cluster.get("title", f"Priority Work {index}"),
                    category="Infrastructure",
                    village=cluster.get("village") or "Constituency-wide",
                    department=cluster.get("department") or "Public Works Department",
                    reason=f"Cluster has {cluster.get('complaint_count', 0)} linked complaints with priority score {cluster.get('priority_score', 0)}.",
                    impact_score=min(100, int(cluster.get("priority_score", 50))),
                    priority_score=min(100, int(cluster.get("priority_score", 50))),
                    urgency=str(cluster.get("urgency") or "high"),
                    estimated_beneficiaries="500-2000 citizens",
                    estimated_budget="₹5-15 Lakhs",
                    estimated_resolution_time="30-60 days",
                    government_scheme="PMGSY / State Rural Development",
                    expected_social_impact="Improved daily mobility and access to services",
                    expected_infrastructure_improvement="Repair and upgrade of local civic infrastructure",
                    ai_confidence=0.72,
                    risk_if_ignored="Escalating citizen grievances and safety incidents",
                    executive_summary=pred.get("value", cluster.get("title", "")),
                    detailed_explanation=(
                        f"Address recurring complaints in {cluster.get('village', 'the area')} "
                        f"through coordinated departmental action."
                    ),
                    recommended_action="Convene department review meeting within 7 days",
                    cluster_id=cluster.get("id"),
                )
            )
        while len(items) < 10:
            rank = len(items) + 1
            items.append(
                MpDevelopmentWorkItem(
                    priority_rank=rank,
                    project_title=f"Constituency development initiative #{rank}",
                    category="Public Services",
                    village="Amethi",
                    department="District Administration",
                    reason="Derived from constituency analytics baseline.",
                    impact_score=40,
                    priority_score=40,
                    urgency="medium",
                    estimated_beneficiaries="200-500 citizens",
                    estimated_budget="₹2-5 Lakhs",
                    estimated_resolution_time="45 days",
                    government_scheme=None,
                    expected_social_impact="Improved service delivery",
                    expected_infrastructure_improvement="Operational capacity building",
                    ai_confidence=0.6,
                    risk_if_ignored="Continued service gaps",
                    executive_summary="Routine constituency development priority",
                    detailed_explanation="Heuristic recommendation from analytics when AI engine is offline.",
                    recommended_action="Review with constituency development officer",
                    cluster_id=None,
                )
            )
        return GeminiMpRecommendationOutput(
            executive_brief=(
                "Constituency intelligence indicates urgent focus on top complaint clusters, "
                "water and road infrastructure, and departmental coordination."
            ),
            decision_timeline_summary=(
                "Week 1: Review top 3 priorities. Week 2-3: Department site visits. "
                "Week 4: Progress review with district officials."
            ),
            recommendations=items,
        )

    def _generate_with_retries(self, prompt: str) -> GeminiMpRecommendationOutput:
        max_retries = max(1, self.settings.gemini_max_retries)
        last_error = "Unknown error"
        generation_config = genai.GenerationConfig(
            response_mime_type="application/json",
            temperature=0.2,
            top_p=0.9,
            max_output_tokens=8192,
        )

        for attempt in range(1, max_retries + 1):
            try:
                attempt_prompt = prompt if attempt == 1 else prompt + build_recommendation_retry_prompt(last_error)
                response = self.model.generate_content(attempt_prompt, generation_config=generation_config)
                raw_text = getattr(response, "text", None) or ""
                if not raw_text.strip():
                    raise RecommendationResponseParseError("Empty response from Gemini")
                return parse_recommendation_output(raw_text)
            except (RecommendationResponseParseError, ValueError, AttributeError) as exc:
                last_error = str(exc)
                logger.warning("Recommendation parse attempt %s/%s failed: %s", attempt, max_retries, last_error)

        raise RecommendationResponseParseError(
            f"Failed after {max_retries} attempts: {last_error}"
        )

    def generate(self, *, force: bool = False) -> GeminiMpRecommendationOutput:
        if not self.settings.recommendation_engine_enabled:
            raise BadRequestError("Recommendation engine is disabled")

        context = self.build_context()
        if not force:
            cached = self.engine_repo.get_cached_output(context.context_hash)
            if cached is not None:
                logger.info("Using cached recommendation output for %s", context.context_hash)
                return cached

        started = time.perf_counter()
        model_version = get_configured_model_name() or self.settings.gemini_model

        try:
            if not self.settings.gemini_api_key:
                logger.warning("GEMINI_API_KEY missing — using heuristic recommendations")
                output = self._heuristic_fallback(context)
            else:
                prompt = build_recommendation_prompt(context)
                output = self._generate_with_retries(prompt)

            self.engine_repo.persist_engine_output(
                output,
                context_hash=context.context_hash,
                constituency=context.constituency,
                district=context.district,
                state=context.state,
                model_version=model_version,
            )
            elapsed_ms = int((time.perf_counter() - started) * 1000)
            logger.info(
                "Recommendation engine completed in %sms (%s items)",
                elapsed_ms,
                len(output.recommendations),
            )
            return output
        except Exception as exc:
            logger.exception("Recommendation engine failed")
            raise BadRequestError(f"Recommendation generation failed: {exc}") from exc

    def generate_safe(self, *, force: bool = False) -> GeminiMpRecommendationOutput | None:
        try:
            return self.generate(force=force)
        except Exception:
            logger.exception("Safe recommendation generation failed")
            return None
