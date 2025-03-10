from fastapi import APIRouter

from app.controllers import auth_controller, user_controller
from app.api.v1.endpoints import health

api_router = APIRouter()

# Health check
api_router.include_router(health.router, tags=["health"])

# Authentication
api_router.include_router(
    auth_controller.router,
    prefix="/auth",
    tags=["authentication"]
)

# Users
api_router.include_router(
    user_controller.router,
    prefix="/users",
    tags=["users"]
)

# Import and include other routers here
# Example:
# from app.api.v1.endpoints import items, users
# api_router.include_router(items.router, prefix="/items", tags=["items"])
# api_router.include_router(users.router, prefix="/users", tags=["users"]) 