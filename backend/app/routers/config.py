from fastapi import APIRouter

from app.models import AppConfigResponse

router = APIRouter()

_DEFAULT_CONFIG = AppConfigResponse(
    agentName="gemini-hackathon-agent",
    industry="sales",
    language="en",
    accent="#4DA6FF",
    title="Exodia AI Demo Platform",
)


@router.get("/api/config", response_model=AppConfigResponse)
async def get_config() -> AppConfigResponse:
    return _DEFAULT_CONFIG
