from fastapi import APIRouter

from app.models import DemoSummary, DemosResponse

router = APIRouter()

_DEMOS = [
    DemoSummary(
        slug="sales",
        name="Sales Strategy",
        persona_name="Aria",
        persona_initials="AR",
        persona_role="Senior Sales Strategist",
        value_prop="Analyse prospect screens in real time and generate tailored proposals on the fly — close faster with an AI co-pilot that knows your deal.",
        available=True,
        supported_languages=["EN", "IT", "AR-EG", "AR-AE"],
    ),
    DemoSummary(
        slug="manufacturing",
        name="Manufacturing & Quality",
        persona_name="Marco",
        persona_initials="MA",
        persona_role="Process & Quality Engineer",
        value_prop="Detect visual defects on the production line and surface the right SOP in seconds — cut rework and keep compliance airtight.",
        available=False,
        supported_languages=["EN", "IT", "AR-EG", "AR-AE"],
    ),
    DemoSummary(
        slug="logistics",
        name="Logistics & Supply Chain",
        persona_name="Elena",
        persona_initials="EL",
        persona_role="Head of Logistics Operations",
        value_prop="Track shipments, flag delays, and brief carrier performance in real time — keep your supply chain moving with zero blind spots.",
        available=False,
        supported_languages=["EN", "IT", "AR-EG", "AR-AE"],
    ),
    DemoSummary(
        slug="real_estate",
        name="Real Estate Advisory",
        persona_name="Sofia",
        persona_initials="SO",
        persona_role="Senior Property Advisor",
        value_prop="Walk through a property on screen and receive live CMA analysis and buyer-profile summaries — turn viewings into offers faster.",
        available=False,
        supported_languages=["EN", "IT", "AR-EG", "AR-AE"],
    ),
    DemoSummary(
        slug="dental",
        name="Dental Practice",
        persona_name="Dr. Nour",
        persona_initials="DN",
        persona_role="Specialist in Restorative Dentistry",
        value_prop="Review dental images with an AI specialist, retrieve patient briefs, and deliver multilingual aftercare instructions at the point of care.",
        available=False,
        supported_languages=["EN", "IT", "AR-EG", "AR-AE"],
    ),
]


@router.get("/api/demos", response_model=DemosResponse)
async def list_demos() -> DemosResponse:
    return DemosResponse(demos=_DEMOS)
