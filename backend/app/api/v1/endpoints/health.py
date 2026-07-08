"""Health check endpoint."""

from fastapi import APIRouter, status

from app.api.deps import SettingsDep
from app.models.schemas.health import HealthResponse, ServiceStatus
from app.services.firebase import verify_firestore_connection
from app.services.gemini import get_configured_model_name, verify_gemini_connection

router = APIRouter(tags=["health"])


@router.get(
    "/health",
    response_model=HealthResponse,
    status_code=status.HTTP_200_OK,
    summary="Application health check",
    description="Returns the health status of the API and its dependencies.",
)
async def health_check(settings: SettingsDep) -> HealthResponse:
    """Return application and dependency health status."""
    firestore_healthy = verify_firestore_connection()
    gemini_healthy = verify_gemini_connection()

    services = [
        ServiceStatus(
            name="firestore",
            status="healthy" if firestore_healthy else "unhealthy",
            message="Connected" if firestore_healthy else "Connection failed",
        ),
        ServiceStatus(
            name="gemini",
            status="healthy" if gemini_healthy else "unhealthy",
            message=(
                f"Model {get_configured_model_name()} ready"
                if gemini_healthy
                else "Not initialized"
            ),
        ),
    ]

    all_healthy = firestore_healthy and gemini_healthy
    any_healthy = firestore_healthy or gemini_healthy

    if all_healthy:
        overall_status = "healthy"
    elif any_healthy:
        overall_status = "degraded"
    else:
        overall_status = "unhealthy"

    return HealthResponse(
        success=all_healthy,
        status=overall_status,
        app_name=settings.app_name,
        version=settings.app_version,
        environment=settings.environment,
        services=services,
    )
