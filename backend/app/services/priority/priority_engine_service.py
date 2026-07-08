"""Gemini-powered cluster priority engine."""

from __future__ import annotations

import logging
import time
from datetime import UTC, datetime

import google.generativeai as genai
from google.generativeai import GenerativeModel

from app.core.config import Settings
from app.core.exceptions import BadRequestError, NotFoundError
from app.models.domain.cluster import ClusterPriorityAnalysis, ClusterResponse
from app.models.schemas.ai_cluster_priority import GeminiClusterPriorityOutput
from app.services.priority.priority_repository import PriorityRepository
from app.services.gemini import get_configured_model_name
from app.services.priority.priority_calculator import PriorityCalculator
from app.services.priority.priority_prompt_builder import (
    PRIORITY_PROMPT_VERSION,
    build_priority_analysis_prompt,
    build_priority_retry_prompt,
)
from app.services.priority.priority_response_parser import (
    PriorityResponseParseError,
    parse_priority_output,
    to_cluster_priority_analysis,
)

logger = logging.getLogger(__name__)

PRIORITY_ENGINE_ACTOR = "civiclens-priority-engine"


class PriorityAnalysisCache:
    """In-memory cache for recent priority analyses."""

    def __init__(self, ttl_seconds: int = 3600) -> None:
        self._ttl = ttl_seconds
        self._store: dict[str, tuple[float, ClusterPriorityAnalysis]] = {}

    def get(self, cluster_id: str, analysis_hash: str) -> ClusterPriorityAnalysis | None:
        key = f"{cluster_id}:{analysis_hash}"
        entry = self._store.get(key)
        if entry is None:
            return None
        expires_at, value = entry
        if time.time() > expires_at:
            del self._store[key]
            return None
        return value

    def set(self, cluster_id: str, analysis: ClusterPriorityAnalysis) -> None:
        key = f"{cluster_id}:{analysis.analysis_hash}"
        self._store[key] = (time.time() + self._ttl, analysis)


_priority_cache = PriorityAnalysisCache()


