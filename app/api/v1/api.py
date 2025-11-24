"""
API router aggregation for version 1.

All endpoint routers are registered here.
Uses refactored endpoints with dependency injection.
"""

from fastapi import APIRouter

# Import refactored endpoints (NOT controllers!)
from app.api.v1.endpoints import auth, users, health, metrics

# Create main API router
api_router = APIRouter()

# Register endpoint routers
# Order matters for route matching!

# Health and metrics (no prefix)
api_router.include_router(
    health.router,
    tags=["health"],
    responses={404: {"description": "Not found"}}
)

api_router.include_router(
    metrics.router,
    tags=["metrics"],
    responses={404: {"description": "Not found"}}
)

# Authentication endpoints
api_router.include_router(
    auth.router,
    prefix="/auth",
    tags=["authentication"],
    responses={
        401: {"description": "Not authenticated"},
        422: {"description": "Validation error"}
    }
)

# User management endpoints (admin only)
api_router.include_router(
    users.router,
    prefix="/users",
    tags=["users"],
    responses={
        401: {"description": "Not authenticated"},
        403: {"description": "Not authorized"},
        422: {"description": "Validation error"}
    }
)

# Note: Controllers directory should be deleted after migration
# Old imports (REMOVED):
# from app.controllers import auth_controller, user_controller
