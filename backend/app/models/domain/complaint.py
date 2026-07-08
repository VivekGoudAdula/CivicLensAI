"""Complaint domain models."""

from datetime import datetime

from pydantic import BaseModel, EmailStr, Field

from app.models.enums.common import (
    AnalysisStatus,
    ComplaintCategory,
    ComplaintPriority,
    ComplaintStatus,
    SentimentLabel,
)
from app.models.schemas.common import Attachment, DocumentMetadata, DocumentMetadataCreate, GeoLocation


class ComplaintImageAnalysis(BaseModel):
    """Gemini Vision image intelligence attached to a complaint."""

    primary_issue: str = Field(max_length=128)
    secondary_issue: str | None = Field(default=None, max_length=128)
    description: str = Field(max_length=3000)
    severity: str = Field(default="Medium", max_length=32)
    confidence_score: float = Field(default=0.0, ge=0, le=1)
    visible_damage: str = Field(default="", max_length=2000)
    estimated_area_affected: str = Field(default="", max_length=512)
    safety_risk: str = Field(default="", max_length=2000)
    suggested_department: str = Field(default="", max_length=256)
    suggested_immediate_action: str = Field(default="", max_length=2000)
    suggested_long_term_action: str = Field(default="", max_length=2000)
    possible_public_impact: str = Field(default="", max_length=2000)
    duplicate_indicators: list[str] = Field(default_factory=list, max_length=20)
    detected_objects: list[str] = Field(default_factory=list, max_length=50)
    environmental_risk: str = Field(default="", max_length=2000)
    road_safety_risk: str = Field(default="", max_length=2000)
    human_presence: bool = False
    vehicles_present: bool = False
    requires_urgent_attention: bool = False
    reasoning: str = Field(default="", max_length=3000)
    processed_at: datetime
    model_version: str = Field(default="gemini-2.5-flash", max_length=64)
    prompt_version: str = Field(default="1.0.0", max_length=16)


class ComplaintAIAnalysis(BaseModel):
    """AI-generated civic intelligence attached to a complaint."""

    category: str = Field(default="", max_length=128)
    sub_category: str = Field(default="", max_length=128)
    responsible_department: str = Field(default="", max_length=256)
    urgency: str = Field(default="medium", max_length=32)
    severity: str = Field(default="medium", max_length=32)
    priority_level: str = Field(default="medium", max_length=32)
    summary: str = Field(max_length=2000)
    detailed_explanation: str = Field(default="", max_length=5000)
    keywords: list[str] = Field(default_factory=list, max_length=50)
    affected_infrastructure: str = Field(default="", max_length=1000)
    affected_citizens_estimate: str | None = Field(default=None, max_length=256)
    government_scheme: str | None = Field(default=None, max_length=512)
    suggested_immediate_action: str = Field(default="", max_length=2000)
    suggested_long_term_action: str = Field(default="", max_length=2000)
    required_department: str = Field(default="", max_length=256)
    required_team: str = Field(default="", max_length=256)
    confidence_score: float = Field(default=0.0, ge=0, le=1)
    reasoning: str = Field(default="", max_length=3000)
    duplicate_possibility: float = Field(default=0.0, ge=0, le=1)
    tags: list[str] = Field(default_factory=list, max_length=20)
    language_detected: str = Field(default="en", max_length=32)
    translated_english: str | None = Field(default=None, max_length=5000)
    voice_transcript: str | None = Field(default=None, max_length=5000)
    sentiment: SentimentLabel = SentimentLabel.NEUTRAL
    urgency_score: float = Field(default=0.5, ge=0, le=1)
    language: str = Field(default="en", max_length=16)
    processed_at: datetime
    model_version: str = Field(default="gemini-2.5-flash", max_length=64)
    prompt_version: str = Field(default="1.0.0", max_length=16)


