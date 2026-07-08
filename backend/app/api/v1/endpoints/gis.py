"""GIS map REST API endpoints."""

from __future__ import annotations

import logging
from typing import Annotated

from fastapi import APIRouter, Depends

from app.api.repository_deps import ClusterRepoDep, ComplaintRepoDep
from app.models.schemas.gis_portal import GisMapResponse
from app.services.gis_portal_service import GisPortalService

logger = logging.getLogger(__name__)

router = APIRouter()


def get_gis_portal_service(
    complaint_repo: ComplaintRepoDep,
    cluster_repo: ClusterRepoDep,
) -> GisPortalService:
    return GisPortalService(complaint_repo, cluster_repo)


GisPortalServiceDep = Annotated[GisPortalService, Depends(get_gis_portal_service)]


@router.get(
    "/map",
    response_model=GisMapResponse,
    summary="Constituency GIS map data",
)
async def get_gis_map(service: GisPortalServiceDep) -> GisMapResponse:
    return service.get_map_data()
