"""Analytics domain models."""

from datetime import datetime

from pydantic import BaseModel, Field

from app.models.enums.common import AnalyticsReportType
from app.models.schemas.common import DocumentMetadata, DocumentMetadataCreate


class VillageComplaintMetric(BaseModel):
    """Complaint count metric for a single village."""

    village_id: str
    village_name: str
    count: int = Field(ge=0)


class AnalyticsMetrics(BaseModel):
    """Aggregated analytics metrics payload."""

    total_complaints: int = Field(default=0, ge=0)
    resolved_complaints: int = Field(default=0, ge=0)
    pending_complaints: int = Field(default=0, ge=0)
    rejected_complaints: int = Field(default=0, ge=0)
    average_resolution_days: float = Field(default=0, ge=0)
    complaints_by_category: dict[str, int] = Field(default_factory=dict)
    complaints_by_status: dict[str, int] = Field(default_factory=dict)
    complaints_by_priority: dict[str, int] = Field(default_factory=dict)
    top_villages: list[VillageComplaintMetric] = Field(default_factory=list, max_length=20)
    cluster_count: int = Field(default=0, ge=0)
    open_cluster_count: int = Field(default=0, ge=0)
    recommendation_count: int = Field(default=0, ge=0)
    active_recommendation_count: int = Field(default=0, ge=0)
    ai_sentiment_distribution: dict[str, int] = Field(default_factory=dict)
    department_workload: dict[str, int] = Field(default_factory=dict)


class AnalyticsBase(BaseModel):
    """Shared analytics document fields."""

    report_type: AnalyticsReportType
    period_start: datetime
    period_end: datetime
    constituency: str = Field(max_length=128)
    district: str | None = Field(default=None, max_length=128)
    state: str | None = Field(default=None, max_length=64)
    department_id: str | None = Field(default=None, max_length=128)
    village_id: str | None = Field(default=None, max_length=128)
    metrics: AnalyticsMetrics
    generated_at: datetime
    source_complaint_count: int = Field(default=0, ge=0)
    source_recommendation_count: int = Field(default=0, ge=0)


class AnalyticsCreate(BaseModel):
    """Fields required to create an analytics document."""

    report_type: AnalyticsReportType
    period_start: datetime
    period_end: datetime
    constituency: str = Field(max_length=128)
    district: str | None = Field(default=None, max_length=128)
    state: str | None = Field(default=None, max_length=64)
    department_id: str | None = Field(default=None, max_length=128)
    village_id: str | None = Field(default=None, max_length=128)
    metrics: AnalyticsMetrics
    source_complaint_count: int = Field(default=0, ge=0)
    source_recommendation_count: int = Field(default=0, ge=0)
    metadata: DocumentMetadataCreate = Field(default_factory=DocumentMetadataCreate)


class AnalyticsUpdate(BaseModel):
    """Fields allowed on analytics update."""

    metrics: AnalyticsMetrics | None = None
    source_complaint_count: int | None = Field(default=None, ge=0)
    source_recommendation_count: int | None = Field(default=None, ge=0)
    updated_by: str = Field(default="system", max_length=128)


class AnalyticsResponse(AnalyticsBase):
    """Analytics document returned from Firestore."""

    id: str
    metadata: DocumentMetadata


class AnalyticsSearchFilters(BaseModel):
    """Filter parameters for analytics queries."""

    report_type: AnalyticsReportType | None = None
    constituency: str | None = None
    district: str | None = None
    state: str | None = None
    department_id: str | None = None
    village_id: str | None = None
    period_start_after: datetime | None = None
    period_end_before: datetime | None = None