class ComplaintBase(BaseModel):
    """Shared complaint fields."""

    title: str = Field(min_length=5, max_length=256)
    description: str = Field(min_length=10, max_length=5000)
    category: ComplaintCategory
    priority: ComplaintPriority = ComplaintPriority.MEDIUM
    status: ComplaintStatus = ComplaintStatus.SUBMITTED
    village_id: str = Field(min_length=1, max_length=128)
    village_ref: str = Field(description="Firestore path: villages/{id}")
    village_name: str = Field(max_length=128)
    constituency: str = Field(max_length=128)
    district: str = Field(max_length=128)
    state: str = Field(max_length=64)
    citizen_name: str | None = Field(default=None, max_length=128)
    citizen_phone: str | None = Field(default=None, pattern=r"^\+?[0-9]{10,15}$")
    citizen_email: EmailStr | None = None
    location: GeoLocation | None = None
    landmark: str | None = Field(default=None, max_length=256)
    category_id: str | None = Field(default=None, max_length=128)
    category_name: str | None = Field(default=None, max_length=128)
    category_slug: str | None = Field(default=None, max_length=64)
    image_base64: str | None = None
    image_mime_type: str | None = Field(default=None, max_length=128)
    audio_base64: str | None = None
    audio_mime_type: str | None = Field(default=None, max_length=128)
    audio_duration_seconds: float | None = Field(default=None, ge=0)
    is_anonymous: bool = False
    attachments: list[Attachment] = Field(default_factory=list, max_length=10)
    cluster_id: str | None = Field(default=None, max_length=128)
    cluster_ref: str | None = Field(default=None, description="Firestore path: clusters/{id}")
    ai_analysis: ComplaintAIAnalysis | None = None
    analysis_status: AnalysisStatus = AnalysisStatus.PENDING
    analysis_started_at: datetime | None = None
    analysis_completed_at: datetime | None = None
    analysis_model_name: str | None = Field(default=None, max_length=64)
    analysis_processing_time_ms: int | None = Field(default=None, ge=0)
    analysis_prompt_version: str | None = Field(default=None, max_length=16)
    analysis_error_message: str | None = Field(default=None, max_length=2000)
    analysis_retry_count: int = Field(default=0, ge=0)
    image_analysis: ComplaintImageAnalysis | None = None
    image_analysis_status: AnalysisStatus | None = None
    vision_model: str | None = Field(default=None, max_length=64)
    vision_processing_time_ms: int | None = Field(default=None, ge=0)
    vision_completed_at: datetime | None = None
    vision_started_at: datetime | None = None
    vision_prompt_version: str | None = Field(default=None, max_length=16)
    vision_error_message: str | None = Field(default=None, max_length=2000)
    vision_retry_count: int = Field(default=0, ge=0)
    is_duplicate: bool = False
    duplicate_score: float | None = Field(default=None, ge=0, le=100)
    duplicate_reason: str | None = Field(default=None, max_length=2000)
    duplicate_confidence: float | None = Field(default=None, ge=0, le=1)
    matched_complaint_id: str | None = Field(default=None, max_length=128)
    matched_cluster_id: str | None = Field(default=None, max_length=128)
    submitted_at: datetime
    resolved_at: datetime | None = None


class ComplaintCreate(BaseModel):
    """Fields required to create a complaint."""

    title: str = Field(min_length=5, max_length=256)
    description: str = Field(min_length=10, max_length=5000)
    category: ComplaintCategory
    priority: ComplaintPriority = ComplaintPriority.MEDIUM
    village_id: str = Field(min_length=1, max_length=128)
    village_name: str = Field(max_length=128)
    constituency: str = Field(max_length=128)
    district: str = Field(max_length=128)
    state: str = Field(max_length=64)
    citizen_name: str | None = Field(default=None, max_length=128)
    citizen_phone: str | None = Field(default=None, pattern=r"^\+?[0-9]{10,15}$")
    citizen_email: EmailStr | None = None
    location: GeoLocation | None = None
    landmark: str | None = Field(default=None, max_length=256)
    category_id: str | None = Field(default=None, max_length=128)
    category_name: str | None = Field(default=None, max_length=128)
    category_slug: str | None = Field(default=None, max_length=64)
    image_base64: str | None = None
    image_mime_type: str | None = Field(default=None, max_length=128)
    audio_base64: str | None = None
    audio_mime_type: str | None = Field(default=None, max_length=128)
    audio_duration_seconds: float | None = Field(default=None, ge=0)
    is_anonymous: bool = False
    attachments: list[Attachment] = Field(default_factory=list, max_length=10)
    status: ComplaintStatus = ComplaintStatus.PENDING
    metadata: DocumentMetadataCreate = Field(default_factory=DocumentMetadataCreate)


