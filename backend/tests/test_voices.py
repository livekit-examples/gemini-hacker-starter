from fastapi.testclient import TestClient

from app.main import app
from app.voice_catalog import DEFAULT_GEMINI_VOICES

client = TestClient(app)


def test_voices_endpoint_returns_default_catalog():
    response = client.get("/api/voices")
    assert response.status_code == 200
    data = response.json()

    assert "voices" in data
    assert data["voices"] == DEFAULT_GEMINI_VOICES


def test_voices_endpoint_items_are_non_empty_strings():
    response = client.get("/api/voices")
    assert response.status_code == 200
    data = response.json()

    assert all(isinstance(voice, str) and voice.strip() for voice in data["voices"])
