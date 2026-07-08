"""Complaint service layer for citizen portal."""

from __future__ import annotations

import logging
import re

from app.core.config import Settings
from app.core.exceptions import BadRequestError, NotFoundError
from app.db.pagination import PaginationParams
from app.models.domain.complaint import ComplaintCreate, ComplaintResponse, ComplaintSearchFilters, ComplaintUpdate
from app.models.enums.common import AnalysisStatus, ComplaintCategory, ComplaintPriority, ComplaintStatus
from app.models.schemas.common import DocumentMetadataCreate, GeoLocation
from app.models.schemas.complaint_portal import (
    CitizenComplaintSubmit,
    CitizenComplaintUpdate,
    ComplaintAIAnalysisResponse,
    ComplaintCreateResponse,
    ComplaintDetailResponse,
    ComplaintImageAnalysisResponse,
    ComplaintListItem,
    ComplaintListResponse,
)
from app.repositories.category_repository import CategoryRepository
from app.repositories.complaint_repository import ComplaintRepository
from app.services.ai.complaint_ai_service import ComplaintAIService
from app.services.clustering.duplicate_detection_service import DuplicateDetectionService
from app.services.vision.image_vision_service import ImageVisionService

logger = logging.getLogger(__name__)

CITIZEN_ACTOR = "citizen_portal"

SLUG_TO_CATEGORY: dict[str, ComplaintCategory] = {
    "roads": ComplaintCategory.ROADS,
    "water": ComplaintCategory.WATER,
    "garbage": ComplaintCategory.GARBAGE,
    "street_lights": ComplaintCategory.STREET_LIGHTS,
    "drainage": ComplaintCategory.DRAINAGE,
    "healthcare": ComplaintCategory.HEALTH,
    "health": ComplaintCategory.HEALTH,
    "education": ComplaintCategory.EDUCATION,
    "public_transport": ComplaintCategory.PUBLIC_TRANSPORT,
    "environment": ComplaintCategory.ENVIRONMENT,
    "electricity": ComplaintCategory.ELECTRICITY,
    "sanitation": ComplaintCategory.SANITATION,
    "other": ComplaintCategory.OTHER,
}


def _strip_base64_prefix(data: str) -> str:
    if data.startswith("data:"):
        match = re.match(r"^data:[^;]+;base64,(.+)$", data, re.DOTALL)
        if match:
            return match.group(1)
    return data


def _to_ai_response(complaint: ComplaintResponse) -> ComplaintAIAnalysisResponse | None:
    if complaint.ai_analysis is None:
        return None
    return ComplaintAIAnalysisResponse.model_validate(complaint.ai_analysis.model_dump())


def _to_image_analysis_response(
    complaint: ComplaintResponse,
) -> ComplaintImageAnalysisResponse | None:
    if complaint.image_analysis is None:
        return None
    return ComplaintImageAnalysisResponse.model_validate(complaint.image_analysis.model_dump())


def _to_list_item(complaint: ComplaintResponse) -> ComplaintListItem:
    return ComplaintListItem(
        id=complaint.id,
        title=complaint.title,
        description=complaint.description,
        category_id=complaint.category_id or "",
        category_name=complaint.category_name or complaint.category.value.replace("_", " ").title(),
        category_slug=complaint.category_slug or complaint.category.value,
        status=complaint.status,
        priority=complaint.priority,
        address=complaint.location.address if complaint.location else None,
        landmark=complaint.landmark,
        is_anonymous=complaint.is_anonymous,
        citizen_name=None if complaint.is_anonymous else complaint.citizen_name,
        citizen_phone=None if complaint.is_anonymous else complaint.citizen_phone,
        has_image=bool(complaint.image_base64),
        has_audio=bool(complaint.audio_base64),
        submitted_at=complaint.submitted_at,
        constituency=complaint.constituency,
        analysis_status=complaint.analysis_status,
        has_ai_analysis=complaint.ai_analysis is not None,
        image_analysis_status=complaint.image_analysis_status,
        has_image_analysis=complaint.image_analysis is not None,
        cluster_id=complaint.cluster_id,
        is_duplicate=complaint.is_duplicate,
        duplicate_score=complaint.duplicate_score,
    )


