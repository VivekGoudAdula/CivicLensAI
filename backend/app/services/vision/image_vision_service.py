"""Gemini Vision civic image intelligence pipeline."""

from __future__ import annotations

import logging
import time
from datetime import UTC, datetime
from typing import Any

import google.generativeai as genai
from google.generativeai import GenerativeModel

from app.core.config import Settings
from app.core.exceptions import BadRequestError, NotFoundError
from app.models.domain.complaint import ComplaintImageAnalysis, ComplaintResponse, ComplaintUpdate
from app.models.enums.common import AnalysisStatus
from app.models.schemas.ai_image_analysis import GeminiImageAnalysisOutput
from app.repositories.complaint_repository import ComplaintRepository
from app.services.gemini import get_configured_model_name
from app.services.vision.image_processor import ImageProcessingError, compress_image_base64
from app.services.vision.vision_prompt_builder import (
    VISION_PROMPT_VERSION,
    build_vision_analysis_prompt,
    build_vision_retry_prompt,
)
from app.services.vision.vision_response_parser import (
    VisionResponseParseError,
    parse_vision_output,
    to_complaint_image_analysis,
)

logger = logging.getLogger(__name__)

VISION_ACTOR = "civiclens-vision"


class ImageVisionService:
    """Orchestrates Gemini Vision analysis, validation, persistence, and retries."""

    def __init__(
        self,
        complaint_repo: ComplaintRepository,
        model: GenerativeModel,
        settings: Settings,
    ):
        self.complaint_repo = complaint_repo
        self.model = model
        self.settings = settings

    def _has_analyzable_image(self, complaint: ComplaintResponse) -> bool:
        return bool(complaint.image_base64 and complaint.image_mime_type)

    def _should_skip_analysis(
        self,
        complaint: ComplaintResponse,
        *,
        force: bool,
    ) -> bool:
        if not self._has_analyzable_image(complaint):
            logger.info("Skipping vision analysis for %s — no image", complaint.id)
            return True
        if force:
            return False
        if complaint.image_analysis_status == AnalysisStatus.COMPLETED and complaint.image_analysis:
            logger.info("Skipping vision analysis for %s — already completed", complaint.id)
            return True
        if complaint.image_analysis_status == AnalysisStatus.PROCESSING:
            logger.info("Skipping vision analysis for %s — already processing", complaint.id)
            return True
        return False

    def _prepare_image(self, complaint: ComplaintResponse) -> tuple[str, str]:
        assert complaint.image_base64 is not None
        assert complaint.image_mime_type is not None
        processed = compress_image_base64(
            complaint.image_base64,
            complaint.image_mime_type,
            max_dimension=self.settings.vision_max_image_dimension,
            jpeg_quality=self.settings.vision_jpeg_quality,
        )
        return processed.data_base64, processed.mime_type

    def _build_content_parts(
        self,
        complaint: ComplaintResponse,
        prompt: str,
        image_base64: str,
        image_mime_type: str,
    ) -> list[Any]:
        return [
            prompt,
            {
                "inline_data": {
                    "mime_type": image_mime_type,
                    "data": image_base64,
                }
            },
        ]

    def _generate_with_retries(
        self,
        complaint: ComplaintResponse,
        image_base64: str,
        image_mime_type: str,
    ) -> GeminiImageAnalysisOutput:
        prompt = build_vision_analysis_prompt(complaint)
        parts = self._build_content_parts(complaint, prompt, image_base64, image_mime_type)
        max_retries = max(1, self.settings.gemini_max_retries)
        last_error = "Unknown error"

        generation_config = genai.GenerationConfig(
            response_mime_type="application/json",
            temperature=0.1,
            top_p=0.85,
            max_output_tokens=4096,
        )

        for attempt in range(1, max_retries + 1):
            try:
                attempt_parts = list(parts)
                if attempt > 1:
                    attempt_parts[0] = str(parts[0]) + build_vision_retry_prompt(last_error)

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
                    raise VisionResponseParseError("Empty response from Gemini Vision")

                return parse_vision_output(raw_text)
            except (VisionResponseParseError, ValueError, AttributeError) as exc:
                last_error = str(exc)
                logger.warning(
                    "Gemini Vision parse attempt %s/%s failed: %s",
                    attempt,
                    max_retries,
                    last_error,
                )

        raise VisionResponseParseError(
            f"Failed to obtain valid JSON after {max_retries} attempts: {last_error}"
        )

    def _mark_processing(self, complaint: ComplaintResponse) -> ComplaintResponse:
        return self.complaint_repo.update(
            complaint.id,
            ComplaintUpdate(
                image_analysis_status=AnalysisStatus.PROCESSING,
                vision_started_at=datetime.now(UTC),
                vision_error_message=None,
                vision_retry_count=(complaint.vision_retry_count or 0) + 1,
                updated_by=VISION_ACTOR,
            ),
        )

    def _mark_failed(self, complaint_id: str, error_message: str) -> ComplaintResponse:
        return self.complaint_repo.update(
            complaint_id,
            ComplaintUpdate(
                image_analysis_status=AnalysisStatus.FAILED,
                vision_completed_at=datetime.now(UTC),
                vision_error_message=error_message[:2000],
                updated_by=VISION_ACTOR,
            ),
        )

    def _persist_success(
        self,
        complaint_id: str,
        analysis: ComplaintImageAnalysis,
        *,
        processing_time_ms: int,
    ) -> ComplaintResponse:
        model_name = get_configured_model_name() or self.settings.gemini_model
        return self.complaint_repo.update(
            complaint_id,
            ComplaintUpdate(
                image_analysis=analysis,
                image_analysis_status=AnalysisStatus.COMPLETED,
                vision_model=model_name,
                vision_processing_time_ms=processing_time_ms,
                vision_completed_at=datetime.now(UTC),
                vision_prompt_version=self.settings.vision_prompt_version,
                vision_error_message=None,
                updated_by=VISION_ACTOR,
            ),
        )

    def analyze_complaint_image(
        self,
        complaint_id: str,
        *,
        force: bool = False,
    ) -> ComplaintResponse:
        """Run Gemini Vision analysis for a complaint image and persist results."""
        if not self.settings.vision_analysis_enabled:
            raise BadRequestError("Vision analysis is disabled")

        complaint = self.complaint_repo.get_by_id_or_raise(complaint_id)

        if not self._has_analyzable_image(complaint):
            raise BadRequestError("Complaint has no image to analyze")

        if self._should_skip_analysis(complaint, force=force):
            return complaint

        started = time.perf_counter()
        complaint = self._mark_processing(complaint)
        logger.info("Vision analysis started for complaint %s", complaint_id)

        try:
            image_base64, image_mime_type = self._prepare_image(complaint)
            gemini_output = self._generate_with_retries(complaint, image_base64, image_mime_type)
            analysis = to_complaint_image_analysis(
                gemini_output,
                model_version=get_configured_model_name() or self.settings.gemini_model,
                prompt_version=self.settings.vision_prompt_version,
            )
            elapsed_ms = int((time.perf_counter() - started) * 1000)
            updated = self._persist_success(complaint_id, analysis, processing_time_ms=elapsed_ms)
            logger.info(
                "Vision analysis completed for complaint %s in %sms "
                "(primary_issue=%s, confidence=%.2f, urgent=%s)",
                complaint_id,
                elapsed_ms,
                analysis.primary_issue,
                analysis.confidence_score,
                analysis.requires_urgent_attention,
            )
            return updated
        except ImageProcessingError as exc:
            logger.exception("Image preprocessing failed for complaint %s", complaint_id)
            return self._mark_failed(complaint_id, str(exc))
        except Exception as exc:
            logger.exception("Vision analysis failed for complaint %s", complaint_id)
            err_msg = str(exc)
            if "ResourceExhausted" in err_msg or "429" in err_msg or "quota" in err_msg.lower():
                err_msg = "API key error"
            return self._mark_failed(complaint_id, err_msg)

    def analyze_if_needed(self, complaint_id: str) -> ComplaintResponse:
        """Analyze complaint image only when not already completed."""
        complaint = self.complaint_repo.get_by_id(complaint_id)
        if complaint is None:
            raise NotFoundError(f"Complaint '{complaint_id}' not found")
        if not self._has_analyzable_image(complaint):
            return complaint
        if complaint.image_analysis_status == AnalysisStatus.COMPLETED and complaint.image_analysis:
            return complaint
        return self.analyze_complaint_image(complaint_id, force=False)
