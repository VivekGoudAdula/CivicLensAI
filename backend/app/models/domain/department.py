"""Department domain models."""

from pydantic import BaseModel, EmailStr, Field

from app.models.enums.common import DepartmentCategory
from app.models.schemas.common import DocumentMetadata, DocumentMetadataCreate


class DepartmentBase(BaseModel):
    """Shared department fields."""

    name: str = Field(min_length=2, max_length=256)
    code: str = Field(min_length=2, max_length=32, pattern=r"^[A-Z0-9_]+$")
    category: DepartmentCategory
    description: str | None = Field(default=None, max_length=2000)
    head_name: str | None = Field(default=None, max_length=128)
    contact_email: EmailStr | None = None
    contact_phone: str | None = Field(default=None, pattern=r"^\+?[0-9]{10,15}$")
    constituency: str | None = Field(default=None, max_length=128)
    is_active: bool = True


class DepartmentCreate(DepartmentBase):
    """Fields required to create a department."""

    metadata: DocumentMetadataCreate = Field(default_factory=DocumentMetadataCreate)


class DepartmentUpdate(BaseModel):
    """Fields allowed on department update."""

    name: str | None = Field(default=None, min_length=2, max_length=256)
    category: DepartmentCategory | None = None
    description: str | None = Field(default=None, max_length=2000)
    head_name: str | None = Field(default=None, max_length=128)
    contact_email: EmailStr | None = None
    contact_phone: str | None = Field(default=None, pattern=r"^\+?[0-9]{10,15}$")
    constituency: str | None = Field(default=None, max_length=128)
    is_active: bool | None = None
    updated_by: str = Field(default="system", max_length=128)


class DepartmentResponse(DepartmentBase):
    """Department document returned from Firestore."""

    id: str
    metadata: DocumentMetadata
    assigned_recommendation_count: int = Field(default=0, ge=0)
    active_recommendation_count: int = Field(default=0, ge=0)


class DepartmentSearchFilters(BaseModel):
    """Filter parameters for department queries."""

    category: DepartmentCategory | None = None
    constituency: str | None = None
    is_active: bool | None = None
    code: str | None = None
    name_prefix: str | None = Field(default=None, max_length=256)
