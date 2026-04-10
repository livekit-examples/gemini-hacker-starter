from pydantic import BaseModel


class DemoConfig(BaseModel):
    # Identity
    slug: str
    name: str
    # Persona
    persona_name: str
    persona_initials: str
    persona_role: str
    # Display
    value_prop: str
    accent: str
    available: bool
    # Languages
    supported_languages: list[str]
    # Dental only — keyed by language code
    disclaimer: dict[str, str] = {}


DEMO_CONFIGS: dict[str, DemoConfig] = {
    "sales": DemoConfig(
        slug="sales",
        name="Sales Strategy",
        persona_name="Aria",
        persona_initials="AR",
        persona_role="Senior Sales Strategist",
        value_prop=(
            "Analyse prospect screens in real time and generate tailored proposals "
            "on the fly — close faster with an AI co-pilot that knows your deal."
        ),
        accent="#4DA6FF",
        available=True,
        supported_languages=["en", "it", "ar-EG", "ar-AE"],
    ),
    "manufacturing": DemoConfig(
        slug="manufacturing",
        name="Manufacturing & Quality",
        persona_name="Marco",
        persona_initials="MA",
        persona_role="Process & Quality Engineer",
        value_prop=(
            "Detect visual defects on the production line and surface the right SOP "
            "in seconds — cut rework and keep compliance airtight."
        ),
        accent="#4DA6FF",
        available=False,
        supported_languages=["en", "it", "ar-EG", "ar-AE"],
    ),
    "logistics": DemoConfig(
        slug="logistics",
        name="Logistics & Supply Chain",
        persona_name="Elena",
        persona_initials="EL",
        persona_role="Head of Logistics Operations",
        value_prop=(
            "Track shipments, flag delays, and brief carrier performance in real "
            "time — keep your supply chain moving with zero blind spots."
        ),
        accent="#4DA6FF",
        available=False,
        supported_languages=["en", "it", "ar-EG", "ar-AE"],
    ),
    "real_estate": DemoConfig(
        slug="real_estate",
        name="Real Estate Advisory",
        persona_name="Sofia",
        persona_initials="SO",
        persona_role="Senior Property Advisor",
        value_prop=(
            "Walk through a property on screen and receive live CMA analysis and "
            "buyer-profile summaries — turn viewings into offers faster."
        ),
        accent="#4DA6FF",
        available=False,
        supported_languages=["en", "it", "ar-EG", "ar-AE"],
    ),
    "dental": DemoConfig(
        slug="dental",
        name="Dental Practice",
        persona_name="Dr. Nour",
        persona_initials="DN",
        persona_role="Specialist in Restorative Dentistry",
        value_prop=(
            "Review dental images with an AI specialist, retrieve patient briefs, "
            "and deliver multilingual aftercare instructions at the point of care."
        ),
        accent="#4DA6FF",
        available=False,
        supported_languages=["en", "it", "ar-EG", "ar-AE"],
        disclaimer={
            "en": (
                "This AI assistant is intended for qualified dental professionals only. "
                "All clinical decisions remain the sole responsibility of the treating "
                "dentist. This tool does not replace professional clinical judgement."
            ),
            "it": (
                "Questo assistente AI è destinato esclusivamente a professionisti "
                "odontoiatrici qualificati. Tutte le decisioni cliniche rimangono di "
                "esclusiva responsabilità del dentista curante. Questo strumento non "
                "sostituisce il giudizio clinico professionale."
            ),
            "ar-EG": (
                "المساعد الذكي ده مخصص للأطباء والمتخصصين في طب الأسنان بس. "
                "كل القرارات الطبية مسؤولية الدكتور المعالج. "
                "الأداة دي مش بديل عن الحكم الطبي المتخصص."
            ),
            "ar-AE": (
                "هذا المساعد الذكي مخصص للمتخصصين المؤهلين في طب الأسنان فقط. "
                "تظل جميع القرارات السريرية مسؤولية الطبيب المعالج حصراً. "
                "هذه الأداة لا تحل محل الحكم السريري المهني."
            ),
        },
    ),
}
