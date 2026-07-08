"""Complaint REST API endpoints for citizen portal."""

from __future__ import annotations

import logging
from typing import Annotated

from fastapi import APIRouter, Depends, Query, status

from app.api.clustering_deps import DuplicateDetectionServiceDep
from app.api.deps import GeminiDep, SettingsDep, get_current_user_email
from app.api.repository_deps import CategoryRepoDep, ComplaintRepoDep
from app.core.exceptions import BadRequestError
from app.models.enums.common import ComplaintStatus
from app.models.schemas.cluster_portal import ClusterProcessResponse
from app.models.schemas.complaint_portal import (
    CitizenComplaintSubmit,
    CitizenComplaintUpdate,
    ComplaintAIAnalysisResponse,
    ComplaintAnalyzeResponse,
    ComplaintCreateResponse,
    ComplaintDetailResponse,
    ComplaintImageAnalyzeResponse,
    ComplaintListResponse,
)
from app.services.ai.complaint_ai_service import ComplaintAIService
from app.services.complaint_service import ComplaintService
from app.services.vision.image_vision_service import ImageVisionService

logger = logging.getLogger(__name__)

router = APIRouter()


def get_complaint_ai_service(
    complaint_repo: ComplaintRepoDep,
    model: GeminiDep,
    settings: SettingsDep,
) -> ComplaintAIService:
    return ComplaintAIService(complaint_repo, model, settings)


def get_image_vision_service(
    complaint_repo: ComplaintRepoDep,
    model: GeminiDep,
    settings: SettingsDep,
) -> ImageVisionService:
    return ImageVisionService(complaint_repo, model, settings)


def get_complaint_service(
    complaint_repo: ComplaintRepoDep,
    category_repo: CategoryRepoDep,
    ai_service: Annotated[ComplaintAIService, Depends(get_complaint_ai_service)],
    vision_service: Annotated[ImageVisionService, Depends(get_image_vision_service)],
    duplicate_service: DuplicateDetectionServiceDep,
    settings: SettingsDep,
) -> ComplaintService:
    return ComplaintService(
        complaint_repo,
        category_repo,
        ai_service,
        vision_service,
        duplicate_service,
        settings,
    )


ComplaintAIServiceDep = Annotated[ComplaintAIService, Depends(get_complaint_ai_service)]
ComplaintServiceDep = Annotated[ComplaintService, Depends(get_complaint_service)]


@router.post(
    "",
    response_model=ComplaintCreateResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Submit a new complaint",
)
async def create_complaint(
    payload: CitizenComplaintSubmit,
    service: ComplaintServiceDep,
    current_user_email: str | None = Depends(get_current_user_email),
) -> ComplaintCreateResponse:
    """Create a new citizen complaint."""
    logger.info("Creating complaint: %s", payload.title)
    return service.create(payload, citizen_email=current_user_email)


@router.get(
    "",
    response_model=ComplaintListResponse,
    summary="List complaints",
)
async def list_complaints(
    service: ComplaintServiceDep,
    settings: SettingsDep,
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=10, ge=1, le=100),
    search: str | None = Query(default=None, max_length=128),
    category_id: str | None = Query(default=None),
    status: ComplaintStatus | None = Query(default=None),
    current_user_email: str | None = Depends(get_current_user_email),
) -> ComplaintListResponse:
    """List complaints with optional search and filters."""
    filter_email = None
    if current_user_email and current_user_email != settings.admin_email:
        filter_email = current_user_email

    return service.list_complaints(
        page=page,
        page_size=page_size,
        search=search,
        category_id=category_id,
        status=status,
        citizen_email=filter_email,
    )


