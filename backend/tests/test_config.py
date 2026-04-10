from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_config_status_200():
    response = client.get("/api/config")
    assert response.status_code == 200


def test_config_required_fields_present():
    response = client.get("/api/config")
    data = response.json()
    assert "agentName" in data
    assert "industry" in data
    assert "language" in data
    assert "accent" in data
    assert "title" in data


def test_config_field_types():
    response = client.get("/api/config")
    data = response.json()
    for field in ("agentName", "industry", "language", "accent", "title"):
        assert isinstance(data[field], str)
        assert len(data[field]) > 0
