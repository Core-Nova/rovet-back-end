"""
User management endpoints for admin operations.

All endpoints require admin authentication.
Uses dependency injection for services - no direct database access.
"""

from fastapi import APIRouter, Depends, status, Query

from app.api.dependencies import get_user_service, get_current_admin_user
from app.services.user_service import UserService
from app.dto.user import UserResponse, UserUpdate, UserFilter, PaginatedUserResponse
from app.models.user import User, UserRole

router = APIRouter()


@router.get(
    "/",
    response_model=PaginatedUserResponse,
    summary="List All Users",
    description="Get paginated list of users with optional filtering (Admin only)",
    responses={
        200: {"description": "Paginated list of users"},
        401: {"description": "Not authenticated"},
        403: {"description": "Not authorized (admin required)"}
    }
)
def get_all_users(
    email: str = Query(None, description="Filter by email (partial match)"),
    role: UserRole = Query(None, description="Filter by user role (user/admin)"),
    is_active: bool = Query(None, description="Filter by active status (true/false)"),
    page: int = Query(1, ge=1, description="Page number (1-indexed)"),
    size: int = Query(10, ge=1, le=100, description="Page size (1-100)"),
    user_service: UserService = Depends(get_user_service),
    _: User = Depends(get_current_admin_user)
):
    """
    Get all users with filtering and pagination.
    
    **Authentication Required:** Yes  
    **Authorization:** Admin only
    
    **Filters:**
    - `email`: Partial match on email address
    - `role`: Filter by user role (user/admin)
    - `is_active`: Filter by active status
    
    **Pagination:**
    - `page`: Page number (starts at 1)
    - `size`: Items per page (max 100)
    
    **Usage:**
    ```bash
    # Get all users (first page)
    curl -H "Authorization: Bearer <admin_token>" \\
         "http://localhost:8001/api/v1/users/"
    
    # Filter by email
    curl -H "Authorization: Bearer <admin_token>" \\
         "http://localhost:8001/api/v1/users/?email=john"
    
    # Filter by role and status
    curl -H "Authorization: Bearer <admin_token>" \\
         "http://localhost:8001/api/v1/users/?role=admin&is_active=true"
    
    # Pagination
    curl -H "Authorization: Bearer <admin_token>" \\
         "http://localhost:8001/api/v1/users/?page=2&size=20"
    ```
    
    **Response:**
    ```json
    {
      "items": [...],
      "total": 50,
      "page": 1,
      "size": 10,
      "pages": 5
    }
    ```
    """
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


@router.get(
    "/{user_id}",
    response_model=UserResponse,
    summary="Get User by ID",
    description="Get detailed information for a specific user (Admin only)",
    responses={
        200: {"description": "User details"},
        401: {"description": "Not authenticated"},
        403: {"description": "Not authorized (admin required)"},
        404: {"description": "User not found"}
    }
)
def get_user(
    user_id: int,
    user_service: UserService = Depends(get_user_service),
    _: User = Depends(get_current_admin_user)
):
    """
    Get user by ID.
    
    **Authentication Required:** Yes  
    **Authorization:** Admin only
    
    **Usage:**
    ```bash
    curl -H "Authorization: Bearer <admin_token>" \\
         "http://localhost:8001/api/v1/users/123"
    ```
    """
    return user_service.get(id=user_id)


@router.put(
    "/{user_id}",
    response_model=UserResponse,
    summary="Update User",
    description="Update user information (Admin only)",
    responses={
        200: {"description": "User successfully updated"},
        400: {"description": "Invalid input data"},
        401: {"description": "Not authenticated"},
        403: {"description": "Not authorized (admin required)"},
        404: {"description": "User not found"},
        409: {"description": "Email already in use"}
    }
)
def update_user(
    user_id: int,
    user_update: UserUpdate,
    user_service: UserService = Depends(get_user_service),
    _: User = Depends(get_current_admin_user)
):
    """
    Update user information.
    
    **Authentication Required:** Yes  
    **Authorization:** Admin only
    
    **Updatable Fields:**
    - email (must be unique)
    - password (will be hashed)
    - full_name
    - role
    - is_active
    
    **Business Rules:**
    - If email changes, new email must be unique
    - If password changes, it must meet complexity requirements
    - Partial updates supported (only send fields to update)
    
    **Usage:**
    ```bash
    # Update email only
    curl -X PUT "http://localhost:8001/api/v1/users/123" \\
         -H "Authorization: Bearer <admin_token>" \\
         -H "Content-Type: application/json" \\
         -d '{"email": "newemail@example.com"}'
    
    # Update multiple fields
    curl -X PUT "http://localhost:8001/api/v1/users/123" \\
         -H "Authorization: Bearer <admin_token>" \\
         -H "Content-Type: application/json" \\
         -d '{
           "email": "newemail@example.com",
           "full_name": "New Name",
           "is_active": false
         }'
    ```
    """
    return user_service.update_user(user_id=user_id, user_update=user_update)


@router.delete(
    "/{user_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete User",
    description="Delete a user account (Admin only)",
    responses={
        204: {"description": "User successfully deleted"},
        401: {"description": "Not authenticated"},
        403: {"description": "Not authorized (admin required)"},
        404: {"description": "User not found"}
    }
)
def delete_user(
    user_id: int,
    user_service: UserService = Depends(get_user_service),
    _: User = Depends(get_current_admin_user)
):
    """
    Delete user.
    
    **Authentication Required:** Yes  
    **Authorization:** Admin only
    
    **Warning:**
    - This is a permanent deletion
    - Consider using is_active=false for soft deletion instead
    
    **Usage:**
    ```bash
    curl -X DELETE "http://localhost:8001/api/v1/users/123" \\
         -H "Authorization: Bearer <admin_token>"
    ```
    
    **Response:**
    - 204 No Content (empty response body)
    """
    user_service.delete(id=user_id)
    return None
