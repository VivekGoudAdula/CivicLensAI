"""Shared Pydantic schema components."""

from datetime import datetime

from pydantic import BaseModel, Field


class GeoLocation(BaseModel):
    """Geographic coordinates and optional address."""

    latitude: float = Field(ge=-90, le=90)
    longitude: float = Field(ge=-180, le=180)
    address: str | None = Field(default=None, max_length=500)


class DocumentMetadata(BaseModel):
    """Standard audit metadata for all documents."""

    created_at: datetime
    updated_at: datetime
    created_by: str = Field(default="system", max_length=128)
    updated_by: str = Field(default="system", max_length=128)
    version: int = Field(default=1, ge=1)


class DocumentMetadataCreate(BaseModel):
    """Metadata fields set on document creation."""

    created_by: str = Field(default="system", max_length=128)
    updated_by: str = Field(default="system", max_length=128)


class Attachment(BaseModel):
    """File attachment reference."""

    url: str = Field(max_length=2048)
    file_name: str = Field(max_length=255)
    mime_type: str = Field(max_length=128)
    size_bytes: int | None = Field(default=None, ge=0)


class DocumentReferenceField(BaseModel):
    """Denormalized Firestore document reference."""

    ref_path: str = Field(description="Firestore document path, e.g. villages/abc123")
    document_id: str = Field(min_length=1, max_length=128)
