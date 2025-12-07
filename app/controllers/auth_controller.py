from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.config import settings
from app.api.deps import get_db
from app.services.auth_service import AuthService
from app.services.user_service import UserService
from app.dto.auth import LoginRequest
from app.dto.token import TokenResponse, RefreshTokenRequest
from app.dto.user import UserCreate, UserResponse
from app.api.v1.endpoints.metrics import record_login_attempt, record_user_registration

router = APIRouter()


@router.post("/login", response_model=TokenResponse)
def login(
    login_data: LoginRequest,
    db: Session = Depends(get_db)
):
    """
    Login endpoint to get access and refresh tokens.
    
    Returns both access token (short-lived) and refresh token (long-lived)
    following OAuth 2.0 best practices.
    """
    try:
        auth_service = AuthService(db)
        user = auth_service.authenticate_user(email=login_data.email, password=login_data.password)
        record_login_attempt("success")
        
        access_token, refresh_token = auth_service.create_tokens(user)
        
        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer",
            expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
        )
    except Exception as e:
        record_login_attempt("failure")
        raise e


@router.post("/register", response_model=UserResponse)
def register(user_create: UserCreate, db: Session = Depends(get_db)):
    """
    Register new user
    """
    user_service = UserService(db)
    user = user_service.create_user(user_create=user_create)
    record_user_registration()
    return user


@router.post("/refresh", response_model=TokenResponse)
def refresh_token(
    refresh_data: RefreshTokenRequest,
    db: Session = Depends(get_db)
):
    """
    Refresh access token using a refresh token.
    
    This endpoint allows clients to obtain new access tokens without
    requiring user re-authentication.
    """
    try:
        auth_service = AuthService(db)
        access_token, refresh_token = auth_service.refresh_access_token(refresh_data.refresh_token)
        
        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer",
            expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
        )
    except Exception as e:
        raise HTTPException(status_code=401, detail=str(e))


@router.get("/me", response_model=UserResponse)
def get_current_user(
    db: Session = Depends(get_db),
    token: str = Depends(AuthService.oauth2_scheme)
):
    """
    Get current user
    """
    auth_service = AuthService(db)
    return auth_service.get_current_user(token) 