"""Global search REST API."""

from __future__ import annotations

import logging
from typing import Annotated

from fastapi import APIRouter, Depends, Query

from app.api.repository_deps import ClusterRepoDep, ComplaintRepoDep, RecommendationRepoDep
from app.models.schemas.search_portal import GlobalSearchFilters, GlobalSearchResponse, SearchSortOption
from app.services.search_portal_service import SearchPortalService

logger = logging.getLogger(__name__)

router = APIRouter()


def get_search_portal_service(
    complaint_repo: ComplaintRepoDep,
    cluster_repo: ClusterRepoDep,
    recommendation_repo: RecommendationRepoDep,
) -> SearchPortalService:
    return SearchPortalService(complaint_repo, cluster_repo, recommendation_repo)


SearchPortalServiceDep = Annotated[SearchPortalService, Depends(get_search_portal_service)]


@router.get("", response_model=GlobalSearchResponse, summary="Global platform search")
async def global_search(
    service: SearchPortalServiceDep,
    q: str = Query(default="", max_length=128),
    sort: SearchSortOption = Query(default="newest"),
    limit: int = Query(default=50, ge=1, le=200),
    category: str | None = None,
    department: str | None = None,
    village: str | None = None,
    priority: str | None = None,
    severity: str | None = None,
    status: str | None = None,
    cluster_id: str | None = None,
    date_from: str | None = None,
    date_to: str | None = None,
    ai_confidence_min: float | None = Query(default=None, ge=0, le=1),
    recommendation_status: str | None = None,
    urgency: str | None = None,
    resolved: bool | None = None,
) -> GlobalSearchResponse:
    filters = GlobalSearchFilters(
        category=category,
        department=department,
        village=village,
        priority=priority,
        severity=severity,
        status=status,
        cluster_id=cluster_id,
        date_from=date_from,
        date_to=date_to,
        ai_confidence_min=ai_confidence_min,
        recommendation_status=recommendation_status,
        urgency=urgency,
        resolved=resolved,
    )
    return service.search(q, filters=filters, sort=sort, limit=limit)
