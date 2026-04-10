"""Tests for GET /api/demos — returns full DemoConfig list."""

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)

EXPECTED_SLUGS = {"sales", "manufacturing", "logistics", "real_estate", "dental"}
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


def test_demos_status_200():
    response = client.get("/api/demos")
    assert response.status_code == 200


def test_demos_returns_five_items():
    response = client.get("/api/demos")
    data = response.json()
    assert "demos" in data
    assert len(data["demos"]) == 5


def test_demos_contains_all_expected_slugs():
    response = client.get("/api/demos")
    data = response.json()
    slugs = {d["slug"] for d in data["demos"]}
    assert slugs == EXPECTED_SLUGS


def test_demos_each_item_has_full_demo_config_fields():
    response = client.get("/api/demos")
    data = response.json()
    for demo in data["demos"]:
        for field in REQUIRED_FIELDS:
            assert field in demo, f"slug={demo.get('slug')}: missing field '{field}'"


def test_demos_each_item_persona_initials_2_to_3_chars():
    response = client.get("/api/demos")
    data = response.json()
    for demo in data["demos"]:
        initials = demo["persona_initials"]
        assert 2 <= len(initials) <= 3, (
            f"slug={demo['slug']}: persona_initials '{initials}' not 2–3 chars"
        )
        assert initials == initials.upper(), (
            f"slug={demo['slug']}: persona_initials '{initials}' not uppercase"
        )


def test_demos_available_is_bool():
    response = client.get("/api/demos")
    data = response.json()
    for demo in data["demos"]:
        assert isinstance(demo["available"], bool), (
            f"slug={demo['slug']}: available is not bool"
        )
