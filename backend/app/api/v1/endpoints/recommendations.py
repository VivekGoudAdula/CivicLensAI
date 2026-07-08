"""MP decision recommendation REST API."""

from __future__ import annotations

import logging

from fastapi import APIRouter, Query

from app.api.recommendation_deps import (
    RecommendationEngineServiceDep,
    RecommendationPortalServiceDep,
)
from app.models.schemas.recommendation_portal import (
    RecommendationCenterResponse,
    RecommendationGenerateResponse,
    RecommendationListResponse,
)

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get(
    "/center",
    response_model=RecommendationCenterResponse,
    summary="AI Decision Recommendation Center",
)
async def get_recommendation_center(
    service: RecommendationPortalServiceDep,
) -> RecommendationCenterResponse:
    return service.get_center()


@router.post(
    "/generate",
    response_model=RecommendationGenerateResponse,
    summary="Generate MP development recommendations via Gemini",
)
async def generate_recommendations(
    engine: RecommendationEngineServiceDep,
    portal: RecommendationPortalServiceDep,
    force: bool = Query(default=False),
) -> RecommendationGenerateResponse:
    try:
        engine.generate(force=force)
        center = portal.get_center()
        return RecommendationGenerateResponse(
            success=True,
            message="Recommendation engine completed successfully",
            center=center,
        )
    except Exception as exc:
        logger.exception("Recommendation generation failed")
        return RecommendationGenerateResponse(success=False, message=str(exc))


@router.get(
    "",
    response_model=RecommendationListResponse,
    summary="List persisted recommendations",
)
async def list_recommendations(
    service: RecommendationPortalServiceDep,
    limit: int = Query(default=50, ge=1, le=200),
) -> RecommendationListResponse:
    return service.list_recommendations(limit=limit)
