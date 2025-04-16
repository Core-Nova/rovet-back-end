from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.api import deps
from app.core.config import settings
from app.dto.user import UserFilter, UserUpdate
from app.models.user import User, UserRole
from app.repositories.user_repository import UserRepository
from app.schemas.user import User, UserCreate, UserUpdate as UserUpdateSchema, PaginatedUserResponse

router = APIRouter()

@router.get("/", response_model=PaginatedUserResponse)
def get_all_users(
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
    email: str = None,
    role: UserRole = None,
    is_active: bool = None,
    page: int = Query(1, ge=1),
    size: int = Query(settings.DEFAULT_PAGE_SIZE, ge=1, le=settings.MAX_PAGE_SIZE)
) -> Any:
    """
    Get all users with optional filtering and pagination.
    Only admin users can access this endpoint.
    """
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(status_code=403, detail="Not enough permissions")

    user_repo = UserRepository(db)
    filter_params = UserFilter(email=email, role=role, is_active=is_active)
    users, total = user_repo.get_filtered_users(filter_params, page, size)
    
    return {
        "items": [User.from_orm(user) for user in users],
        "total": total,
        "page": page,
        "size": size,
        "pages": (total + size - 1) // size
    }

@router.get("/{user_id}", response_model=User)
def get_user_by_id(
    user_id: int,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    """
    Get a specific user by ID.
    Only admin users can access this endpoint.
    """
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(status_code=403, detail="Not enough permissions")

    user_repo = UserRepository(db)
    user = user_repo.get_by_id(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    return User.from_orm(user)

@router.put("/{user_id}", response_model=User)
def update_user(
    user_id: int,
    user_update: UserUpdate,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    """
    Update a user's information.
    Only admin users can access this endpoint.
    """
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    user_repo = UserRepository(db)
    user = user_repo.get_by_id(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    updated_user = user_repo.update(user, user_update)
    return User.from_orm(updated_user)

@router.delete("/{user_id}", status_code=204)
def delete_user(
    user_id: int,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
) -> None:
    """
    Delete a user.
    Only admin users can access this endpoint.
    """
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    user_repo = UserRepository(db)
    user = user_repo.get_by_id(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    user_repo.delete(user) 