from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.core.config import settings


def test_health_check(client: TestClient, db: Session) -> None:
    response = client.get(f"{settings.API_V1_STR}/health")
    assert response.status_code == 200
    content = response.json()
    assert content["status"] == "healthy"
    assert content["database"] == "healthy"
    assert "version" in content 