from datetime import datetime, timedelta
from typing import Optional
from jose import jwt, JWTError
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.security import ALGORITHM, create_access_token, verify_password
from app.exceptions.base import UnauthorizedException
from app.services.user_service import UserService
from app.models.user import User
from app.core.logging import logger


class AuthService:
    oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.API_V1_STR}/auth/login")

    def __init__(self, db: Session):
        self.db = db
        self.user_service = UserService(db)

    def create_access_token(self, user: User) -> str:
        logger.info(f"Creating access token for user {user.email}")
        expire = datetime.utcnow() + timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )
        token = create_access_token(
            subject=user.id,
            role=user.role,
            expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        )
        logger.info("Access token created successfully")
        return token

    def verify_token(self, token: str) -> dict:
        logger.info("Verifying token")
        try:
            payload = jwt.decode(
                token, settings.SECRET_KEY, algorithms=[ALGORITHM]
            )
            logger.info(f"Token decoded successfully. Payload: {payload}")
            if not payload.get("sub") or not payload.get("role"):
                logger.error("Invalid token payload: missing required fields")
                raise UnauthorizedException(detail="Invalid token payload")
            return payload
        except JWTError as e:
            logger.error(f"JWT validation error: {str(e)}")
            raise UnauthorizedException(detail=f"Invalid token: {str(e)}")

    def get_current_user(self, token: str) -> User:
        logger.info("Getting current user from token")
        payload = self.verify_token(token)
        user_id = int(payload.get("sub"))
        logger.info(f"Looking up user with ID: {user_id}")
        
        user = self.user_service.get(user_id)
        if not user:
            logger.error(f"User not found with ID: {user_id}")
            raise UnauthorizedException(detail="User not found")
        if not user.is_active:
            logger.error(f"User {user.email} is inactive")
            raise UnauthorizedException(detail="Inactive user")
            
        logger.info(f"Successfully retrieved user: {user.email}")
        return user

    def authenticate_user(self, email: str, password: str) -> Optional[User]:
        logger.info(f"Authenticating user with email: {email}")
        user = self.user_service.authenticate(email=email, password=password)
        if not user:
            logger.error(f"Authentication failed for user: {email}")
            raise UnauthorizedException(detail="Incorrect email or password")
        if not user.is_active:
            logger.error(f"User {email} is inactive")
            raise UnauthorizedException(detail="Inactive user")
        logger.info(f"Successfully authenticated user: {email}")
        return user 