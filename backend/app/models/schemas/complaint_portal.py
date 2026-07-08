"""API schemas for citizen complaint portal."""

from datetime import datetime

from pydantic import BaseModel, Field, field_validator

from app.models.domain.complaint import ComplaintAIAnalysis, ComplaintImageAnalysis
from app.models.domain.category import CategoryResponse
from app.models.enums.common import AnalysisStatus, ComplaintCategory, ComplaintPriority, ComplaintStatus
from app.models.schemas.common import DocumentMetadata, GeoLocation

MAX_IMAGE_BASE64_LENGTH = 700_000
MAX_AUDIO_BASE64_LENGTH = 700_000


class ComplaintMediaBase64(BaseModel):
    """Base64-encoded media attachment."""

    data: str = Field(min_length=1)
    mime_type: str = Field(max_length=128)
    file_name: str | None = Field(default=None, max_length=255)


class CitizenComplaintSubmit(BaseModel):
    """Citizen portal complaint submission payload."""

    title: str = Field(min_length=5, max_length=256)
    description: str = Field(min_length=10, max_length=5000)
    category_id: str = Field(min_length=1, max_length=128)
    latitude: float = Field(ge=-90, le=90)
    longitude: float = Field(ge=-180, le=180)
    address: str = Field(min_length=3, max_length=500)
    landmark: str | None = Field(default=None, max_length=256)
    image: ComplaintMediaBase64 | None = None
    audio: ComplaintMediaBase64 | None = None
    audio_duration_seconds: float | None = Field(default=None, ge=0)
    contact_name: str | None = Field(default=None, max_length=128)
    mobile_number: str = Field(pattern=r"^[6-9]\d{9}$")
    is_anonymous: bool = False
    constituency: str = Field(default="Amethi", max_length=128)
    district: str = Field(default="Amethi", max_length=128)
    state: str = Field(default="Uttar Pradesh", max_length=64)
    village_id: str = Field(default="citizen_portal", max_length=128)
    village_name: str = Field(default="Citizen Reported", max_length=128)

    @field_validator("image")
    @classmethod
    def validate_image_size(cls, value: ComplaintMediaBase64 | None) -> ComplaintMediaBase64 | None:
        if value and len(value.data) > MAX_IMAGE_BASE64_LENGTH:
            raise ValueError(
                f"Image exceeds maximum size of {MAX_IMAGE_BASE64_LENGTH} characters"
            )
        if value and not value.mime_type.startswith("image/"):
            raise ValueError("Image must be a valid image MIME type")
        return value

    @field_validator("audio")
    @classmethod
    def validate_audio_size(cls, value: ComplaintMediaBase64 | None) -> ComplaintMediaBase64 | None:
        if value and len(value.data) > MAX_AUDIO_BASE64_LENGTH:
            raise ValueError(
                f"Audio exceeds maximum size of {MAX_AUDIO_BASE64_LENGTH} characters"
            )
        if value and not value.mime_type.startswith("audio/"):
            raise ValueError("Audio must be a valid audio MIME type")
        return value

    @field_validator("contact_name")
    @classmethod
    def validate_contact_name(cls, value: str | None, info) -> str | None:
        is_anonymous = info.data.get("is_anonymous", False)
        if not is_anonymous and not value:
            raise ValueError("Contact name is required when not submitting anonymously")
        return value


class CitizenComplaintUpdate(BaseModel):
    """Citizen portal complaint update payload."""

    title: str | None = Field(default=None, min_length=5, max_length=256)
    description: str | None = Field(default=None, min_length=10, max_length=5000)
    category_id: str | None = Field(default=None, max_length=128)
    latitude: float | None = Field(default=None, ge=-90, le=90)
    longitude: float | None = Field(default=None, ge=-180, le=180)
    address: str | None = Field(default=None, max_length=500)
    landmark: str | None = Field(default=None, max_length=256)
    status: ComplaintStatus | None = None