@router.get(
    "/{complaint_id}",
    response_model=ComplaintDetailResponse,
    summary="Get complaint details",
)
async def get_complaint(
    complaint_id: str,
    service: ComplaintServiceDep,
    settings: SettingsDep,
    current_user_email: str | None = Depends(get_current_user_email),
) -> ComplaintDetailResponse:
    """Retrieve a single complaint by ID."""
    complaint = service.get_complaint(complaint_id)
    # If authenticated user is a citizen, restrict detail access to own complaints
    if current_user_email and current_user_email != settings.admin_email:
        if complaint.citizen_email != current_user_email:
            from fastapi import HTTPException
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have permission to view this complaint",
            )
    return complaint


@router.put(
    "/{complaint_id}",
    response_model=ComplaintDetailResponse,
    summary="Update a complaint",
)
async def update_complaint(
    complaint_id: str,
    payload: CitizenComplaintUpdate,
    service: ComplaintServiceDep,
) -> ComplaintDetailResponse:
    """Update an existing complaint."""
    return service.update_complaint(complaint_id, payload)


@router.delete(
    "/{complaint_id}",
    status_code=status.HTTP_200_OK,
    summary="Delete a complaint",
)
async def delete_complaint(
    complaint_id: str,
    service: ComplaintServiceDep,
) -> dict[str, bool]:
    """Delete a complaint by ID."""
    service.delete_complaint(complaint_id)
    return {"success": True}


@router.post(
    "/{complaint_id}/analyze",
    response_model=ComplaintAnalyzeResponse,
    summary="Analyze or re-analyze a complaint with Gemini",
)
async def analyze_complaint(
    complaint_id: str,
    service: ComplaintServiceDep,
    force: bool = Query(default=False, description="Force re-analysis even if already completed"),
) -> ComplaintAnalyzeResponse:
    """Trigger Gemini AI analysis for a complaint."""
    complaint = service.analyze_complaint(complaint_id, force=force)
    if complaint.analysis_error_message:
        return ComplaintAnalyzeResponse(
            success=False,
            message=f"Analysis failed: {complaint.analysis_error_message}",
            complaint=complaint,
        )
    return ComplaintAnalyzeResponse(
        success=complaint.ai_analysis is not None,
        message=f"Analysis {complaint.analysis_status}",
        complaint=complaint,
    )


@router.post(
    "/{complaint_id}/analyze-image",
    response_model=ComplaintImageAnalyzeResponse,
    summary="Analyze or re-analyze a complaint image with Gemini Vision",
)
async def analyze_complaint_image(
    complaint_id: str,
    service: ComplaintServiceDep,
    force: bool = Query(default=False, description="Force re-analysis even if already completed"),
) -> ComplaintImageAnalyzeResponse:
    """Trigger Gemini Vision image intelligence for a complaint."""
    complaint = service.analyze_complaint_image(complaint_id, force=force)
    if complaint.vision_error_message:
        return ComplaintImageAnalyzeResponse(
            success=False,
            message=f"Vision analysis failed: {complaint.vision_error_message}",
            complaint=complaint,
        )
    return ComplaintImageAnalyzeResponse(
        success=complaint.image_analysis is not None,
        message=f"Image analysis {complaint.image_analysis_status}",
        complaint=complaint,
    )


@router.post(
    "/{complaint_id}/cluster",
    response_model=ClusterProcessResponse,
    summary="Run duplicate detection and clustering for a complaint",
)
async def cluster_complaint(
    complaint_id: str,
    duplicate_service: DuplicateDetectionServiceDep,
    settings: SettingsDep,
    force: bool = Query(default=False),
) -> ClusterProcessResponse:
    """Trigger duplicate detection and cluster assignment."""
    if not settings.clustering_enabled:
        raise BadRequestError("Clustering is disabled")
    updated = duplicate_service.process_complaint(complaint_id, force=force)
    return ClusterProcessResponse(
        success=updated.cluster_id is not None,
        message="Clustering completed" if updated.cluster_id else "Clustering did not assign a cluster",
        complaint_id=updated.id,
        cluster_id=updated.cluster_id,
        is_duplicate=updated.is_duplicate,
        duplicate_score=updated.duplicate_score,
    )