class PriorityEngineService:
    """Orchestrates Gemini priority analysis, validation, ranking, and persistence."""

    def __init__(
        self,
        priority_repo: PriorityRepository,
        calculator: PriorityCalculator,
        model: GenerativeModel,
        settings: Settings,
        cache: PriorityAnalysisCache | None = None,
    ):
        self.priority_repo = priority_repo
        self.calculator = calculator
        self.model = model
        self.settings = settings
        self.cache = cache or _priority_cache

    def _should_skip(self, cluster: ClusterResponse, analysis_hash: str, *, force: bool) -> bool:
        if force:
            return False
        if cluster.priority_analysis_hash == analysis_hash and cluster.priority_analysis:
            logger.info("Skipping priority analysis for %s — hash unchanged", cluster.id)
            return True
        return False

    def _generate_with_retries(self, prompt: str) -> GeminiClusterPriorityOutput:
        max_retries = max(1, self.settings.gemini_max_retries)
        last_error = "Unknown error"

        generation_config = genai.GenerationConfig(
            response_mime_type="application/json",
            temperature=0.15,
            top_p=0.85,
            max_output_tokens=4096,
        )

        for attempt in range(1, max_retries + 1):
            try:
                attempt_prompt = prompt
                if attempt > 1:
                    attempt_prompt = prompt + build_priority_retry_prompt(last_error)

                response = self.model.generate_content(
                    attempt_prompt,
                    generation_config=generation_config,
                )
                raw_text = getattr(response, "text", None) or ""
                if not raw_text and response.candidates:
                    parts_text: list[str] = []
                    for candidate in response.candidates:
                        content = getattr(candidate, "content", None)
                        if content and getattr(content, "parts", None):
                            for part in content.parts:
                                if hasattr(part, "text") and part.text:
                                    parts_text.append(part.text)
                    raw_text = "\n".join(parts_text)

                if not raw_text.strip():
                    raise PriorityResponseParseError("Empty response from Gemini")

                return parse_priority_output(raw_text)
            except (PriorityResponseParseError, ValueError, AttributeError) as exc:
                last_error = str(exc)
                logger.warning(
                    "Priority parse attempt %s/%s failed: %s",
                    attempt,
                    max_retries,
                    last_error,
                )

        raise PriorityResponseParseError(
            f"Failed to obtain valid JSON after {max_retries} attempts: {last_error}"
        )

    def recalculate_global_ranks(self) -> int:
        """Assign priority_rank across all analyzed clusters."""
        ranked = self.priority_repo.list_ranked_clusters(limit=self.settings.priority_ranking_limit)
        for index, cluster in enumerate(ranked, start=1):
            if cluster.priority_rank != index:
                self.priority_repo.update_cluster_rank(cluster.id, index)
        logger.info("Recalculated priority ranks for %s clusters", len(ranked))
        return len(ranked)

    def analyze_cluster(
        self,
        cluster_id: str,
        *,
        force: bool = False,
        recalculate_ranks: bool = True,
    ) -> ClusterResponse:
        """Run Gemini priority analysis for a cluster."""
        if not self.settings.priority_engine_enabled:
            raise BadRequestError("Priority engine is disabled")

        cluster = self.priority_repo.get_cluster(cluster_id)
        complaints = self.priority_repo.get_cluster_complaints(cluster)
        if not complaints:
            raise BadRequestError(f"Cluster '{cluster_id}' has no linked complaints")

        context = self.calculator.build_context(cluster, complaints)

        if self._should_skip(cluster, context.analysis_hash, force=force):
            return cluster

        cached = self.cache.get(cluster.id, context.analysis_hash)
        if cached is not None and not force:
            logger.info("Using in-memory cached priority analysis for %s", cluster.id)
            updated = self.priority_repo.persist_priority_analysis(cluster.id, cached)
            if recalculate_ranks:
                self.recalculate_global_ranks()
                updated = self.priority_repo.get_cluster(cluster_id)
            return updated

        started = time.perf_counter()
        logger.info("Priority analysis started for cluster %s", cluster_id)

        try:
            prompt = build_priority_analysis_prompt(context)
            gemini_output = self._generate_with_retries(prompt)
            analysis = to_cluster_priority_analysis(
                gemini_output,
                analysis_hash=context.analysis_hash,
                model_version=get_configured_model_name() or self.settings.gemini_model,
                prompt_version=self.settings.priority_prompt_version,
            )
            self.cache.set(cluster.id, analysis)
            updated = self.priority_repo.persist_priority_analysis(cluster.id, analysis)
            elapsed_ms = int((time.perf_counter() - started) * 1000)
            logger.info(
                "Priority analysis completed for cluster %s in %sms (score=%s, impact=%s)",
                cluster_id,
                elapsed_ms,
                analysis.priority_score,
                analysis.impact_score,
            )
            if recalculate_ranks:
                self.recalculate_global_ranks()
                updated = self.priority_repo.get_cluster(cluster_id)
            return updated
        except Exception as exc:
            logger.exception("Priority analysis failed for cluster %s", cluster_id)
            raise BadRequestError(f"Priority analysis failed: {exc}") from exc

    def analyze_if_needed(
        self,
        cluster_id: str,
        *,
        recalculate_ranks: bool = True,
    ) -> ClusterResponse:
        """Analyze cluster priority only when data has changed."""
        cluster = self.priority_repo.get_cluster(cluster_id)
        complaints = self.priority_repo.get_cluster_complaints(cluster)
        if not complaints:
            return cluster
        context = self.calculator.build_context(cluster, complaints)
        if cluster.priority_analysis_hash == context.analysis_hash and cluster.priority_analysis:
            return cluster
        return self.analyze_cluster(
            cluster_id,
            force=False,
            recalculate_ranks=recalculate_ranks,
        )

    def analyze_if_needed_safe(self, cluster_id: str) -> ClusterResponse | None:
        """Non-fatal priority analysis for pipeline hooks."""
        if not self.settings.priority_engine_enabled:
            return None
        try:
            return self.analyze_if_needed(cluster_id)
        except Exception:
            logger.exception("Priority analysis hook failed for cluster %s", cluster_id)
            return None
