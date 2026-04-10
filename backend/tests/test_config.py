"""Tests for GET /api/config?industry={slug}."""

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)

REQUIRED_FIELDS = {
    "slug",
    "name",
    "persona_name",
    "persona_initials",
    "persona_role",
    "value_prop",
    "accent",
    "available",
    "supported_languages",
}


def test_config_known_industry_200():
    response = client.get("/api/config", params={"industry": "sales"})
    assert response.status_code == 200


def test_config_returns_correct_slug():
    response = client.get("/api/config", params={"industry": "sales"})
    data = response.json()
    assert data["slug"] == "sales"


def test_config_required_fields_present():
    response = client.get("/api/config", params={"industry": "sales"})
    data = response.json()
    for field in REQUIRED_FIELDS:
        assert field in data, f"Missing field: {field}"


def test_config_unknown_industry_404():
    response = client.get("/api/config", params={"industry": "unknown_industry"})
    assert response.status_code == 404


def test_config_404_has_descriptive_detail():
    response = client.get("/api/config", params={"industry": "unknown_industry"})
    body = response.json()
    assert "detail" in body
    assert "unknown_industry" in body["detail"]


def test_config_dental_has_disclaimer():
    response = client.get("/api/config", params={"industry": "dental"})
    data = response.json()
    assert "disclaimer" in data
    assert isinstance(data["disclaimer"], dict)
    assert len(data["disclaimer"]) == 4
