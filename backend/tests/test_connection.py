import base64
import json

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def _decode_jwt_payload(token: str) -> dict:
    """Decode the JWT payload without verifying the signature."""
    parts = token.split(".")
    assert len(parts) == 3, "JWT must have exactly 3 dot-separated parts"
    padded = parts[1] + "=" * (-len(parts[1]) % 4)
    return json.loads(base64.urlsafe_b64decode(padded))


def test_connection_details_status_200():
    response = client.get("/api/connection-details")
    assert response.status_code == 200


def test_connection_details_schema():
    response = client.get("/api/connection-details")
    data = response.json()
    assert "serverUrl" in data
    assert "roomName" in data
    assert "participantToken" in data
    assert "participantName" in data


def test_connection_details_token_is_valid_jwt():
    response = client.get("/api/connection-details")
    data = response.json()
    token = data["participantToken"]

    # A JWT has exactly three dot-separated parts
    assert len(token.split(".")) == 3

    decoded = _decode_jwt_payload(token)

    # LiveKit-required claims
    assert "video" in decoded
    assert decoded["video"]["roomJoin"] is True
    assert "room" in decoded["video"]
    assert decoded["iss"] == "test-api-key"
    assert decoded["sub"].startswith("voice_assistant_user_")


def test_connection_details_room_name_matches_token():
    response = client.get("/api/connection-details")
    data = response.json()
    decoded = _decode_jwt_payload(data["participantToken"])
    assert decoded["video"]["room"] == data["roomName"]


def test_connection_details_post_sets_room_config_and_metadata():
    response = client.post(
        "/api/connection-details",
        json={
            "language": "ar-EG",
            "industry": "comune",
            "room_config": {"agents": [{"agent_name": "gemini-hackathon-agent"}]},
        },
    )
    assert response.status_code == 200

    decoded = _decode_jwt_payload(response.json()["participantToken"])

    assert "roomConfig" in decoded
    assert decoded["roomConfig"]["agents"][0]["agentName"] == "gemini-hackathon-agent"

    metadata = json.loads(decoded["metadata"])
    assert metadata["preferredLanguage"] == "ar-EG"
    assert metadata["industry"] == "comune"
