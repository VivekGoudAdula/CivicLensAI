"""Gemini-powered duplicate detection and cluster assignment orchestration."""

from __future__ import annotations

import logging
import time

import google.generativeai as genai
from google.generativeai import GenerativeModel

from app.core.config import Settings
from app.core.exceptions import BadRequestError, NotFoundError
from app.models.domain.complaint import ComplaintResponse, ComplaintUpdate
from app.models.enums.common import AnalysisStatus
from app.models.schemas.ai_duplicate_matching import GeminiDuplicateMatchOutput
from app.repositories.complaint_repository import ComplaintRepository
from app.services.clustering.cluster_service import ClusterService
from app.services.clustering.matching_prompt_builder import (
    build_duplicate_matching_prompt,
    build_matching_retry_prompt,
)
from app.services.clustering.matching_response_parser import (
    DuplicateMatchParseError,
    parse_duplicate_match_output,
)
from app.services.clustering.similarity_engine import (
    CandidateScore,
    ComparisonCache,
    SimilarityEngine,
    get_comparison_cache,
)
from app.services.gemini import get_configured_model_name

logger = logging.getLogger(__name__)

CLUSTERING_ACTOR = "civiclens-clustering"


class DuplicateDetectionService:
    """Detect duplicates via heuristic filtering and Gemini matching."""

    def __init__(
        self,
        complaint_repo: ComplaintRepository,
        cluster_service: ClusterService,
        similarity_engine: SimilarityEngine,
        model: GenerativeModel,
        settings: Settings,
        cache: ComparisonCache | None = None,
    ):
        self.complaint_repo = complaint_repo
        self.cluster_service = cluster_service
        self.similarity_engine = similarity_engine
        self.model = model
        self.settings = settings
        self.cache = cache or get_comparison_cache()

    def _analysis_ready(self, complaint: ComplaintResponse) -> bool:
        if complaint.analysis_status != AnalysisStatus.COMPLETED or not complaint.ai_analysis:
            return False
        if complaint.image_base64 and complaint.image_mime_type:
            if complaint.image_analysis_status not in {
                AnalysisStatus.COMPLETED,
                AnalysisStatus.FAILED,
            }:
                return False
        return True

    def _should_skip(self, complaint: ComplaintResponse, *, force: bool) -> bool:
        if force:
            return False
        if complaint.cluster_id:
            logger.info(
                "Skipping clustering for %s — already assigned to %s",
                complaint.id,
                complaint.cluster_id,
            )
            return True
        return False

    def _cache_key(self, source_id: str, candidate_ids: list[str]) -> str:
        return f"{source_id}::{'|'.join(sorted(candidate_ids))}"

    def _generate_match(
        self,
        source: ComplaintResponse,
        candidates: list[CandidateScore],
    ) -> GeminiDuplicateMatchOutput:
        candidate_ids = [item.complaint.id for item in candidates]
        cache_key = self._cache_key(source.id, candidate_ids)
        cached = self.cache.get(cache_key)
        if isinstance(cached, GeminiDuplicateMatchOutput):
            logger.info("Using cached duplicate match for complaint %s", source.id)
            return cached

        prompt = build_duplicate_matching_prompt(source, candidates)
        max_retries = max(1, self.settings.gemini_max_retries)
        last_error = "Unknown error"

        generation_config = genai.GenerationConfig(
            response_mime_type="application/json",
            temperature=0.1,
            top_p=0.85,
            max_output_tokens=2048,
        )

        for attempt in range(1, max_retries + 1):
            try:
                attempt_prompt = prompt
                if attempt > 1:
                    attempt_prompt = prompt + build_matching_retry_prompt(last_error)

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
                    raise DuplicateMatchParseError("Empty response from Gemini")

                parsed = parse_duplicate_match_output(raw_text)
                self.cache.set(cache_key, parsed)
                return parsed
            except (DuplicateMatchParseError, ValueError, AttributeError) as exc:
                last_error = str(exc)
                logger.warning(
                    "Duplicate match parse attempt %s/%s failed: %s",
                    attempt,
                    max_retries,
                    last_error,
                )

        raise DuplicateMatchParseError(
            f"Failed to obtain valid JSON after {max_retries} attempts: {last_error}"
        )

    def _resolve_target_cluster(
        self,
        match: GeminiDuplicateMatchOutput,
        candidates: list[CandidateScore],
    ) -> tuple[str | None, str | None]:
        if match.existing_cluster_id:
            return match.existing_cluster_id, match.matched_complaint_id

        if match.matched_complaint_id:
            for item in candidates:
                if item.complaint.id == match.matched_complaint_id and item.complaint.cluster_id:
                    return item.complaint.cluster_id, match.matched_complaint_id
            return None, match.matched_complaint_id

        return None, None

    def _persist_match_metadata(
        self,
        complaint_id: str,
        match: GeminiDuplicateMatchOutput,
        *,
        is_duplicate: bool,
        cluster_id: str | None = None,
        matched_complaint_id: str | None = None,
    ) -> ComplaintResponse:
        return self.complaint_repo.update(
            complaint_id,
            ComplaintUpdate(
                is_duplicate=is_duplicate,
                duplicate_score=float(match.similarity_score),
                duplicate_reason=match.matching_reason if is_duplicate else match.explanation,
                duplicate_confidence=match.confidence,
                matched_complaint_id=matched_complaint_id or match.matched_complaint_id,
                matched_cluster_id=cluster_id or match.existing_cluster_id,
                updated_by=CLUSTERING_ACTOR,
            ),
        )

    def process_complaint(
        self,
        complaint_id: str,
        *,
        force: bool = False,
    ) -> ComplaintResponse:
        """Run duplicate detection and cluster assignment for a complaint."""
        if not self.settings.clustering_enabled:
            raise BadRequestError("Clustering is disabled")

        complaint = self.complaint_repo.get_by_id_or_raise(complaint_id)

        if self._should_skip(complaint, force=force):
            return complaint

        if not self._analysis_ready(complaint):
            raise BadRequestError(
                "Complaint AI analysis must complete before clustering"
            )

        started = time.perf_counter()
        logger.info("Clustering started for complaint %s", complaint_id)

        candidates = self.similarity_engine.find_candidates(complaint)

        if not candidates:
            self.cluster_service.create_cluster_for_complaint(complaint)
            elapsed_ms = int((time.perf_counter() - started) * 1000)
            logger.info(
                "No candidates — created new cluster for %s in %sms",
                complaint_id,
                elapsed_ms,
            )
            return self.complaint_repo.get_by_id_or_raise(complaint_id)

        try:
            match = self._generate_match(complaint, candidates)
        except DuplicateMatchParseError as exc:
            logger.exception("Gemini duplicate matching failed for %s", complaint_id)
            self.cluster_service.create_cluster_for_complaint(complaint)
            return self.complaint_repo.update(
                complaint_id,
                ComplaintUpdate(
                    duplicate_reason=f"Clustering fallback after AI error: {exc}",
                    updated_by=CLUSTERING_ACTOR,
                ),
            )

        is_duplicate = (
            match.is_duplicate
            and match.similarity_score >= self.settings.clustering_duplicate_threshold
        )
        cluster_id, matched_complaint_id = self._resolve_target_cluster(match, candidates)

        if is_duplicate and cluster_id:
            self.cluster_service.assign_complaint_to_cluster(
                complaint,
                cluster_id,
                is_duplicate=True,
                duplicate_score=float(match.similarity_score),
                duplicate_reason=match.matching_reason,
                duplicate_confidence=match.confidence,
                matched_complaint_id=matched_complaint_id,
                matched_cluster_id=match.existing_cluster_id or cluster_id,
            )
        elif is_duplicate and matched_complaint_id:
            matched = self.complaint_repo.get_by_id(matched_complaint_id)
            if matched and matched.cluster_id:
                self.cluster_service.assign_complaint_to_cluster(
                    complaint,
                    matched.cluster_id,
                    is_duplicate=True,
                    duplicate_score=float(match.similarity_score),
                    duplicate_reason=match.matching_reason,
                    duplicate_confidence=match.confidence,
                    matched_complaint_id=matched_complaint_id,
                    matched_cluster_id=matched.cluster_id,
                )
            else:
                cluster = self.cluster_service.create_cluster_for_complaint(complaint)
                if matched and not matched.cluster_id:
                    self.cluster_service.assign_complaint_to_cluster(
                        matched,
                        cluster.id,
                        is_duplicate=False,
                        duplicate_score=0.0,
                        duplicate_reason="Linked during duplicate cluster formation",
                        duplicate_confidence=match.confidence,
                        matched_complaint_id=complaint.id,
                        matched_cluster_id=cluster.id,
                    )
                self._persist_match_metadata(
                    complaint.id,
                    match,
                    is_duplicate=True,
                    cluster_id=cluster.id,
                    matched_complaint_id=matched_complaint_id,
                )
        else:
            self.cluster_service.create_cluster_for_complaint(complaint)
            self._persist_match_metadata(complaint.id, match, is_duplicate=False)

        elapsed_ms = int((time.perf_counter() - started) * 1000)
        logger.info(
            "Clustering completed for %s in %sms (duplicate=%s, score=%s, model=%s)",
            complaint_id,
            elapsed_ms,
            is_duplicate,
            match.similarity_score,
            get_configured_model_name() or self.settings.gemini_model,
        )
        return self.complaint_repo.get_by_id_or_raise(complaint_id)

    def process_if_needed(self, complaint_id: str) -> ComplaintResponse:
        """Cluster complaint when analysis is ready and not yet assigned."""
        complaint = self.complaint_repo.get_by_id(complaint_id)
        if complaint is None:
            raise NotFoundError(f"Complaint '{complaint_id}' not found")
        if complaint.cluster_id:
            return complaint
        if not self._analysis_ready(complaint):
            return complaint
        return self.process_complaint(complaint_id, force=False)
