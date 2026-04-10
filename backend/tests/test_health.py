from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health_status_200():
    response = client.get("/api/health")
    assert response.status_code == 200


def test_health_body_matches_schema():
    response = client.get("/api/health")
    data = response.json()
    assert data["status"] == "ok"
    assert "version" in data
    assert isinstance(data["version"], str)
    assert len(data["version"]) > 0
