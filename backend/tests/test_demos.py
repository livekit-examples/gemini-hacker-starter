from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)

EXPECTED_SLUGS = {"sales", "manufacturing", "logistics", "real_estate", "dental"}


def test_demos_status_200():
    response = client.get("/api/demos")
    assert response.status_code == 200


def test_demos_returns_five_items():
    response = client.get("/api/demos")
    data = response.json()
    assert "demos" in data
    assert len(data["demos"]) == 5


def test_demos_each_has_slug_and_name():
    response = client.get("/api/demos")
    data = response.json()
    for demo in data["demos"]:
        assert "slug" in demo
        assert "name" in demo
        assert isinstance(demo["slug"], str) and len(demo["slug"]) > 0
        assert isinstance(demo["name"], str) and len(demo["name"]) > 0


def test_demos_contains_all_expected_slugs():
    response = client.get("/api/demos")
    data = response.json()
    slugs = {d["slug"] for d in data["demos"]}
    assert slugs == EXPECTED_SLUGS
