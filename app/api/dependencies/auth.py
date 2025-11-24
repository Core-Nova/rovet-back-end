"""
Authentication and authorization dependencies.

Provides user authentication and role-based access control.
"""

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

from app.core.config import settings
from app.models.user import User, UserRole
from app.services.auth_service import AuthService
from app.api.dependencies.services import get_auth_service


oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.API_V1_STR}/auth/login")


def get_current_user(
    token: str = Depends(oauth2_scheme),
    auth_service: AuthService = Depends(get_auth_service)
) -> User:
    """
    Get currently authenticated user from JWT token.
    
    Args:
        token: JWT token from Authorization header
        auth_service: AuthService for token validation
        
    Returns:
        User: Authenticated user object
        
    Raises:
        HTTPException: 401 if token is invalid or user not found
        
    Example:
        ```python
        @router.get("/me")
        def get_me(current_user: User = Depends(get_current_user)):
            return current_user
        ```
    """
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
    """
    Get currently authenticated and active user.
    
    Args:
        current_user: User from get_current_user dependency
        
    Returns:
        User: Authenticated and active user
        
    Raises:
        HTTPException: 400 if user is inactive
        
    Example:
        ```python
        @router.get("/profile")
        def get_profile(user: User = Depends(get_current_active_user)):
            return user
        ```
    """
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user"
        )
    return current_user


def get_current_admin_user(
    current_user: User = Depends(get_current_user),
) -> User:
    """
    Get currently authenticated user with admin privileges.
    
    Args:
        current_user: User from get_current_user dependency
        
    Returns:
        User: Authenticated admin user
        
    Raises:
        HTTPException: 403 if user is not an admin
        
    Example:
        ```python
        @router.get("/admin/users")
        def get_all_users(admin: User = Depends(get_current_admin_user)):
            return {"users": [...]}
        ```
    """
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="The user doesn't have enough privileges",
        )
    return current_user

