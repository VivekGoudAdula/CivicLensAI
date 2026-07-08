"""Repository dependency injection for FastAPI."""

from collections.abc import Generator
from typing import Annotated

from fastapi import Depends
from google.cloud.firestore_v1 import Client as FirestoreClient

from app.api.deps import get_db
from app.repositories.analytics_repository import AnalyticsRepository
from app.repositories.category_repository import CategoryRepository
from app.repositories.cluster_repository import ClusterRepository
from app.repositories.complaint_repository import ComplaintRepository
from app.repositories.department_repository import DepartmentRepository
from app.repositories.recommendation_repository import RecommendationRepository
from app.repositories.village_repository import VillageRepository


def get_village_repository(
    db: FirestoreClient = Depends(get_db),
) -> Generator[VillageRepository, None, None]:
    yield VillageRepository(db)


def get_department_repository(
    db: FirestoreClient = Depends(get_db),
) -> Generator[DepartmentRepository, None, None]:
    yield DepartmentRepository(db)


def get_complaint_repository(
    db: FirestoreClient = Depends(get_db),
) -> Generator[ComplaintRepository, None, None]:
    yield ComplaintRepository(db)


def get_category_repository(
    db: FirestoreClient = Depends(get_db),
) -> Generator[CategoryRepository, None, None]:
    yield CategoryRepository(db)


def get_cluster_repository(
    db: FirestoreClient = Depends(get_db),
) -> Generator[ClusterRepository, None, None]:
    yield ClusterRepository(db)


def get_recommendation_repository(
    db: FirestoreClient = Depends(get_db),
) -> Generator[RecommendationRepository, None, None]:
    yield RecommendationRepository(db)


def get_analytics_repository(
    db: FirestoreClient = Depends(get_db),
) -> Generator[AnalyticsRepository, None, None]:
    yield AnalyticsRepository(db)


VillageRepoDep = Annotated[VillageRepository, Depends(get_village_repository)]
DepartmentRepoDep = Annotated[DepartmentRepository, Depends(get_department_repository)]
ComplaintRepoDep = Annotated[ComplaintRepository, Depends(get_complaint_repository)]
CategoryRepoDep = Annotated[CategoryRepository, Depends(get_category_repository)]
ClusterRepoDep = Annotated[ClusterRepository, Depends(get_cluster_repository)]
RecommendationRepoDep = Annotated[
    RecommendationRepository,
    Depends(get_recommendation_repository),
]
AnalyticsRepoDep = Annotated[AnalyticsRepository, Depends(get_analytics_repository)]
