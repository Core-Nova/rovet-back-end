"""
Dependency injection providers for the application.

This package contains all FastAPI dependency providers organized by domain:
- database: Database session management
- services: Service and repository dependencies
- auth: Authentication and authorization
- validation: Request validation utilities

Following SOLID principles:
- Dependencies are injected, not created
- Easy to test with overrides
- Clear dependency graph
"""

from app.api.dependencies.database import get_db
from app.api.dependencies.services import (
    get_password_service,
    get_user_repository,
    get_user_service,
    get_auth_service,
)
from app.api.dependencies.auth import (
    oauth2_scheme,
    get_current_user,
    get_current_active_user,
    get_current_admin_user,
)
from app.api.dependencies.validation import validate_pagination

__all__ = [
    "get_db",
    "get_password_service",
    "get_user_repository",
    "get_user_service",
    "get_auth_service",
    "oauth2_scheme",
    "get_current_user",
    "get_current_active_user",
    "get_current_admin_user",
    "validate_pagination",
]

