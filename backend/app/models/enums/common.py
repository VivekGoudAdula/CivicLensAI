"""Shared enumeration types for CivicLens AI domain models."""

from enum import StrEnum


class ComplaintCategory(StrEnum):
    ROADS = "roads"
    WATER = "water"
    ELECTRICITY = "electricity"
    SANITATION = "sanitation"
    HEALTH = "health"
    EDUCATION = "education"
    CORRUPTION = "corruption"
    EMPLOYMENT = "employment"
    HOUSING = "housing"
    OTHER = "other"
    GARBAGE = "garbage"
    STREET_LIGHTS = "street_lights"
    DRAINAGE = "drainage"
    PUBLIC_TRANSPORT = "public_transport"
    ENVIRONMENT = "environment"


class ComplaintPriority(StrEnum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class ComplaintStatus(StrEnum):
    PENDING = "pending"
    SUBMITTED = "submitted"
    UNDER_REVIEW = "under_review"
    CLUSTERED = "clustered"
    IN_PROGRESS = "in_progress"
    RESOLVED = "resolved"
    REJECTED = "rejected"
    CLOSED = "closed"


class ClusterStatus(StrEnum):
    OPEN = "open"
    ANALYZING = "analyzing"
    RECOMMENDED = "recommended"
    ASSIGNED = "assigned"
    RESOLVED = "resolved"
    ARCHIVED = "archived"


class RecommendationStatus(StrEnum):
    DRAFT = "draft"
    PENDING_REVIEW = "pending_review"
    APPROVED = "approved"
    ASSIGNED = "assigned"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    REJECTED = "rejected"


class RecommendationPriority(StrEnum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"


class DepartmentCategory(StrEnum):
    INFRASTRUCTURE = "infrastructure"
    HEALTH = "health"
    EDUCATION = "education"
    SANITATION = "sanitation"
    WATER = "water"
    ELECTRICITY = "electricity"
    AGRICULTURE = "agriculture"
    ADMINISTRATION = "administration"
    WOMEN_WELFARE = "women_welfare"
    RURAL_DEVELOPMENT = "rural_development"


class AnalyticsReportType(StrEnum):
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    CONSTITUENCY_SNAPSHOT = "constituency_snapshot"
    DEPARTMENT_PERFORMANCE = "department_performance"
    CLUSTER_SUMMARY = "cluster_summary"
    VILLAGE_SUMMARY = "village_summary"


class SentimentLabel(StrEnum):
    POSITIVE = "positive"
    NEUTRAL = "neutral"
    NEGATIVE = "negative"
    MIXED = "mixed"


class AnalysisStatus(StrEnum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
