from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.services.auth_service import AuthService
from app.services.user_service import UserService
from app.dto.auth import TokenResponse, LoginRequest
from app.dto.user import UserCreate, UserResponse
from app.api.v1.endpoints.metrics import record_login_attempt, record_user_registration

router = APIRouter()


@router.post("/login", response_model=TokenResponse)
def login(
    login_data: LoginRequest,
    db: Session = Depends(get_db)
):
    """
    Login endpoint to get an access token for future requests
    """
    try:
        auth_service = AuthService(db)
        user = auth_service.authenticate_user(email=login_data.email, password=login_data.password)
        record_login_attempt("success")
        return TokenResponse(
            access_token=auth_service.create_access_token(user=user),
            token_type="bearer"
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