def _to_detail(complaint: ComplaintResponse) -> ComplaintDetailResponse:
    return ComplaintDetailResponse(
        id=complaint.id,
        title=complaint.title,
        description=complaint.description,
        category_id=complaint.category_id or "",
        category_name=complaint.category_name or complaint.category.value.replace("_", " ").title(),
        category_slug=complaint.category_slug or complaint.category.value,
        status=complaint.status,
        priority=complaint.priority,
        location=complaint.location,
        landmark=complaint.landmark,
        image_base64=complaint.image_base64,
        image_mime_type=complaint.image_mime_type,
        audio_base64=complaint.audio_base64,
        audio_mime_type=complaint.audio_mime_type,
        audio_duration_seconds=complaint.audio_duration_seconds,
        is_anonymous=complaint.is_anonymous,
        citizen_name=None if complaint.is_anonymous else complaint.citizen_name,
        citizen_phone=None if complaint.is_anonymous else complaint.citizen_phone,
        citizen_email=complaint.citizen_email,
        constituency=complaint.constituency,
        district=complaint.district,
        state=complaint.state,
        village_name=complaint.village_name,
        submitted_at=complaint.submitted_at,
        resolved_at=complaint.resolved_at,
        metadata=complaint.metadata,
        ai_analysis=_to_ai_response(complaint),
        analysis_status=complaint.analysis_status,
        analysis_started_at=complaint.analysis_started_at,
        analysis_completed_at=complaint.analysis_completed_at,
        analysis_model_name=complaint.analysis_model_name,
        analysis_processing_time_ms=complaint.analysis_processing_time_ms,
        analysis_prompt_version=complaint.analysis_prompt_version,
        analysis_error_message=complaint.analysis_error_message,
        analysis_retry_count=complaint.analysis_retry_count,
        image_analysis=_to_image_analysis_response(complaint),
        image_analysis_status=complaint.image_analysis_status,
        vision_model=complaint.vision_model,
        vision_processing_time_ms=complaint.vision_processing_time_ms,
        vision_completed_at=complaint.vision_completed_at,
        vision_started_at=complaint.vision_started_at,
        vision_prompt_version=complaint.vision_prompt_version,
        vision_error_message=complaint.vision_error_message,
        vision_retry_count=complaint.vision_retry_count,
        cluster_id=complaint.cluster_id,
        is_duplicate=complaint.is_duplicate,
        duplicate_score=complaint.duplicate_score,
        duplicate_reason=complaint.duplicate_reason,
        duplicate_confidence=complaint.duplicate_confidence,
        matched_complaint_id=complaint.matched_complaint_id,
        matched_cluster_id=complaint.matched_cluster_id,
    )


