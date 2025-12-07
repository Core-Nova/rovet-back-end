"""
FastAPI dependencies for authentication and authorization.

Following industry best practices for microservices:
- Token verification without database lookup (for microservices)
- Permission-based access control
- Reusable dependency functions
"""

from typing import Optional, List
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.security import verify_token
from app.dto.token import TokenPayload
from app.models.user import User, UserRole
from app.api.dependencies.database import get_db
from app.services.auth_service import AuthService
from app.core.logging import logger

oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl=f"{settings.API_V1_STR}/auth/login",
    scheme_name="Bearer"
)


def get_token_payload(token: str = Depends(oauth2_scheme)) -> TokenPayload:
    """
    Verify JWT token and return payload (for microservices).
    
    This dependency verifies the token signature and claims without
    requiring database access. Perfect for microservices that only
    need to verify tokens and check permissions.
    
    Usage:
        @router.get("/protected")
        def protected_endpoint(payload: TokenPayload = Depends(get_token_payload)):
            user_id = payload.sub
            permissions = payload.permissions
            ...
    """
    try:
        payload_dict = verify_token(token)
        payload = TokenPayload(**payload_dict)
        
        # Validate token type
        if payload.type != "access":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token type",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        return payload
    except Exception as e:
        logger.error(f"Token verification failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )


def get_current_user(
    db: Session = Depends(get_db),
    token: str = Depends(oauth2_scheme)
) -> User:
    """
    Verify token and return User model (for auth service).
    
    This dependency verifies the token and performs a database lookup
    to return the full User model. Use this in the authentication
    service when you need full user data.
    
    Usage:
        @router.get("/profile")
        def get_profile(user: User = Depends(get_current_user)):
            return user
    """
    auth_service = AuthService(db)
    try:
        return auth_service.get_current_user(token)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
            headers={"WWW-Authenticate": "Bearer"},
        )


def get_current_active_user(
    current_user: User = Depends(get_current_user),
) -> User:
    """Verify user is active."""
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Inactive user"
        )
    return current_user


def require_role(*allowed_roles: UserRole):
    """
    Dependency factory for role-based access control.
    
    Usage:
        @router.get("/admin-only")
        def admin_endpoint(
            payload: TokenPayload = Depends(require_role(UserRole.ADMIN))
        ):
            ...
    """
    def role_checker(payload: TokenPayload = Depends(get_token_payload)) -> TokenPayload:
        user_role = UserRole(payload.role)
        if user_role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Required role: {', '.join(r.value for r in allowed_roles)}"
            )
        return payload
    
    return role_checker


def require_permission(*required_permissions: str):
    """
    Dependency factory for permission-based access control.
    
    Usage:
        @router.delete("/users/{user_id}")
        def delete_user(
            user_id: int,
            payload: TokenPayload = Depends(require_permission("users:delete"))
        ):
            ...
    """
    def permission_checker(payload: TokenPayload = Depends(get_token_payload)) -> TokenPayload:
        user_permissions = set(payload.permissions)
        required = set(required_permissions)
        
        if not required.issubset(user_permissions):
            missing = required - user_permissions
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Missing required permissions: {', '.join(missing)}"
            )
        return payload
    
    return permission_checker


def require_any_permission(*permissions: str):
    """
    Dependency factory for checking if user has ANY of the specified permissions.
    
    Usage:
        @router.get("/users")
        def list_users(
            payload: TokenPayload = Depends(require_any_permission("users:read", "admin:access"))
        ):
            ...
    """
    def permission_checker(payload: TokenPayload = Depends(get_token_payload)) -> TokenPayload:
        user_permissions = set(payload.permissions)
        required = set(permissions)
        
        if not user_permissions.intersection(required):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Missing required permission. Need one of: {', '.join(permissions)}"
            )
        return payload
    
    return permission_checker


# Convenience dependencies
RequireAdmin = require_role(UserRole.ADMIN)
RequireUser = require_role(UserRole.USER, UserRole.ADMIN)

