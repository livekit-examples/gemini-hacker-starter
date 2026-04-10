from fastapi import APIRouter

from app.demo_configs import DEMO_CONFIGS, DemoConfig
from app.models import DemosResponse

router = APIRouter()


@router.get("/api/demos", response_model=DemosResponse)
async def list_demos() -> DemosResponse:
    demos: list[DemoConfig] = list(DEMO_CONFIGS.values())
    return DemosResponse(demos=demos)
