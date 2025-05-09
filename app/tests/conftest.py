import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from unittest.mock import MagicMock, patch
import logging

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

from app.db.session import Base
from app.main import app
from app.db.session import get_db
from app.models.user import UserRole
from app.services.auth_service import AuthService

SQLALCHEMY_TEST_DATABASE_URL = "sqlite:///./test.db"

@pytest.fixture(scope="session")
def test_db_engine():
    logger.info("Creating test database engine")
    engine = create_engine(
        SQLALCHEMY_TEST_DATABASE_URL,
        connect_args={"check_same_thread": False}
    )
    Base.metadata.create_all(bind=engine)
    logger.info("Test database engine created successfully")
    yield engine
    Base.metadata.drop_all(bind=engine)
    logger.info("Test database engine cleaned up")

@pytest.fixture(scope="function")
def db(test_db_engine):
    logger.info("Creating new database session")
    TestingSessionLocal = sessionmaker(
        autocommit=False, autoflush=False, bind=test_db_engine
    )
    db = TestingSessionLocal()
    try:
        for table in reversed(Base.metadata.sorted_tables):
            db.execute(table.delete())
        db.commit()
        logger.info("Database session created and tables cleared")
        yield db
    finally:
        db.rollback()
        db.close()
        logger.info("Database session closed")

@pytest.fixture(scope="function")
def mock_db():
    logger.info("Creating mock database session")
    mock_session = MagicMock()
    mock_session.query.return_value = MagicMock()
    mock_session.add = MagicMock()
    mock_session.commit = MagicMock()
    mock_session.rollback = MagicMock()
    mock_session.close = MagicMock()
    mock_session.refresh = MagicMock()
    logger.info("Mock database session created")
    return mock_session

@pytest.fixture(scope="function")
def client(mock_db: MagicMock) -> TestClient:
    logger.info("Creating test client")
    def override_get_db():
        try:
            yield mock_db
        finally:
            pass
    
    app.dependency_overrides[get_db] = override_get_db
    
    with TestClient(app) as test_client:
        logger.info("Test client created successfully")
        yield test_client
    
    app.dependency_overrides.clear()
    logger.info("Test client cleaned up")

@pytest.fixture(scope="function")
def mock_user_repository():
    logger.info("Creating mock user repository")
    mock_repo = MagicMock()
    mock_repo.get_by_email.return_value = None
    mock_repo.create_with_password.return_value = MagicMock(
        id=1,
        email="test@example.com",
        full_name="Test User",
        role=UserRole.USER,
        is_active=True
    )
    logger.info("Mock user repository created")
    return mock_repo

@pytest.fixture(scope="function")
def mock_auth_service():
    logger.info("Creating mock auth service")
    mock_service = MagicMock()
    mock_service.authenticate_user.return_value = MagicMock(
        id=1,
        email="test@example.com",
        role=UserRole.USER,
        is_active=True
    )
    mock_service.create_access_token.return_value = "mock_token"
    mock_service.verify_token.return_value = {"sub": "1", "role": UserRole.USER}
    logger.info("Mock auth service created")
    return mock_service

@pytest.fixture(scope="function")
def auth_service(mock_db):
    logger.info("Creating auth service")
    service = AuthService(mock_db)
    logger.info("Auth service created")
    return service 