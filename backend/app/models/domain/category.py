"""Complaint category domain models."""

from pydantic import BaseModel, Field

from app.models.schemas.common import DocumentMetadata, DocumentMetadataCreate


class CategoryBase(BaseModel):
    """Shared category fields."""

    name: str = Field(min_length=2, max_length=128)
    slug: str = Field(min_length=2, max_length=64, pattern=r"^[a-z0-9_]+$")
    description: str | None = Field(default=None, max_length=500)
    icon: str | None = Field(default=None, max_length=64)
    display_order: int = Field(default=0, ge=0)
    is_active: bool = True


class CategoryCreate(CategoryBase):
    """Fields required to create a category."""

    metadata: DocumentMetadataCreate = Field(default_factory=DocumentMetadataCreate)


class CategoryUpdate(BaseModel):
    """Fields allowed on category update."""

    name: str | None = Field(default=None, min_length=2, max_length=128)
    description: str | None = Field(default=None, max_length=500)
    icon: str | None = Field(default=None, max_length=64)
    display_order: int | None = Field(default=None, ge=0)
    is_active: bool | None = None
    updated_by: str = Field(default="system", max_length=128)


class CategoryResponse(CategoryBase):
    """Category document returned from Firestore."""

    id: str
    metadata: DocumentMetadata
