"""API v1 router aggregation."""

from fastapi import APIRouter

from app.api.v1.endpoints import analytics, auth, categories, clusters, complaints, gis, health, priority, recommendations, search

api_router = APIRouter()
api_router.include_router(health.router)
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(complaints.router, prefix="/complaints", tags=["complaints"])
api_router.include_router(categories.router, prefix="/categories", tags=["categories"])
api_router.include_router(clusters.router, prefix="/clusters", tags=["clusters"])
api_router.include_router(priority.router, prefix="/priority", tags=["priority"])
api_router.include_router(analytics.router, prefix="/analytics", tags=["analytics"])
api_router.include_router(gis.router, prefix="/gis", tags=["gis"])
api_router.include_router(recommendations.router, prefix="/recommendations", tags=["recommendations"])
api_router.include_router(search.router, prefix="/search", tags=["search"])
