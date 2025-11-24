from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_read_main():
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert data["message"] == "Rovet Backend API"
    assert data["version"] == "1.0.0"
    assert data["docs"] == "/api/docs" 