from typing import List
from fastapi import APIRouter, Depends, status, Query
from sqlalchemy.orm import Session

from app.api.deps import get_db, get_current_admin_user
from app.services.user_service import UserService
from app.dto.user import UserResponse, UserUpdate, UserFilter, PaginatedUserResponse
from app.models.user import User, UserRole

router = APIRouter()


@router.get("/", response_model=PaginatedUserResponse)
def get_all_users(
    email: str = Query(None, description="Filter by email (partial match)"),
    role: UserRole = Query(None, description="Filter by user role"),
    is_active: bool = Query(None, description="Filter by active status"),
    page: int = Query(1, ge=1, description="Page number"),
    size: int = Query(10, ge=1, le=100, description="Page size"),
    db: Session = Depends(get_db),
    _: User = Depends(get_current_admin_user)
):
    """
    Get all users with filtering and pagination.
    This endpoint is protected and requires admin privileges.
    """
    user_service = UserService(db)
    filter_params = UserFilter(
        email=email,
        role=role,
        is_active=is_active
    )
    return user_service.get_filtered_users(
        filter_params=filter_params,
        page=page,
        size=size
    )


@router.get("/{user_id}", response_model=UserResponse)
def get_user(
    user_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_admin_user)
):
    """
    Get user by ID.
    This endpoint is protected and requires admin privileges.
    """
    user_service = UserService(db)
    return user_service.get(id=user_id)


@router.put("/{user_id}", response_model=UserResponse)
def update_user(
    user_id: int,
    user_update: UserUpdate,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_admin_user)
):
    """
    Update user.
    This endpoint is protected and requires admin privileges.
    """
    user_service = UserService(db)
    return user_service.update_user(user_id=user_id, user_update=user_update)


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_admin_user)
):
    """
    Delete user.
    This endpoint is protected and requires admin privileges.
    """
    user_service = UserService(db)
    user_service.delete(id=user_id)
    return None 