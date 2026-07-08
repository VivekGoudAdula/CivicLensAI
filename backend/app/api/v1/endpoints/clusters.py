"""Cluster REST API endpoints."""

from __future__ import annotations

import logging
from typing import Annotated

from fastapi import APIRouter, Depends, Query, status

from app.api.clustering_deps import DuplicateDetectionServiceDep
from app.api.deps import SettingsDep
from app.api.repository_deps import ClusterRepoDep, ComplaintRepoDep
from app.models.enums.common import ClusterStatus
from app.models.schemas.cluster_portal import (
    ClusterDashboardSummary,
    ClusterDetailResponse,
    ClusterListResponse,
    ClusterProcessResponse,
)
from app.services.cluster_portal_service import ClusterPortalService

logger = logging.getLogger(__name__)

router = APIRouter()


def get_cluster_portal_service(
    cluster_repo: ClusterRepoDep,
    complaint_repo: ComplaintRepoDep,
    duplicate_service: DuplicateDetectionServiceDep,
    settings: SettingsDep,
) -> ClusterPortalService:
    return ClusterPortalService(cluster_repo, complaint_repo, duplicate_service, settings)


ClusterPortalServiceDep = Annotated[ClusterPortalService, Depends(get_cluster_portal_service)]


@router.get(
    "",
    response_model=ClusterListResponse,
    summary="List complaint clusters",
)
async def list_clusters(
    service: ClusterPortalServiceDep,
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=12, ge=1, le=100),
    search: str | None = Query(default=None, max_length=128),
    category: str | None = Query(default=None),
    status: ClusterStatus | None = Query(default=None),
) -> ClusterListResponse:
    return service.list_clusters(
        page=page,
        page_size=page_size,
        search=search,
        category=category,
        status=status,
    )


@router.get(
    "/dashboard",
    response_model=ClusterDashboardSummary,
    summary="Cluster dashboard summary metrics",
)
async def cluster_dashboard(
    service: ClusterPortalServiceDep,
) -> ClusterDashboardSummary:
    return service.get_dashboard_summary()


@router.get(
    "/{cluster_id}",
    response_model=ClusterDetailResponse,
    summary="Get cluster details",
)
async def get_cluster(
    cluster_id: str,
    service: ClusterPortalServiceDep,
) -> ClusterDetailResponse:
    return service.get_cluster(cluster_id)


@router.post(
    "/process/{complaint_id}",
    response_model=ClusterProcessResponse,
    status_code=status.HTTP_200_OK,
    summary="Run duplicate detection and clustering for a complaint",
)
async def process_complaint_clustering(
    complaint_id: str,
    service: ClusterPortalServiceDep,
    force: bool = Query(default=False),
) -> ClusterProcessResponse:
    return service.process_complaint_clustering(complaint_id, force=force)
