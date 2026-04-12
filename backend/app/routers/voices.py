from fastapi import APIRouter

from app.config import settings
from app.models import VoicesResponse
from app.voice_catalog import resolve_voice_catalog

router = APIRouter()


@router.get("/api/voices", response_model=VoicesResponse)
async def get_voices() -> VoicesResponse:
    return VoicesResponse(voices=resolve_voice_catalog(settings.realtime_voices))
