"""Health check response schemas."""

from pydantic import BaseModel, Field


class ServiceStatus(BaseModel):
    """Status of an individual service dependency."""

    name: str
    status: str = Field(description="healthy | unhealthy")
    message: str | None = None


class HealthResponse(BaseModel):
    """Health check API response."""

    success: bool = True
    status: str = Field(description="healthy | degraded | unhealthy")
    app_name: str
    version: str
    environment: str
    services: list[ServiceStatus]
