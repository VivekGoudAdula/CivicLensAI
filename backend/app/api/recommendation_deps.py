"""Recommendation engine dependency injection."""

from __future__ import annotations

from typing import Annotated

from fastapi import Depends

from app.api.deps import GeminiDep, SettingsDep
from app.api.priority_deps import get_priority_portal_service
from app.api.repository_deps import ClusterRepoDep, ComplaintRepoDep, RecommendationRepoDep
from app.services.analytics_intelligence_service import AnalyticsIntelligenceService
from app.services.gis_portal_service import GisPortalService
from app.services.priority_portal_service import PriorityPortalService
from app.services.recommendation.recommendation_context_builder import RecommendationContextBuilder
from app.services.recommendation.recommendation_engine_repository import RecommendationEngineRepository
from app.services.recommendation.recommendation_engine_service import RecommendationEngineService
from app.services.recommendation_portal_service import RecommendationPortalService


def get_recommendation_engine_repository(
    recommendation_repo: RecommendationRepoDep,
) -> RecommendationEngineRepository:
    return RecommendationEngineRepository(recommendation_repo)


def get_recommendation_context_builder() -> RecommendationContextBuilder:
    return RecommendationContextBuilder()


def get_analytics_intelligence_service(
    complaint_repo: ComplaintRepoDep,
    cluster_repo: ClusterRepoDep,
) -> AnalyticsIntelligenceService:
    return AnalyticsIntelligenceService(complaint_repo, cluster_repo)


def get_gis_portal_service(
    complaint_repo: ComplaintRepoDep,
    cluster_repo: ClusterRepoDep,
) -> GisPortalService:
    return GisPortalService(complaint_repo, cluster_repo)


def get_recommendation_engine_service(
    complaint_repo: ComplaintRepoDep,
    cluster_repo: ClusterRepoDep,
    priority_portal: Annotated[PriorityPortalService, Depends(get_priority_portal_service)],
    analytics_service: Annotated[AnalyticsIntelligenceService, Depends(get_analytics_intelligence_service)],
    gis_service: Annotated[GisPortalService, Depends(get_gis_portal_service)],
    engine_repo: Annotated[RecommendationEngineRepository, Depends(get_recommendation_engine_repository)],
    context_builder: Annotated[RecommendationContextBuilder, Depends(get_recommendation_context_builder)],
    model: GeminiDep,
    settings: SettingsDep,
) -> RecommendationEngineService:
    return RecommendationEngineService(
        complaint_repo,
        cluster_repo,
        priority_portal,
        analytics_service,
        gis_service,
        engine_repo,
        context_builder,
        model,
        settings,
    )


def get_recommendation_portal_service(
    recommendation_repo: RecommendationRepoDep,
    engine_repo: Annotated[RecommendationEngineRepository, Depends(get_recommendation_engine_repository)],
) -> RecommendationPortalService:
    return RecommendationPortalService(recommendation_repo, engine_repo)


RecommendationEngineServiceDep = Annotated[
    RecommendationEngineService, Depends(get_recommendation_engine_service)
]
RecommendationPortalServiceDep = Annotated[
    RecommendationPortalService, Depends(get_recommendation_portal_service)
]
