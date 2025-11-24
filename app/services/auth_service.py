"""
Authentication service module for JWT and user authentication logic.

This service follows the Dependency Inversion Principle:
- Depends on abstractions (UserService)
- Dependencies are injected via constructor
- Easy to test with mocks
"""

from datetime import timedelta
from jose import jwt, JWTError
from fastapi.security import OAuth2PasswordBearer

from app.core.config import settings
from app.core.security import ALGORITHM, create_access_token
from app.exceptions.base import UnauthorizedException
from app.services.user_service import UserService
from app.models.user import User
from app.core.logging import logger


class AuthService:
    """
    Authentication service for handling JWT and user authentication.
    
    Responsibilities:
    - User authentication (email/password)
    - JWT token creation
    - JWT token validation
    - Current user retrieval from token
    
    Dependencies are injected, not created:
    - UserService: for user operations (includes DB access via repository)
    
    Note: This service does NOT need direct database access. All DB
    operations are delegated to UserService which handles its own
    repository and transaction management.
    """
    
    oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.API_V1_STR}/auth/login")

    def __init__(self, user_service: UserService):
        """
        Initialize AuthService with injected dependencies.
        
        Args:
            user_service: UserService for user operations
            
        Example:
            ```python
            # In production (via DI):
            service = AuthService(user_service)
            
            # In tests (with mocks):
            mock_user_service = MagicMock(spec=UserService)
            service = AuthService(mock_user_service)
            ```
        """
        self.user_service = user_service

    def create_access_token(self, user: User) -> str:
        """
        Create JWT access token for authenticated user.
        
        Token includes:
        - User ID (as subject)
        - User role
        - Expiration timestamp
        
        Args:
            user: Authenticated user object
            
        Returns:
            str: JWT token string
            
        Example:
            ```python
            user = User(id=1, email="user@example.com", role=UserRole.USER)
            token = service.create_access_token(user)
            # Returns: "eyJhbGciOiJIUzI1NiIs..."
            ```
        """
        logger.debug(f"Creating access token for user {user.email}")

        token = create_access_token(
            subject=user.id,
            role=user.role,
            expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        )
        
        logger.debug("Access token created successfully")
        return token

    def verify_token(self, token: str) -> dict:
        """
        Verify and decode JWT token.
        
        Args:
            token: JWT token string
            
        Returns:
            dict: Decoded token payload with 'sub' (user_id) and 'role'
            
        Raises:
            UnauthorizedException: If token is invalid or expired
            
        Example:
            ```python
            payload = service.verify_token(token)
            user_id = int(payload["sub"])
            role = payload["role"]
            ```
        """
        logger.debug("Verifying token")
        try:
            payload = jwt.decode(
                token, settings.SECRET_KEY, algorithms=[ALGORITHM]
            )
            logger.debug("Token decoded successfully")
            
            # Validate required fields
            if not payload.get("sub") or not payload.get("role"):
                logger.error("Invalid token payload: missing required fields")
                raise UnauthorizedException(detail="Invalid token payload")
                
            return payload
            
        except JWTError as e:
            logger.error(f"JWT validation error: {str(e)}")
            raise UnauthorizedException(detail=f"Invalid token: {str(e)}")

    def get_current_user(self, token: str) -> User:
        """
        Get current authenticated user from JWT token.
        
        Args:
            token: JWT token string
            
        Returns:
            User: Authenticated user object
            
        Raises:
            UnauthorizedException: If token invalid or user not found/inactive
            
        Example:
            ```python
            user = service.get_current_user(token)
            print(f"Current user: {user.email}")
            ```
        """
        logger.debug("Getting current user from token")
        
        # Verify and decode token
        payload = self.verify_token(token)
        user_id = int(payload.get("sub"))
        logger.debug(f"Looking up user with ID: {user_id}")
        
        # Get user from database
        user = self.user_service.get(user_id)
        if not user:
            logger.error(f"User not found with ID: {user_id}")
            raise UnauthorizedException(detail="User not found")
            
        # Check if user is active
        if not user.is_active:
            logger.error(f"User {user.email} is inactive")
            raise UnauthorizedException(detail="Inactive user")
        
        logger.debug(f"Successfully retrieved user: {user.email}")
        return user

    def authenticate_user(self, email: str, password: str) -> User:
        """
        Authenticate user with email and password.
        
        Args:
            email: User email address
            password: Plain text password
            
        Returns:
            User: Authenticated user object
            
        Raises:
            UnauthorizedException: If credentials invalid or user inactive
            
        Example:
            ```python
            try:
                user = service.authenticate_user("user@example.com", "password123")
                token = service.create_access_token(user)
            except UnauthorizedException:
                # Invalid credentials
                pass
            ```
        """
        logger.debug(f"Authenticating user with email: {email}")
        
        # Authenticate via user service
        user = self.user_service.authenticate(email=email, password=password)
        
        if not user:
            logger.error(f"Authentication failed for user: {email}")
            raise UnauthorizedException(detail="Incorrect email or password")
            
        # Check if user is active
        if not user.is_active:
            logger.error(f"User {email} is inactive")
            raise UnauthorizedException(detail="Inactive user")
            
        logger.debug(f"Successfully authenticated user: {email}")
        return user
