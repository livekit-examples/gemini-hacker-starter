import base64
import hashlib
import hmac
import json
import random
import time
from typing import Any

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.config import settings
from app.models import ConnectionDetailsResponse

router = APIRouter()

_TOKEN_TTL_SECONDS = 900  # 15 minutes


def _b64url_encode(data: bytes) -> str:
    """URL-safe base64 encoding without padding."""
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode()


def _mint_livekit_token(
    api_key: str,
    api_secret: str,
    identity: str,
    participant_name: str,
    room_name: str,
    metadata: str | None = None,
) -> str:
    """Mint a LiveKit-compatible JWT token using HMAC-SHA256."""
    now = int(time.time())
    header: dict[str, Any] = {"alg": "HS256", "typ": "JWT"}
    payload: dict[str, Any] = {
        "exp": now + _TOKEN_TTL_SECONDS,
        "iss": api_key,
        "sub": identity,
        "nbf": now,
        "name": participant_name,
        "video": {
            "roomJoin": True,
            "room": room_name,
            "canPublish": True,
            "canPublishData": True,
            "canSubscribe": True,
        },
    }
    if metadata:
        payload["metadata"] = metadata
    header_b64 = _b64url_encode(json.dumps(header, separators=(",", ":")).encode())
    payload_b64 = _b64url_encode(json.dumps(payload, separators=(",", ":")).encode())
    signing_input = f"{header_b64}.{payload_b64}".encode()
    signature = hmac.new(
        api_secret.encode(), signing_input, hashlib.sha256
    ).digest()
    return f"{header_b64}.{payload_b64}.{_b64url_encode(signature)}"


def _validate_livekit_settings() -> None:
    if not settings.livekit_url:
        raise HTTPException(status_code=503, detail="LIVEKIT_URL is not configured")
    if not settings.livekit_api_key:
        raise HTTPException(status_code=503, detail="LIVEKIT_API_KEY is not configured")
    if not settings.livekit_api_secret:
        raise HTTPException(status_code=503, detail="LIVEKIT_API_SECRET is not configured")


def _build_connection_response(language: str | None = None) -> ConnectionDetailsResponse:
    _validate_livekit_settings()
    suffix = random.randint(0, 99_999)
    room_name = f"voice_assistant_room_{suffix}"
    participant_identity = f"voice_assistant_user_{suffix}"
    participant_name = "user"
    metadata = json.dumps({"preferredLanguage": language}) if language else None
    token = _mint_livekit_token(
        api_key=settings.livekit_api_key,
        api_secret=settings.livekit_api_secret,
        identity=participant_identity,
        participant_name=participant_name,
        room_name=room_name,
        metadata=metadata,
    )
    return ConnectionDetailsResponse(
        serverUrl=settings.livekit_url,
        roomName=room_name,
        participantToken=token,
        participantName=participant_name,
    )


class ConnectionDetailsRequest(BaseModel):
    language: str | None = None


@router.get("/api/connection-details", response_model=ConnectionDetailsResponse)
async def connection_details() -> ConnectionDetailsResponse:
    return _build_connection_response()


@router.post("/api/connection-details", response_model=ConnectionDetailsResponse)
async def connection_details_post(
    body: ConnectionDetailsRequest = ConnectionDetailsRequest(),
) -> ConnectionDetailsResponse:
    return _build_connection_response(language=body.language)
