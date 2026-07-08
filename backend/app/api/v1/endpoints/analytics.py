"""Analytics dashboard REST API endpoints."""

from __future__ import annotations

import logging
from typing import Annotated

from fastapi import APIRouter, Depends, Query

from app.api.priority_deps import get_priority_portal_service
from app.api.repository_deps import ClusterRepoDep, ComplaintRepoDep
from app.models.schemas.analytics_intelligence import AnalyticsIntelligenceResponse
from app.models.schemas.analytics_portal import (
    DashboardActivitiesResponse,
    DashboardAnalyticsResponse,
    DashboardHomeResponse,
)
from app.services.analytics_intelligence_service import AnalyticsIntelligenceService
from app.services.analytics_portal_service import AnalyticsPortalService
from app.services.priority_portal_service import PriorityPortalService

logger = logging.getLogger(__name__)

router = APIRouter()


def get_analytics_portal_service(
    complaint_repo: ComplaintRepoDep,
    cluster_repo: ClusterRepoDep,
    priority_portal: Annotated[PriorityPortalService, Depends(get_priority_portal_service)],
) -> AnalyticsPortalService:
    return AnalyticsPortalService(complaint_repo, cluster_repo, priority_portal)


AnalyticsPortalServiceDep = Annotated[AnalyticsPortalService, Depends(get_analytics_portal_service)]


@router.get(
    "/dashboard",
    response_model=DashboardHomeResponse,
    summary="MP command center home dashboard",
)
async def get_dashboard_home(service: AnalyticsPortalServiceDep) -> DashboardHomeResponse:
    return service.get_home_dashboard()


@router.get(
    "/activities",
    response_model=DashboardActivitiesResponse,
    summary="Recent constituency activity feed",
)
async def get_dashboard_activities(
    service: AnalyticsPortalServiceDep,
    limit: int = Query(default=100, ge=1, le=500),
) -> DashboardActivitiesResponse:
    return service.get_activities(limit=limit)


@router.get(
    "/overview",
    response_model=DashboardAnalyticsResponse,
    summary="Analytics overview charts and insights",
)
async def get_analytics_overview(service: AnalyticsPortalServiceDep) -> DashboardAnalyticsResponse:
    return service.get_analytics_overview()


@router.get(
    "/intelligence",
    response_model=AnalyticsIntelligenceResponse,
    summary="Full constituency analytics intelligence (Phase 11)",
)
async def get_analytics_intelligence(
    complaint_repo: ComplaintRepoDep,
    cluster_repo: ClusterRepoDep,
) -> AnalyticsIntelligenceResponse:
    service = AnalyticsIntelligenceService(complaint_repo, cluster_repo)
    return service.get_intelligence()