class ComplaintAIAnalysisResponse(ComplaintAIAnalysis):
    """AI analysis payload exposed via the citizen portal API."""


class ComplaintImageAnalysisResponse(ComplaintImageAnalysis):
    """Gemini Vision image analysis payload exposed via the citizen portal API."""


class ComplaintAnalyzeResponse(BaseModel):
    """Response after triggering complaint AI analysis."""

    success: bool = True
    message: str
    complaint: "ComplaintDetailResponse"


class ComplaintImageAnalyzeResponse(BaseModel):
    """Response after triggering complaint image vision analysis."""

    success: bool = True
    message: str
    complaint: "ComplaintDetailResponse"


class ComplaintListItem(BaseModel):
    """Summary complaint for list views."""

    id: str
    title: str
    description: str
    category_id: str
    category_name: str
    category_slug: str
    status: ComplaintStatus
    priority: ComplaintPriority
    address: str | None = None
    landmark: str | None = None
    is_anonymous: bool = False
    citizen_name: str | None = None
    citizen_phone: str | None = None
    has_image: bool = False
    has_audio: bool = False
    submitted_at: datetime
    constituency: str
    analysis_status: AnalysisStatus | None = None
    has_ai_analysis: bool = False
    image_analysis_status: AnalysisStatus | None = None
    has_image_analysis: bool = False
    cluster_id: str | None = None
    is_duplicate: bool = False
    duplicate_score: float | None = None


class ComplaintDetailResponse(BaseModel):
    """Full complaint detail for citizen portal."""

    id: str
    title: str
    description: str
    category_id: str
    category_name: str
    category_slug: str
    status: ComplaintStatus
    priority: ComplaintPriority
    location: GeoLocation | None = None
    landmark: str | None = None
    image_base64: str | None = None
    image_mime_type: str | None = None
    audio_base64: str | None = None
    audio_mime_type: str | None = None
    audio_duration_seconds: float | None = None
    is_anonymous: bool = False
    citizen_name: str | None = None
    citizen_phone: str | None = None
    citizen_email: str | None = None
    constituency: str
    district: str
    state: str
    village_name: str
    submitted_at: datetime
    resolved_at: datetime | None = None
    metadata: DocumentMetadata
    ai_analysis: ComplaintAIAnalysisResponse | None = None
    analysis_status: AnalysisStatus = AnalysisStatus.PENDING
    analysis_started_at: datetime | None = None
    analysis_completed_at: datetime | None = None
    analysis_model_name: str | None = None
    analysis_processing_time_ms: int | None = None
    analysis_prompt_version: str | None = None
    analysis_error_message: str | None = None
    analysis_retry_count: int = 0
    image_analysis: ComplaintImageAnalysisResponse | None = None
    image_analysis_status: AnalysisStatus | None = None
    vision_model: str | None = None
    vision_processing_time_ms: int | None = None
    vision_completed_at: datetime | None = None
    vision_started_at: datetime | None = None
    vision_prompt_version: str | None = None
    vision_error_message: str | None = None
    vision_retry_count: int = 0
    cluster_id: str | None = None
    is_duplicate: bool = False
    duplicate_score: float | None = None
    duplicate_reason: str | None = None
    duplicate_confidence: float | None = None
    matched_complaint_id: str | None = None
    matched_cluster_id: str | None = None


class ComplaintListResponse(BaseModel):
    """Paginated complaint list response."""

    success: bool = True
    items: list[ComplaintListItem]
    total: int
    page: int
    page_size: int
    has_more: bool


class ComplaintCreateResponse(BaseModel):
    """Response after creating a complaint."""

    success: bool = True
    message: str = "Complaint submitted successfully"
    complaint: ComplaintDetailResponse


class CategoryListResponse(BaseModel):
    """Active categories list response."""

    success: bool = True
    items: list[CategoryResponse]


ComplaintAnalyzeResponse.model_rebuild()
ComplaintImageAnalyzeResponse.model_rebuild()
