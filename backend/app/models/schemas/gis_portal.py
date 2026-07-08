"""GIS map API schemas for constituency intelligence visualization."""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field


class GisBounds(BaseModel):
    """Geographic bounding box for map viewport."""

    south: float
    west: float
    north: float
    east: float
    center_lat: float
    center_lng: float


class GisComplaintPin(BaseModel):
    """Geo-located complaint marker for the constituency map."""

    id: str
    title: str
    description: str
    latitude: float
    longitude: float
    category: str
    department: str
    priority: str
    severity: str | None = None
    status: str
    village_name: str
    cluster_id: str | None = None
    cluster_title: str | None = None
    ai_summary: str | None = None
    ai_confidence: float | None = None
    has_image: bool = False
    address: str | None = None
    submitted_at: datetime
    heat_weight: float = Field(ge=0, le=1, description="Normalized weight for heatmap layer")


class GisClusterMarker(BaseModel):
    """Geo-located cluster marker with aggregate intelligence."""

    id: str
    title: str
    latitude: float
    longitude: float
    complaint_count: int
    average_priority: float
    highest_severity: str | None = None
    representative_complaint_id: str | None = None
    cluster_score: float = Field(ge=0, le=100)
    department: str | None = None
    village_name: str | None = None
    hotspot_score: float = 0.0
    heat_weight: float = Field(ge=0, le=1)


class GisMapResponse(BaseModel):
    """Complete GIS payload for interactive constituency map."""

    success: bool = True
    complaints: list[GisComplaintPin] = Field(default_factory=list)
    clusters: list[GisClusterMarker] = Field(default_factory=list)
    bounds: GisBounds | None = None
    total_complaints: int = 0
    total_clusters: int = 0
    last_updated_at: datetime
