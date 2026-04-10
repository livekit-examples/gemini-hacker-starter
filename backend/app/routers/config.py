from fastapi import APIRouter, HTTPException

from app.demo_configs import DEMO_CONFIGS, DemoConfig

router = APIRouter()


@router.get("/api/config", response_model=DemoConfig)
async def get_config(industry: str) -> DemoConfig:
    config = DEMO_CONFIGS.get(industry)
    if config is None:
        known = ", ".join(sorted(DEMO_CONFIGS.keys()))
        raise HTTPException(
            status_code=404,
            detail=f"Unknown industry '{industry}'. Known slugs: {known}.",
        )
    return config
