"""Priority engine REST API endpoints."""

from __future__ import annotations

import logging

from fastapi import APIRouter, Query, status

from app.api.priority_deps import PriorityPortalServiceDep
from app.models.schemas.priority_portal import (
    PriorityAnalyzeResponse,
    PriorityDashboardResponse,
    PriorityRerankResponse,
)

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get(
    "/dashboard",
    response_model=PriorityDashboardResponse,
    summary="Priority intelligence dashboard",
)
async def priority_dashboard(service: PriorityPortalServiceDep) -> PriorityDashboardResponse:
    return service.get_dashboard()


@router.post(
    "/analyze/{cluster_id}",
    response_model=PriorityAnalyzeResponse,
    status_code=status.HTTP_200_OK,
    summary="Analyze or re-analyze cluster priority with Gemini",
)
async def analyze_cluster_priority(
    cluster_id: str,
    service: PriorityPortalServiceDep,
    force: bool = Query(default=False),
) -> PriorityAnalyzeResponse:
    return service.analyze_cluster(cluster_id, force=force)


@router.post(
    "/rerank",
    response_model=PriorityRerankResponse,
    status_code=status.HTTP_200_OK,
    summary="Recalculate priority for all clusters",
)
async def rerank_all_clusters(
    service: PriorityPortalServiceDep,
    force: bool = Query(default=False),
) -> PriorityRerankResponse:
    return service.rerun_all(force=force)
