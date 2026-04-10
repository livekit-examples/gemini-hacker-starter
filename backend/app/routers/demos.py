from fastapi import APIRouter

from app.models import DemoSummary, DemosResponse

router = APIRouter()

_DEMOS = [
    DemoSummary(slug="sales", name="Sales Strategy"),
    DemoSummary(slug="manufacturing", name="Manufacturing & Quality"),
    DemoSummary(slug="logistics", name="Logistics & Supply Chain"),
    DemoSummary(slug="real_estate", name="Real Estate Advisory"),
    DemoSummary(slug="dental", name="Dental Practice"),
]


@router.get("/api/demos", response_model=DemosResponse)
async def list_demos() -> DemosResponse:
    return DemosResponse(demos=_DEMOS)
