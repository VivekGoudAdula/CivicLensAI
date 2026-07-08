"""Village domain models."""

from datetime import datetime

from pydantic import BaseModel, Field

from app.models.schemas.common import DocumentMetadata, DocumentMetadataCreate, GeoLocation


class VillageBase(BaseModel):
    """Shared village fields."""

    name: str = Field(min_length=2, max_length=128)
    constituency: str = Field(min_length=2, max_length=128)
    district: str = Field(min_length=2, max_length=128)
    state: str = Field(min_length=2, max_length=64)
    block: str | None = Field(default=None, max_length=128)
    pin_code: str | None = Field(default=None, pattern=r"^\d{6}$")
    population: int | None = Field(default=None, ge=0)
    geo: GeoLocation | None = None
    is_active: bool = True


class VillageCreate(VillageBase):
    """Fields required to create a village."""

    metadata: DocumentMetadataCreate = Field(default_factory=DocumentMetadataCreate)


class VillageUpdate(BaseModel):
    """Fields allowed on village update."""

    name: str | None = Field(default=None, min_length=2, max_length=128)
    constituency: str | None = Field(default=None, min_length=2, max_length=128)
    district: str | None = Field(default=None, min_length=2, max_length=128)
    state: str | None = Field(default=None, min_length=2, max_length=64)
    block: str | None = Field(default=None, max_length=128)
    pin_code: str | None = Field(default=None, pattern=r"^\d{6}$")
    population: int | None = Field(default=None, ge=0)
    geo: GeoLocation | None = None
    is_active: bool | None = None
    updated_by: str = Field(default="system", max_length=128)


class VillageResponse(VillageBase):
    """Village document returned from Firestore."""

    id: str
    metadata: DocumentMetadata
    complaint_count: int = Field(default=0, ge=0)
    open_complaint_count: int = Field(default=0, ge=0)


class VillageSearchFilters(BaseModel):
    """Filter parameters for village queries."""

    constituency: str | None = None
    district: str | None = None
    state: str | None = None
    block: str | None = None
    is_active: bool | None = None
    name_prefix: str | None = Field(default=None, max_length=128)