class ComplaintUpdate(BaseModel):
    """Fields allowed on complaint update."""

    title: str | None = Field(default=None, min_length=5, max_length=256)
    description: str | None = Field(default=None, min_length=10, max_length=5000)
    category: ComplaintCategory | None = None
    category_id: str | None = Field(default=None, max_length=128)
    category_name: str | None = Field(default=None, max_length=128)
    category_slug: str | None = Field(default=None, max_length=64)
    priority: ComplaintPriority | None = None
    status: ComplaintStatus | None = None
    location: GeoLocation | None = None
    cluster_id: str | None = Field(default=None, max_length=128)
    cluster_ref: str | None = None
    ai_analysis: ComplaintAIAnalysis | None = None
    analysis_status: AnalysisStatus | None = None
    analysis_started_at: datetime | None = None
    analysis_completed_at: datetime | None = None
    analysis_model_name: str | None = Field(default=None, max_length=64)
    analysis_processing_time_ms: int | None = Field(default=None, ge=0)
    analysis_prompt_version: str | None = Field(default=None, max_length=16)
    analysis_error_message: str | None = None
    analysis_retry_count: int | None = Field(default=None, ge=0)
    image_analysis: ComplaintImageAnalysis | None = None
    image_analysis_status: AnalysisStatus | None = None
    vision_model: str | None = Field(default=None, max_length=64)
    vision_processing_time_ms: int | None = Field(default=None, ge=0)
    vision_completed_at: datetime | None = None
    vision_started_at: datetime | None = None
    vision_prompt_version: str | None = Field(default=None, max_length=16)
    vision_error_message: str | None = None
    vision_retry_count: int | None = Field(default=None, ge=0)
    is_duplicate: bool | None = None
    duplicate_score: float | None = Field(default=None, ge=0, le=100)
    duplicate_reason: str | None = None
    duplicate_confidence: float | None = Field(default=None, ge=0, le=1)
    matched_complaint_id: str | None = Field(default=None, max_length=128)
    matched_cluster_id: str | None = Field(default=None, max_length=128)
    landmark: str | None = Field(default=None, max_length=256)
    image_base64: str | None = None
    image_mime_type: str | None = Field(default=None, max_length=128)
    audio_base64: str | None = None
    audio_mime_type: str | None = Field(default=None, max_length=128)
    audio_duration_seconds: float | None = Field(default=None, ge=0)
    is_anonymous: bool | None = None
    updated_by: str = Field(default="system", max_length=128)


class ComplaintResponse(ComplaintBase):
    """Complaint document returned from Firestore."""

    id: str
    metadata: DocumentMetadata


class ComplaintSearchFilters(BaseModel):
    """Filter parameters for complaint queries."""

    citizen_email: str | None = None
    constituency: str | None = None
    district: str | None = None
    state: str | None = None
    village_id: str | None = None
    cluster_id: str | None = None
    category: ComplaintCategory | None = None
    category_id: str | None = None
    status: ComplaintStatus | None = None
    priority: ComplaintPriority | None = None
    keyword: str | None = Field(default=None, max_length=64)
    submitted_after: datetime | None = None
    submitted_before: datetime | None = None
