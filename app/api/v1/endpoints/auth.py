"""
Authentication endpoints for user registration, login, and profile.

All endpoints use dependency injection for services.
No direct database access or manual service instantiation.
"""

from fastapi import APIRouter, Depends, status
from fastapi.security import OAuth2PasswordBearer

from app.api.dependencies import get_auth_service, get_user_service, get_current_user
from app.services.auth_service import AuthService
from app.services.user_service import UserService
from app.dto.auth import TokenResponse, LoginRequest
from app.dto.user import UserCreate, UserResponse
from app.models.user import User
from app.api.v1.endpoints.metrics import record_login_attempt, record_user_registration

router = APIRouter()


@router.post(
    "/login",
    response_model=TokenResponse,
    status_code=status.HTTP_200_OK,
    summary="User Login",
    description="Authenticate user with email and password to receive JWT token",
    responses={
        200: {
            "description": "Successfully authenticated",
            "content": {
                "application/json": {
                    "example": {
                        "access_token": "eyJhbGciOiJIUzI1NiIs...",
                        "token_type": "bearer"
                    }
                }
            }
        },
        401: {"description": "Invalid credentials or inactive user"}
    }
)
def login(
    login_data: LoginRequest,
    auth_service: AuthService = Depends(get_auth_service)
):
    """
    Login endpoint to get an access token for future requests.
    
    **Process:**
    1. Validate email and password
    2. Check user is active
    3. Generate JWT token
    4. Return token
    
    **Usage:**
    ```bash
    curl -X POST "http://localhost:8001/api/v1/auth/login" \\
         -H "Content-Type: application/json" \\
         -d '{"email": "user@example.com", "password": "password123"}'
    ```
    
    **Response:**
    Use the returned token in subsequent requests:
    ```bash
    curl -H "Authorization: Bearer <token>" http://localhost:8001/api/v1/users/
    ```
    """
    try:
        user = auth_service.authenticate_user(
            email=login_data.email,
            password=login_data.password
        )
        record_login_attempt("success")
        
        return TokenResponse(
            access_token=auth_service.create_access_token(user=user),
            token_type="bearer"
        )
    except Exception as e:
        record_login_attempt("failure")
        raise e


@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="User Registration",
    description="Register a new user account",
    responses={
        201: {
            "description": "User successfully registered",
            "content": {
                "application/json": {
                    "example": {
                        "id": 1,
                        "email": "user@example.com",
                        "full_name": "John Doe",
                        "role": "user",
                        "is_active": True,
                        "created_at": "2024-01-01T00:00:00"
                    }
                }
            }
        },
        400: {"description": "Invalid input data"},
        409: {"description": "Email already registered"}
    }
)
def register(
    user_create: UserCreate,
    user_service: UserService = Depends(get_user_service)
):
    """
    Register new user.
    
    **Requirements:**
    - Email must be valid and unique
    - Password must meet complexity requirements (see PasswordService)
    - Full name is required
    
    **Business Rules:**
    - New users are created with role=USER
    - New users are active by default
    - Password is hashed before storage
    
    **Usage:**
    ```bash
    curl -X POST "http://localhost:8001/api/v1/auth/register" \\
         -H "Content-Type: application/json" \\
         -d '{
           "email": "newuser@example.com",
           "password": "SecurePass123!",
           "full_name": "Jane Doe"
         }'
    ```
    """
    user = user_service.create_user(user_create=user_create)
    record_user_registration()
    return user


@router.get(
    "/me",
    response_model=UserResponse,
    summary="Get Current User",
    description="Get profile information for the currently authenticated user",
    responses={
        200: {
            "description": "Current user profile",
            "content": {
                "application/json": {
                    "example": {
                        "id": 1,
                        "email": "user@example.com",
                        "full_name": "John Doe",
                        "role": "user",
                        "is_active": True,
                        "created_at": "2024-01-01T00:00:00"
                    }
                }
            }
        },
        401: {"description": "Not authenticated or invalid token"}
    }
)
def get_current_user_profile(
    current_user: User = Depends(get_current_user)
):
    """
    Get current authenticated user profile.
    
    **Authentication Required:** Yes  
    **Authorization:** Any authenticated user
    
    **Usage:**
    ```bash
    curl -X GET "http://localhost:8001/api/v1/auth/me" \\
         -H "Authorization: Bearer <your_token>"
    ```
    
    **Returns:**
    - User profile information
    - Does NOT include password hash
    """
    return current_user
