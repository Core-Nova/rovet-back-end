from datetime import timedelta
from typing import Optional
from jose import JWTError
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.security import create_access_token, create_refresh_token, verify_token
from app.exceptions.base import UnauthorizedException
from app.services.user_service import UserService
from app.models.user import User
from app.core.logging import logger


class AuthService:
    oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.API_V1_STR}/auth/login")

    def __init__(self, db: Session):
        self.db = db
        self.user_service = UserService(db)

    def create_tokens(self, user: User) -> tuple[str, str]:
        """
        Create both access and refresh tokens for a user.
        
        Returns:
            Tuple of (access_token, refresh_token)
        """
        logger.info(f"Creating tokens for user {user.email}")

        # Include additional user information in token
        additional_claims = {
            "email": user.email,
            "is_active": user.is_active,
        }
        if user.full_name:
            additional_claims["name"] = user.full_name

        access_token = create_access_token(
            subject=user.id,
            role=user.role,
            expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES),
            additional_claims=additional_claims
        )
        
        refresh_token = create_refresh_token(
            subject=user.id,
            expires_delta=timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
        )
        
        logger.info(f"Tokens created successfully with algorithm {settings.JWT_ALGORITHM}")
        return access_token, refresh_token
    
    def create_access_token(self, user: User) -> str:
        """
        Create a JWT access token for a user (legacy method).
        
        For new code, use create_tokens() to get both access and refresh tokens.
        """
        access_token, _ = self.create_tokens(user)
        return access_token

    def verify_token(self, token: str) -> dict:
        """
        Verify a JWT token and return its payload.
        
        Uses RS256 (RSA) or HS256 (HMAC) based on configuration.
        For microservices, RS256 is recommended as the public key can be shared.
        """
        logger.info("Verifying token")
        try:
            payload = verify_token(token)
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
    
    def refresh_access_token(self, refresh_token: str) -> tuple[str, str]:
        """
        Create new access and refresh tokens from a refresh token.
        
        Args:
            refresh_token: Valid refresh token
            
        Returns:
            Tuple of (new_access_token, new_refresh_token)
        """
        logger.info("Refreshing access token")
        
        # Verify refresh token
        payload = verify_token(refresh_token)
        
        # Check token type
        if payload.get("type") != "refresh":
            raise UnauthorizedException(detail="Invalid token type")
        
        # Get user from token
        user_id = int(payload.get("sub"))
        user = self.user_service.get(user_id)
        
        if not user:
            raise UnauthorizedException(detail="User not found")
        if not user.is_active:
            raise UnauthorizedException(detail="Inactive user")
        
        # Create new tokens
        return self.create_tokens(user) 