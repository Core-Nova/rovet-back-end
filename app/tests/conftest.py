"""
Pytest configuration and fixtures for all test types.

Provides fixtures for:
- Unit tests (mocked dependencies)
- Integration tests (real DB, real services)
- E2E tests (full application, real DB)
- Database tests (real DB operations)
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool
from unittest.mock import MagicMock
from typing import Generator
import os

from app.db.session import Base
from app.main import app
from app.models.user import User, UserRole
from app.api.dependencies import (
    get_db,
    get_user_service,
    get_auth_service,
    get_user_repository,
    get_password_service
)
from app.services.user_service import UserService
from app.services.auth_service import AuthService
from app.services.password_service import PasswordService
from app.repositories.user_repository import UserRepository


# ==================== Database Fixtures ====================

# Use in-memory SQLite for tests (fast)
SQLALCHEMY_TEST_DATABASE_URL = "sqlite:///:memory:"

# Or use file-based SQLite (persistent between test runs)
# SQLALCHEMY_TEST_DATABASE_URL = "sqlite:///./test.db"


@pytest.fixture(scope="session")
def test_db_engine():
    """
    Create test database engine (session-scoped).
    
    Uses SQLite in-memory for speed.
    All tables are created once per test session.
    """
    engine = create_engine(
        SQLALCHEMY_TEST_DATABASE_URL,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,  # Keep one connection for in-memory DB
    )
    
    # Create all tables
    Base.metadata.create_all(bind=engine)
    
    yield engine
    
    # Cleanup
    Base.metadata.drop_all(bind=engine)
    engine.dispose()


@pytest.fixture(scope="function")
def db(test_db_engine) -> Generator[Session, None, None]:
    """
    Provide clean database session for each test.
    
    - Creates new session
    - Clears all data before test
    - Auto-rollback after test
    
    Use for: Integration tests, DB tests, E2E tests
    """
    TestingSessionLocal = sessionmaker(
        autocommit=False,
        autoflush=False,
        bind=test_db_engine
    )
    
    session = TestingSessionLocal()
    
    # Clear all tables before each test
    for table in reversed(Base.metadata.sorted_tables):
        session.execute(table.delete())
    session.commit()
    
    yield session
    
    # Rollback any uncommitted changes
    session.rollback()
    session.close()


@pytest.fixture(scope="function")
def clean_db(db):
    """
    Alias for db fixture with clearer name for E2E tests.
    
    Use for: E2E tests where you want explicit clean state
    """
    yield db


# ==================== Mock Fixtures (Unit Tests) ====================

@pytest.fixture
def mock_db():
    """
    Mock database session.
    
    Use for: Unit tests where you don't want real DB
    """
    mock_session = MagicMock(spec=Session)
    mock_session.query.return_value = MagicMock()
    mock_session.add = MagicMock()
    mock_session.commit = MagicMock()
    mock_session.rollback = MagicMock()
    mock_session.close = MagicMock()
    mock_session.refresh = MagicMock()
    return mock_session


@pytest.fixture
def mock_user_repository():
    """
    Mock UserRepository with common return values.
    
    Use for: Unit tests of services that depend on repository
    """
    mock_repo = MagicMock(spec=UserRepository)
    
    # Common mocked behaviors
    mock_repo.get_by_email.return_value = None  # No user found (default)
    mock_repo.get.return_value = None
    mock_repo.create_with_password.return_value = MagicMock(
        id=1,
        email="test@example.com",
        full_name="Test User",
        role=UserRole.USER,
        is_active=True
    )
    
    return mock_repo


@pytest.fixture
def mock_password_service():
    """
    Mock PasswordService.
    
    Use for: Unit tests that don't need real password hashing
    """
    mock_service = MagicMock(spec=PasswordService)
    mock_service.get_password_hash.return_value = "hashed_password"
    mock_service.verify_password.return_value = True
    mock_service.validate_password.return_value = None  # No exception
    return mock_service


@pytest.fixture
def mock_user_service():
    """
    Mock UserService with common return values.
    
    Use for: Unit tests of endpoints or services that depend on UserService
    """
    mock_service = MagicMock(spec=UserService)
    
    mock_user = MagicMock(
        id=1,
        email="test@example.com",
        full_name="Test User",
        role=UserRole.USER,
        is_active=True
    )
    
    mock_service.create_user.return_value = mock_user
    mock_service.get.return_value = mock_user
    mock_service.authenticate.return_value = mock_user
    mock_service.get_by_email.return_value = mock_user
    
    return mock_service


@pytest.fixture
def mock_auth_service():
    """
    Mock AuthService with common return values.
    
    Use for: Unit tests of endpoints that need authentication
    """
    mock_service = MagicMock(spec=AuthService)
    
    mock_user = MagicMock(
        id=1,
        email="test@example.com",
        full_name="Test User",
        role=UserRole.USER,
        is_active=True
    )
    
    mock_service.authenticate_user.return_value = mock_user
    mock_service.create_access_token.return_value = "mock_jwt_token"
    mock_service.get_current_user.return_value = mock_user
    mock_service.verify_token.return_value = {
        "sub": "1",
        "role": UserRole.USER.value
    }
    
    return mock_service


# ==================== Real Service Fixtures (Integration Tests) ====================

@pytest.fixture
def password_service():
    """
    Real PasswordService instance.
    
    Use for: Integration tests, E2E tests
    """
    return PasswordService()


@pytest.fixture
def user_repository(db):
    """
    Real UserRepository with test database.
    
    Use for: Integration tests, DB tests
    """
    return UserRepository(db)


@pytest.fixture
def user_service(user_repository, password_service):
    """
    Real UserService with real dependencies and test database.
    
    Use for: Integration tests, E2E tests
    """
    return UserService(user_repository, password_service)


@pytest.fixture
def auth_service(user_service):
    """
    Real AuthService with real dependencies and test database.
    
    Use for: Integration tests, E2E tests
    
    Note: AuthService no longer needs direct db access.
    All DB operations are handled through UserService.
    """
    return AuthService(user_service)


# ==================== Test Client Fixtures ====================

@pytest.fixture
def client(db):
    """
    Default test client with real database (for backward compatibility).
    
    - Uses real test database
    - Uses real services
    - Alias for client_integration
    
    Use for: General API tests
    """
    def override_get_db():
        yield db
    
    app.dependency_overrides[get_db] = override_get_db
    
    with TestClient(app) as test_client:
        yield test_client
    
    app.dependency_overrides.clear()


@pytest.fixture
def client_unit(mock_db):
    """
    Test client with mocked database (UNIT TESTS).
    
    - Uses mock database
    - Fast (no real DB operations)
    - Override other dependencies as needed
    
    Use for: Unit tests of API endpoints
    
    Example:
        def test_login_unit(client_unit, mock_auth_service):
            app.dependency_overrides[get_auth_service] = lambda: mock_auth_service
            response = client_unit.post("/api/v1/auth/login", ...)
    """
    def override_get_db():
        yield mock_db
    
    app.dependency_overrides[get_db] = override_get_db
    
    with TestClient(app) as test_client:
        yield test_client
    
    app.dependency_overrides.clear()


@pytest.fixture
def client_integration(db):
    """
    Test client with real database (INTEGRATION TESTS).
    
    - Uses real test database
    - Uses real services
    - Tests actual integration
    
    Use for: Integration tests of API endpoints
    
    Example:
        def test_login_integration(client_integration):
            # Uses real DB, real services
            response = client_integration.post("/api/v1/auth/register", ...)
    """
    def override_get_db():
        yield db
    
    app.dependency_overrides[get_db] = override_get_db
    
    with TestClient(app) as test_client:
        yield test_client
    
    app.dependency_overrides.clear()


@pytest.fixture
def client_e2e(clean_db):
    """
    Test client for END-TO-END tests.
    
    - Uses real test database
    - Uses real services
    - Minimal mocking (only external APIs if needed)
    - Tests complete workflows
    
    Use for: E2E tests of complete user journeys
    
    Example:
        def test_user_registration_flow_e2e(client_e2e):
            # 1. Register
            register_response = client_e2e.post("/api/v1/auth/register", ...)
            # 2. Login
            login_response = client_e2e.post("/api/v1/auth/login", ...)
            # 3. Use token to access protected route
            ...
    """
    def override_get_db():
        yield clean_db
    
    app.dependency_overrides[get_db] = override_get_db
    
    with TestClient(app) as test_client:
        yield test_client
    
    app.dependency_overrides.clear()


# ==================== Helper Fixtures ====================

@pytest.fixture
def test_user(user_service):
    """
    Create a test user in the database.
    
    Use for: Tests that need an existing user
    
    Returns:
        User: Created user object
    """
    from app.dto.user import UserCreate
    
    user_data = UserCreate(
        email="testuser@example.com",
        password="TestPass123!",
        full_name="Test User"
    )
    return user_service.create_user(user_data)


@pytest.fixture
def test_admin(user_service, db):
    """
    Create a test admin user in the database.
    
    Use for: Tests that need admin privileges
    
    Returns:
        User: Created admin user object
    """
    from app.dto.user import UserCreate
    
    user_data = UserCreate(
        email="admin@example.com",
        password="AdminPass123!",
        full_name="Admin User"
    )
    admin = user_service.create_user(user_data)
    
    # Upgrade to admin
    admin.role = UserRole.ADMIN
    db.commit()
    db.refresh(admin)
    
    return admin


@pytest.fixture
def auth_token(auth_service, test_user):
    """
    Get auth token for test user.
    
    Use for: Tests that need authenticated requests
    
    Returns:
        str: JWT token
    """
    return auth_service.create_access_token(test_user)


@pytest.fixture
def admin_token(auth_service, test_admin):
    """
    Get auth token for admin user.
    
    Use for: Tests that need admin authentication
    
    Returns:
        str: JWT token for admin
    """
    return auth_service.create_access_token(test_admin)


@pytest.fixture
def auth_headers(auth_token):
    """
    Get authorization headers for test user.
    
    Use for: Tests making authenticated requests
    
    Returns:
        dict: Headers with Authorization
    """
    return {"Authorization": f"Bearer {auth_token}"}


@pytest.fixture
def admin_headers(admin_token):
    """
    Get authorization headers for admin user.
    
    Use for: Tests making admin requests
    
    Returns:
        dict: Headers with admin Authorization
    """
    return {"Authorization": f"Bearer {admin_token}"}


# ==================== Pytest Configuration ====================

def pytest_configure(config):
    """
    Configure pytest with custom markers.
    """
    config.addinivalue_line("markers", "unit: Unit tests (fast, isolated)")
    config.addinivalue_line("markers", "integration: Integration tests (real DB)")
    config.addinivalue_line("markers", "e2e: End-to-end tests (full workflows)")
    config.addinivalue_line("markers", "slow: Slow tests (>1s)")
    config.addinivalue_line("markers", "db: Database tests")


# ==================== Cleanup ====================

@pytest.fixture(autouse=True)
def cleanup_after_test():
    """
    Auto-cleanup after each test.
    
    Ensures dependency overrides are cleared.
    """
    yield
    # Clear any remaining dependency overrides
    app.dependency_overrides.clear()
