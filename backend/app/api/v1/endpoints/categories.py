"""Category REST API endpoints for citizen portal."""

from __future__ import annotations

import logging
from typing import Annotated

from fastapi import APIRouter, Depends

from app.api.repository_deps import CategoryRepoDep
from app.models.schemas.complaint_portal import CategoryListResponse
from app.services.category_service import CategoryService

logger = logging.getLogger(__name__)

router = APIRouter()


def get_category_service(category_repo: CategoryRepoDep) -> CategoryService:
    return CategoryService(category_repo)


CategoryServiceDep = Annotated[CategoryService, Depends(get_category_service)]


@router.get(
    "",
    response_model=CategoryListResponse,
    summary="List active complaint categories",
)
async def list_categories(service: CategoryServiceDep) -> CategoryListResponse:
    """Return all active complaint categories."""
    return service.list_active()