class ComplaintService:
    """Business logic for citizen complaint operations."""

    def __init__(
        self,
        complaint_repo: ComplaintRepository,
        category_repo: CategoryRepository,
        ai_service: ComplaintAIService,
        vision_service: ImageVisionService,
        duplicate_service: DuplicateDetectionService,
        settings: Settings,
    ):
        self.complaint_repo = complaint_repo
        self.category_repo = category_repo
        self.ai_service = ai_service
        self.vision_service = vision_service
        self.duplicate_service = duplicate_service
        self.settings = settings

    def _resolve_category(self, category_id: str) -> tuple[ComplaintCategory, str, str]:
        category = self.category_repo.get_by_id(category_id)
        if category is None or not category.is_active:
            raise BadRequestError(f"Invalid or inactive category: {category_id}")

        mapped = SLUG_TO_CATEGORY.get(category.slug)
        if mapped is None:
            mapped = ComplaintCategory.OTHER

        return mapped, category.name, category.slug

    def create(self, payload: CitizenComplaintSubmit, citizen_email: str | None = None) -> ComplaintCreateResponse:
        """Submit a new citizen complaint and run Gemini analysis."""
        category_enum, category_name, category_slug = self._resolve_category(payload.category_id)

        image_base64 = None
        image_mime_type = None
        if payload.image:
            image_base64 = _strip_base64_prefix(payload.image.data)
            image_mime_type = payload.image.mime_type

        audio_base64 = None
        audio_mime_type = None
        audio_duration = payload.audio_duration_seconds
        if payload.audio:
            audio_base64 = _strip_base64_prefix(payload.audio.data)
            audio_mime_type = payload.audio.mime_type

        citizen_name = None if payload.is_anonymous else payload.contact_name
        citizen_phone = payload.mobile_number

        create_data = ComplaintCreate(
            title=payload.title,
            description=payload.description,
            category=category_enum,
            priority=ComplaintPriority.MEDIUM,
            village_id=payload.village_id,
            village_name=payload.village_name,
            constituency=payload.constituency,
            district=payload.district,
            state=payload.state,
            citizen_name=citizen_name,
            citizen_phone=citizen_phone,
            citizen_email=citizen_email,
            location=GeoLocation(
                latitude=payload.latitude,
                longitude=payload.longitude,
                address=payload.address,
            ),
            landmark=payload.landmark,
            category_id=payload.category_id,
            category_name=category_name,
            category_slug=category_slug,
            image_base64=image_base64,
            image_mime_type=image_mime_type,
            audio_base64=audio_base64,
            audio_mime_type=audio_mime_type,
            audio_duration_seconds=audio_duration,
            is_anonymous=payload.is_anonymous,
            status=ComplaintStatus.PENDING,
            metadata=DocumentMetadataCreate(created_by=CITIZEN_ACTOR, updated_by=CITIZEN_ACTOR),
        )

        complaint = self.complaint_repo.create(create_data)
        logger.info("Citizen complaint created: %s", complaint.id)

        if self.settings.ai_analysis_enabled:
            try:
                complaint = self.ai_service.analyze_if_needed(complaint.id)
            except Exception:
                logger.exception("Post-create AI analysis failed for %s", complaint.id)
                complaint = self.complaint_repo.get_by_id_or_raise(complaint.id)
        else:
            logger.info("AI analysis disabled — complaint %s stored without analysis", complaint.id)

        if self.settings.vision_analysis_enabled and image_base64 and image_mime_type:
            try:
                complaint = self.vision_service.analyze_if_needed(complaint.id)
            except Exception:
                logger.exception("Post-create vision analysis failed for %s", complaint.id)
                complaint = self.complaint_repo.get_by_id_or_raise(complaint.id)
        elif image_base64:
            logger.info(
                "Vision analysis disabled — complaint %s image stored without vision analysis",
                complaint.id,
            )

        if self.settings.clustering_enabled:
            try:
                complaint = self.duplicate_service.process_if_needed(complaint.id)
            except Exception:
                logger.exception("Post-create clustering failed for %s", complaint.id)
                complaint = self.complaint_repo.get_by_id_or_raise(complaint.id)
        else:
            logger.info("Clustering disabled — complaint %s stored without clustering", complaint.id)

        return ComplaintCreateResponse(complaint=_to_detail(complaint))

    def analyze_complaint(self, complaint_id: str, *, force: bool = False) -> ComplaintDetailResponse:
        """Trigger Gemini analysis for an existing complaint."""
        if not self.settings.ai_analysis_enabled:
            raise BadRequestError("AI analysis is disabled")
        updated = self.ai_service.analyze_complaint(complaint_id, force=force)
        return _to_detail(updated)

    def analyze_complaint_image(
        self,
        complaint_id: str,
        *,
        force: bool = False,
    ) -> ComplaintDetailResponse:
        """Trigger Gemini Vision analysis for a complaint image."""
        if not self.settings.vision_analysis_enabled:
            raise BadRequestError("Vision analysis is disabled")
        updated = self.vision_service.analyze_complaint_image(complaint_id, force=force)
        return _to_detail(updated)

    def list_complaints(
        self,
        *,
        page: int = 1,
        page_size: int = 10,
        search: str | None = None,
        category_id: str | None = None,
        status: ComplaintStatus | None = None,
        citizen_email: str | None = None,
    ) -> ComplaintListResponse:
        """List complaints with search, filters, and page-based pagination."""
        page = max(page, 1)
        page_size = min(max(page_size, 1), 100)

        filters = ComplaintSearchFilters(
            category_id=category_id,
            status=status,
            citizen_email=citizen_email,
        )

        fetch_limit = page * page_size
        pagination = PaginationParams(
            limit=fetch_limit,
            order_by="submitted_at",
            order_direction="desc",
        )

        if search and search.strip():
            result = self.complaint_repo.search(
                search.strip(),
                filters=filters,
                pagination=pagination,
            )
        else:
            result = self.complaint_repo.list(filters=filters, pagination=pagination)

        total = self.complaint_repo.count(filters=filters)
        start = (page - 1) * page_size
        end = start + page_size
        page_items = result.items[start:end]

        return ComplaintListResponse(
            items=[_to_list_item(item) for item in page_items],
            total=total,
            page=page,
            page_size=page_size,
            has_more=end < total,
        )

    def get_complaint(self, complaint_id: str) -> ComplaintDetailResponse:
        """Retrieve a single complaint by ID."""
        complaint = self.complaint_repo.get_by_id(complaint_id)
        if complaint is None:
            raise NotFoundError(f"Complaint '{complaint_id}' not found")
        return _to_detail(complaint)

    def update_complaint(
        self,
        complaint_id: str,
        payload: CitizenComplaintUpdate,
    ) -> ComplaintDetailResponse:
        """Update an existing complaint."""
        existing = self.complaint_repo.get_by_id(complaint_id)
        if existing is None:
            raise NotFoundError(f"Complaint '{complaint_id}' not found")

        update_fields: dict = {"updated_by": CITIZEN_ACTOR}

        if payload.title is not None:
            update_fields["title"] = payload.title
        if payload.description is not None:
            update_fields["description"] = payload.description
        if payload.landmark is not None:
            update_fields["landmark"] = payload.landmark
        if payload.status is not None:
            update_fields["status"] = payload.status

        if payload.category_id is not None:
            category_enum, category_name, category_slug = self._resolve_category(payload.category_id)
            update_fields["category"] = category_enum
            update_fields["category_id"] = payload.category_id
            update_fields["category_name"] = category_name
            update_fields["category_slug"] = category_slug

        if payload.latitude is not None and payload.longitude is not None:
            address = payload.address or (
                existing.location.address if existing.location else None
            )
            update_fields["location"] = GeoLocation(
                latitude=payload.latitude,
                longitude=payload.longitude,
                address=address,
            )
        elif payload.address is not None and existing.location:
            update_fields["location"] = GeoLocation(
                latitude=existing.location.latitude,
                longitude=existing.location.longitude,
                address=payload.address,
            )

        update_data = ComplaintUpdate(**update_fields)
        updated = self.complaint_repo.update(complaint_id, update_data)
        logger.info("Citizen complaint updated: %s", complaint_id)
        return _to_detail(updated)

    def delete_complaint(self, complaint_id: str) -> None:
        """Delete a complaint by ID."""
        deleted = self.complaint_repo.delete(complaint_id)
        if not deleted:
            raise NotFoundError(f"Complaint '{complaint_id}' not found")
        logger.info("Citizen complaint deleted: %s", complaint_id)
