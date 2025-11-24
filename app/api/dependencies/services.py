"""
Service and repository dependencies.

Provides configured instances of services and repositories
with proper dependency injection.
"""

from fastapi import Depends
from sqlalchemy.orm import Session

from app.api.dependencies.database import get_db
from app.services.auth_service import AuthService
from app.services.user_service import UserService
from app.services.password_service import PasswordService
from app.repositories.user_repository import UserRepository


def get_password_service() -> PasswordService:
    """
    Provide PasswordService instance.
    
    Returns:
        PasswordService: Stateless password hashing and validation service
        
    Note:
        PasswordService is stateless, so we create a new instance each time.
        Could be a singleton if we add caching.
    """
    return PasswordService()


def get_user_repository(
    db: Session = Depends(get_db)
) -> UserRepository:
    """
    Provide UserRepository instance with database session.
    
    Args:
        db: Database session from get_db dependency
        
    Returns:
        UserRepository: Configured repository for user data access
        
    Example:
        ```python
        @router.get("/users")
        def get_users(repo: UserRepository = Depends(get_user_repository)):
            return repo.get_all()
        ```
    """
    return UserRepository(db)


def get_user_service(
    repository: UserRepository = Depends(get_user_repository),
    password_service: PasswordService = Depends(get_password_service)
) -> UserService:
    """
    Provide UserService instance with injected dependencies.
    
    This demonstrates proper dependency injection:
    - Repository is injected (not created internally)
    - Password service is injected (not created internally)
    
    Args:
        repository: UserRepository from get_user_repository dependency
        password_service: PasswordService from get_password_service dependency
        
    Returns:
        UserService: Configured service for user business logic
        
    Example:
        ```python
        @router.post("/users")
        def create_user(
            user_data: UserCreate,
            service: UserService = Depends(get_user_service)
        ):
            return service.create_user(user_data)
        ```
        
    Testing:
        ```python
        app.dependency_overrides[get_user_service] = lambda: mock_service
        ```
    """
    return UserService(repository, password_service)


def get_auth_service(
    user_service: UserService = Depends(get_user_service)
) -> AuthService:
    """
    Provide AuthService instance with injected dependencies.
    
    Args:
        user_service: UserService from get_user_service dependency
        
    Returns:
        AuthService: Configured service for authentication logic
        
    Note:
        AuthService no longer needs direct database access.
        All DB operations are handled by UserService via its repository.
        
    Example:
        ```python
        @router.post("/auth/login")
        def login(
            credentials: LoginRequest,
            auth_service: AuthService = Depends(get_auth_service)
        ):
            return auth_service.authenticate_user(...)
        ```
    """
    return AuthService(user_service)

