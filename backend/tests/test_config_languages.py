"""Session 11: Tests verifying that /api/config returns full LanguageInfo objects."""

import json

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)

EXPECTED_CODES = {"en", "it", "ar-EG", "ar-AE"}
LANGUAGE_FIELDS = {"code", "display_name", "flag", "is_rtl"}


def _get_languages(industry: str) -> list[dict]:
    response = client.get("/api/config", params={"industry": industry})
    assert response.status_code == 200
    return response.json()["supported_languages"]


def test_config_dental_supported_languages_are_objects():
    langs = _get_languages("dental")
    assert len(langs) == 4
    for lang in langs:
        for field in LANGUAGE_FIELDS:
            assert field in lang, f"Missing field '{field}' in language object: {lang}"


def test_config_all_industries_have_four_languages():
    for slug in ("sales", "manufacturing", "logistics", "real_estate", "dental"):
        langs = _get_languages(slug)
        assert len(langs) == 4, f"{slug}: expected 4 languages, got {len(langs)}"


def test_config_language_codes_match_expected():
    langs = _get_languages("sales")
    codes = {l["code"] for l in langs}
    assert codes == EXPECTED_CODES


def test_config_arabic_languages_are_rtl():
    langs = _get_languages("dental")
    by_code = {l["code"]: l for l in langs}
    assert by_code["ar-EG"]["is_rtl"] is True
    assert by_code["ar-AE"]["is_rtl"] is True
    assert by_code["en"]["is_rtl"] is False
    assert by_code["it"]["is_rtl"] is False


def test_config_languages_have_flag_emoji():
    langs = _get_languages("sales")
    for lang in langs:
        assert lang["flag"], f"flag is empty for code '{lang['code']}'"
        # Flags are multi-byte emoji — length varies, just check non-empty
        assert len(lang["flag"]) >= 1


def test_config_languages_have_display_names():
    langs = _get_languages("sales")
    for lang in langs:
        assert lang["display_name"], f"display_name is empty for code '{lang['code']}'"


def test_connection_details_post_with_language_includes_metadata():
    """POST /api/connection-details with language sets metadata in JWT."""
    response = client.post(
        "/api/connection-details",
        json={"language": "ar-EG"},
    )
    assert response.status_code == 200
    data = response.json()
    token = data["participantToken"]

    import base64

    parts = token.split(".")
    assert len(parts) == 3
    padded = parts[1] + "=" * (-len(parts[1]) % 4)
    payload = json.loads(base64.urlsafe_b64decode(padded))
    assert "metadata" in payload
    meta = json.loads(payload["metadata"])
    assert meta["preferredLanguage"] == "ar-EG"


def test_connection_details_post_without_language_has_no_metadata():
    """POST /api/connection-details without language produces no metadata field."""
    response = client.post("/api/connection-details", json={})
    assert response.status_code == 200
    data = response.json()
    token = data["participantToken"]

    import base64

    parts = token.split(".")
    padded = parts[1] + "=" * (-len(parts[1]) % 4)
    payload = json.loads(base64.urlsafe_b64decode(padded))
    assert "metadata" not in payload
