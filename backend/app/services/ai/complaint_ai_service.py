"""Gemini-powered complaint analysis pipeline."""

from __future__ import annotations

import logging
import time
from typing import Any

import google.generativeai as genai
from google.generativeai import GenerativeModel

from app.core.config import Settings
from app.core.exceptions import NotFoundError
from app.models.domain.complaint import ComplaintAIAnalysis, ComplaintResponse, ComplaintUpdate
from app.models.enums.common import AnalysisStatus, ComplaintStatus
from app.models.schemas.ai_complaint_analysis import GeminiComplaintAnalysisOutput
from app.repositories.complaint_repository import ComplaintRepository
from app.services.ai.prompt_builder import build_complaint_analysis_prompt, build_retry_prompt
from app.services.ai.response_parser import (
    AIResponseParseError,
    map_priority_level,
    parse_gemini_output,
    to_complaint_ai_analysis,
)
from app.services.gemini import get_configured_model_name

logger = logging.getLogger(__name__)

AI_ACTOR = "civiclens-ai"


class ComplaintAIService:
    """Orchestrates Gemini analysis, validation, persistence, and retries."""

    def __init__(
        self,
        complaint_repo: ComplaintRepository,
        model: GenerativeModel,
        settings: Settings,
    ):
        self.complaint_repo = complaint_repo
        self.model = model
        self.settings = settings

    def _should_skip_analysis(
        self,
        complaint: ComplaintResponse,
        *,
        force: bool,
    ) -> bool:
        if force:
            return False
        if complaint.analysis_status == AnalysisStatus.COMPLETED and complaint.ai_analysis:
            logger.info("Skipping analysis for %s — already completed", complaint.id)
            return True
        if complaint.analysis_status == AnalysisStatus.PROCESSING:
            logger.info("Skipping analysis for %s — already processing", complaint.id)
            return True
        return False

    def _build_content_parts(self, complaint: ComplaintResponse, prompt: str) -> list[Any]:
        parts: list[Any] = [prompt]
        if complaint.image_base64 and complaint.image_mime_type:
            parts.append(
                {
                    "inline_data": {
                        "mime_type": complaint.image_mime_type,
                        "data": complaint.image_base64,
                    }
                }
            )
        if complaint.audio_base64 and complaint.audio_mime_type:
            parts.append(
                {
                    "inline_data": {
                        "mime_type": complaint.audio_mime_type,
                        "data": complaint.audio_base64,
                    }
                }
            )
        return parts

    def _generate_with_retries(self, complaint: ComplaintResponse) -> GeminiComplaintAnalysisOutput:
        prompt = build_complaint_analysis_prompt(complaint)
        parts = self._build_content_parts(complaint, prompt)
        max_retries = max(1, self.settings.gemini_max_retries)
        last_error = "Unknown error"

        generation_config = genai.GenerationConfig(
            response_mime_type="application/json",
            temperature=0.2,
            top_p=0.9,
            max_output_tokens=4096,
        )

        for attempt in range(1, max_retries + 1):
            try:
                attempt_parts = list(parts)
                if attempt > 1:
                    attempt_parts[0] = str(parts[0]) + build_retry_prompt(last_error)

                response = self.model.generate_content(
                    attempt_parts,
                    generation_config=generation_config,
                )
                raw_text = getattr(response, "text", None) or ""
                if not raw_text and response.candidates:
                    parts_text = []
                    for candidate in response.candidates:
                        content = getattr(candidate, "content", None)
                        if content and getattr(content, "parts", None):
                            for part in content.parts:
                                if hasattr(part, "text") and part.text:
                                    parts_text.append(part.text)
                    raw_text = "\n".join(parts_text)

                if not raw_text.strip():
                    raise AIResponseParseError("Empty response from Gemini")

                return parse_gemini_output(raw_text)
            except (AIResponseParseError, ValueError, AttributeError) as exc:
                last_error = str(exc)
                logger.warning(
                    "Gemini parse attempt %s/%s failed for complaint context: %s",
                    attempt,
                    max_retries,
                    last_error,
                )

        raise AIResponseParseError(
            f"Failed to obtain valid JSON after {max_retries} attempts: {last_error}"
        )

    def _mark_processing(self, complaint: ComplaintResponse) -> ComplaintResponse:
        from datetime import UTC, datetime

        return self.complaint_repo.update(
            complaint.id,
            ComplaintUpdate(
                analysis_status=AnalysisStatus.PROCESSING,
                analysis_started_at=datetime.now(UTC),
                analysis_error_message=None,
                analysis_retry_count=(complaint.analysis_retry_count or 0) + 1,
                updated_by=AI_ACTOR,
            ),
        )

    def _mark_failed(self, complaint_id: str, error_message: str) -> ComplaintResponse:
        from datetime import UTC, datetime

        return self.complaint_repo.update(
            complaint_id,
            ComplaintUpdate(
                analysis_status=AnalysisStatus.FAILED,
                analysis_completed_at=datetime.now(UTC),
                analysis_error_message=error_message[:2000],
                updated_by=AI_ACTOR,
            ),
        )

    def _persist_success(
        self,
        complaint_id: str,
        analysis: ComplaintAIAnalysis,
        *,
        processing_time_ms: int,
    ) -> ComplaintResponse:
        from datetime import UTC, datetime

        priority = map_priority_level(analysis.priority_level)
        return self.complaint_repo.update(
            complaint_id,
            ComplaintUpdate(
                ai_analysis=analysis,
                analysis_status=AnalysisStatus.COMPLETED,
                analysis_completed_at=datetime.now(UTC),
                analysis_model_name=get_configured_model_name() or self.settings.gemini_model,
                analysis_processing_time_ms=processing_time_ms,
                analysis_prompt_version=self.settings.gemini_prompt_version,
                analysis_error_message=None,
                priority=priority,
                status=ComplaintStatus.UNDER_REVIEW,
                updated_by=AI_ACTOR,
            ),
        )

    def analyze_complaint(
        self,
        complaint_id: str,
        *,
        force: bool = False,
    ) -> ComplaintResponse:
        """Run Gemini analysis for a complaint and persist structured intelligence."""
        if not self.settings.ai_analysis_enabled:
            raise ValueError("AI analysis is disabled")

        complaint = self.complaint_repo.get_by_id_or_raise(complaint_id)

        if self._should_skip_analysis(complaint, force=force):
            return complaint

        started = time.perf_counter()
        complaint = self._mark_processing(complaint)
        logger.info("AI analysis started for complaint %s", complaint_id)

        try:
            gemini_output = self._generate_with_retries(complaint)
            analysis = to_complaint_ai_analysis(
                gemini_output,
                model_version=get_configured_model_name() or self.settings.gemini_model,
                prompt_version=self.settings.gemini_prompt_version,
            )
            elapsed_ms = int((time.perf_counter() - started) * 1000)
            updated = self._persist_success(complaint_id, analysis, processing_time_ms=elapsed_ms)
            logger.info(
                "AI analysis completed for complaint %s in %sms (confidence=%.2f)",
                complaint_id,
                elapsed_ms,
                analysis.confidence_score,
            )
            return updated
        except Exception as exc:
            logger.exception("AI analysis failed for complaint %s", complaint_id)
            err_msg = str(exc)
            if "ResourceExhausted" in err_msg or "429" in err_msg or "quota" in err_msg.lower():
                err_msg = "API key error"
            return self._mark_failed(complaint_id, err_msg)

    def analyze_if_needed(self, complaint_id: str) -> ComplaintResponse:
        """Analyze complaint only when not already completed."""
        complaint = self.complaint_repo.get_by_id(complaint_id)
        if complaint is None:
            raise NotFoundError(f"Complaint '{complaint_id}' not found")
        if complaint.analysis_status == AnalysisStatus.COMPLETED and complaint.ai_analysis:
            return complaint
        return self.analyze_complaint(complaint_id, force=False)
