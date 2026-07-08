"""Dependency injection for priority engine services."""

from __future__ import annotations

from typing import Annotated

from fastapi import Depends

from app.api.deps import GeminiDep, SettingsDep
from app.api.repository_deps import ClusterRepoDep, ComplaintRepoDep
from app.services.priority.priority_calculator import PriorityCalculator
from app.services.priority.priority_engine_service import PriorityEngineService
from app.services.priority.priority_repository import PriorityRepository
from app.services.priority.priority_scheduler import PriorityScheduler
from app.services.priority_portal_service import PriorityPortalService


def get_priority_repository(
    cluster_repo: ClusterRepoDep,
    complaint_repo: ComplaintRepoDep,
) -> PriorityRepository:
    return PriorityRepository(cluster_repo, complaint_repo)


def get_priority_calculator() -> PriorityCalculator:
    return PriorityCalculator()


def get_priority_engine_service(
    priority_repo: Annotated[PriorityRepository, Depends(get_priority_repository)],
    calculator: Annotated[PriorityCalculator, Depends(get_priority_calculator)],
    model: GeminiDep,
    settings: SettingsDep,
) -> PriorityEngineService:
    return PriorityEngineService(priority_repo, calculator, model, settings)


def get_priority_scheduler(
    priority_engine: Annotated[PriorityEngineService, Depends(get_priority_engine_service)],
    priority_repo: Annotated[PriorityRepository, Depends(get_priority_repository)],
    settings: SettingsDep,
) -> PriorityScheduler:
    return PriorityScheduler(priority_engine, priority_repo, settings)


def get_priority_portal_service(
    priority_repo: Annotated[PriorityRepository, Depends(get_priority_repository)],
    priority_engine: Annotated[PriorityEngineService, Depends(get_priority_engine_service)],
    priority_scheduler: Annotated[PriorityScheduler, Depends(get_priority_scheduler)],
    settings: SettingsDep,
) -> PriorityPortalService:
    return PriorityPortalService(priority_repo, priority_engine, priority_scheduler, settings)


PriorityEngineServiceDep = Annotated[PriorityEngineService, Depends(get_priority_engine_service)]
PrioritySchedulerDep = Annotated[PriorityScheduler, Depends(get_priority_scheduler)]
PriorityRepositoryDep = Annotated[PriorityRepository, Depends(get_priority_repository)]
PriorityPortalServiceDep = Annotated[PriorityPortalService, Depends(get_priority_portal_service)]
