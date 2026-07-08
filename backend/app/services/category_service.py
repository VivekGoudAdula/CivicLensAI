"""Category service layer for citizen portal."""

from __future__ import annotations

import logging

from app.models.domain.category import CategoryResponse
from app.models.schemas.complaint_portal import CategoryListResponse
from app.repositories.category_repository import CategoryRepository

logger = logging.getLogger(__name__)


class CategoryService:
    """Business logic for complaint categories."""

    def __init__(self, category_repo: CategoryRepository):
        self.category_repo = category_repo

    def list_active(self) -> CategoryListResponse:
        """Return all active categories ordered for display."""
        items = self.category_repo.list_active()
        logger.info("Listed %s active categories", len(items))
        return CategoryListResponse(items=items)

    def get_by_id(self, category_id: str) -> CategoryResponse | None:
        """Retrieve a category by document ID."""
        return self.category_repo.get_by_id(category_id)
