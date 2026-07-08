"""Dependency injection for clustering services."""

from __future__ import annotations

from typing import Annotated

from fastapi import Depends

from app.api.deps import GeminiDep, SettingsDep
from app.api.priority_deps import get_priority_engine_service
from app.api.repository_deps import ClusterRepoDep, ComplaintRepoDep, VillageRepoDep
from app.services.clustering.cluster_service import ClusterService
from app.services.clustering.duplicate_detection_service import DuplicateDetectionService
from app.services.clustering.similarity_engine import SimilarityEngine
from app.services.priority.priority_engine_service import PriorityEngineService


def get_cluster_service(
    cluster_repo: ClusterRepoDep,
    complaint_repo: ComplaintRepoDep,
    priority_engine: Annotated[PriorityEngineService, Depends(get_priority_engine_service)],
) -> ClusterService:
    return ClusterService(cluster_repo, complaint_repo, priority_engine)


def get_similarity_engine(
    complaint_repo: ComplaintRepoDep,
    village_repo: VillageRepoDep,
    settings: SettingsDep,
) -> SimilarityEngine:
    return SimilarityEngine(complaint_repo, village_repo, settings)


def get_duplicate_detection_service(
    complaint_repo: ComplaintRepoDep,
    cluster_service: Annotated[ClusterService, Depends(get_cluster_service)],
    similarity_engine: Annotated[SimilarityEngine, Depends(get_similarity_engine)],
    model: GeminiDep,
    settings: SettingsDep,
) -> DuplicateDetectionService:
    return DuplicateDetectionService(
        complaint_repo,
        cluster_service,
        similarity_engine,
        model,
        settings,
    )


DuplicateDetectionServiceDep = Annotated[
    DuplicateDetectionService,
    Depends(get_duplicate_detection_service),
]
ClusterServiceDep = Annotated[ClusterService, Depends(get_cluster_service)]
