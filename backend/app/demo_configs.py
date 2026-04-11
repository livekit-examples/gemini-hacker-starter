from pydantic import BaseModel


class LanguageInfo(BaseModel):
    code: str
    display_name: str
    flag: str
    is_rtl: bool


def _lang(code: str) -> LanguageInfo:
    """Build a LanguageInfo from the canonical language profiles."""
    from app.languages.profiles import PROFILES  # local import to avoid circular

    p = PROFILES[code]
    return LanguageInfo(
        code=p.code,
        display_name=p.display_name,
        flag=p.flag,
        is_rtl=p.is_rtl,
    )


_ALL_LANGUAGES: list[LanguageInfo] = [_lang(c) for c in ("en", "it", "ar-EG", "ar-AE")]


class DemoScenario(BaseModel):
    title: str          # short label shown as a heading
    description: str    # one-line context setting the scene
    steps: list[str]    # ordered prompts to speak aloud, one at a time


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
    # Languages — full LanguageInfo objects, not raw codes
    supported_languages: list[LanguageInfo]
    # Suggested voice prompts shown in the dashboard
    demo_scenarios: list[DemoScenario] = []
    # Dental only — keyed by language code
    disclaimer: dict[str, str] = {}


DEMO_CONFIGS: dict[str, DemoConfig] = {
    "comune": DemoConfig(
        slug="comune",
        name="Servizi Comunali",
        persona_name="Giulia",
        persona_initials="GI",
        persona_role="Municipal Services AI",
        value_prop=(
            "Guide citizens through Italian municipal bureaucracy in real time — "
            "look up document requirements, track application status, and book "
            "appointments across all 4 languages, including Arabic for immigrant communities."
        ),
        accent="#4DA6FF",
        available=True,
        supported_languages=_ALL_LANGUAGES,
        demo_scenarios=[
            DemoScenario(
                title="New Arrival — Residency Registration",
                description="You just moved from Egypt and need to register your address.",
                steps=[
                    "I just moved to Milan from Egypt. I need to register my residency. What documents do I need?",
                    "I have a permesso di soggiorno. Is the service free?",
                    "Can you book an appointment for me? My name is Fatima Al-Rashidi and I'm free on March 15th.",
                ],
            ),
            DemoScenario(
                title="Stuck Building Permit",
                description="Your architect submitted a permit months ago with no update.",
                steps=[
                    "My architect applied for a building permit in September. The ID is APP-2024-PER-00078. Any update?",
                    "What exactly are the updated project drawings supposed to include?",
                    "How long does a building permit normally take once the documents are complete?",
                ],
            ),
            DemoScenario(
                title="Citizenship Journey",
                description="A 12-year resident ready to start the naturalisation process.",
                steps=[
                    "I've been living in Italy for 12 years. How do I apply for Italian citizenship?",
                    "I'm from Egypt — do I need to apostille my birth certificate?",
                    "That's a lot of documents. Can you book an appointment so the Comune can help me collect them?",
                ],
            ),
            DemoScenario(
                title="ISEE for School Fees",
                description="A parent who needs an ISEE certificate to access reduced tuition.",
                steps=[
                    "I need an ISEE certificate for my children's school fees. What documents do I bring?",
                    "I already started the process. My reference is APP-2024-SOC-00389. Is it ready?",
                    "Where exactly do I bring the bank statement to complete the application?",
                ],
            ),
            DemoScenario(
                title="Rejected Outdoor Seating",
                description="A café owner whose dehors application was turned down.",
                steps=[
                    "I applied for outdoor seating for my café. The ID is APP-2024-PER-00031. What happened?",
                    "Can I appeal the decision or submit a new application?",
                    "What documents would I need if I apply for a different area?",
                ],
            ),
        ],
    ),
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
        supported_languages=_ALL_LANGUAGES,
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
        supported_languages=_ALL_LANGUAGES,
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
        supported_languages=_ALL_LANGUAGES,
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
        supported_languages=_ALL_LANGUAGES,
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
        supported_languages=_ALL_LANGUAGES,
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
