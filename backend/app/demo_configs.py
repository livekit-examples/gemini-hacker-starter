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
        demo_scenarios=[
            DemoScenario(
                title="Competitive Deal — Protect Margin",
                description="A rep is looking at a CRM record where a competitor has been mentioned and a discount is being requested.",
                steps=[
                    "I'm looking at the Hartmann Industries deal. Competitor is mentioned in the notes and they're asking for 20% off. What should I do?",
                    "Can you give me the right talking points to push back on the discount without losing the deal?",
                    "Help me write the executive summary section for Hartmann — they're a mid-size manufacturing firm in Stuttgart.",
                ],
            ),
            DemoScenario(
                title="Pipeline Review — Late-Stage Opportunities",
                description="Sales manager reviewing three deals approaching quarter-end with unresolved blockers.",
                steps=[
                    "I'm looking at my pipeline. Three deals are at contract stage and the quarter closes in two weeks. What's the priority?",
                    "The Belloni Group deal has the CFO involved now. Log these talking points: lead with ROI, confirm budget approval authority, propose a 30-day pilot.",
                    "Can you generate the next steps section for Belloni's proposal? They're a logistics company in Milan.",
                ],
            ),
            DemoScenario(
                title="Discovery Call Prep",
                description="Rep preparing for a first call with a new enterprise prospect.",
                steps=[
                    "I have a discovery call with Meridian Healthcare tomorrow. I can see their LinkedIn — 5,000 employees, recent news about digital transformation. What should I focus on?",
                    "Generate a problem statement section for them. They're a large private hospital group.",
                    "What are the three questions I absolutely must ask to qualify this deal?",
                ],
            ),
            DemoScenario(
                title="Stalled Deal — Re-Engagement",
                description="A deal has gone dark after a strong proposal stage. Rep needs a strategy to re-engage.",
                steps=[
                    "The Ferreira Group went silent three weeks ago. We sent the proposal and got no response. What do I do?",
                    "My CRM shows their contract renewal is in two months and they haven't signed anything yet. How urgent is this?",
                    "Log these re-engagement talking points: acknowledge the silence, reference the renewal deadline, offer a quick 15-minute check-in.",
                ],
            ),
        ],
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
        available=True,
        supported_languages=_ALL_LANGUAGES,
        demo_scenarios=[
            DemoScenario(
                title="Weld Defect on Frame Sub-Assembly",
                description="Inspector finds porosity in a weld bead during a quality walkthrough.",
                steps=[
                    "I'm inspecting a frame sub-assembly and I can see porosity in the weld bead near the cross-member. What kind of defect is this?",
                    "How severe is weld porosity? Should we stop the line?",
                    "Can you pull up the weld inspection SOP so I know the acceptance criteria?",
                    "Generate a defect report for the weld porosity I found on this part.",
                ],
            ),
            DemoScenario(
                title="Lockout/Tagout Before CNC Maintenance",
                description="Maintenance technician needs to perform LOTO before servicing the CNC milling machine.",
                steps=[
                    "I need to service the CNC milling machine LM-400. What's the lockout tagout procedure?",
                    "What happens if I skip the step to verify zero energy state?",
                    "The machine has a spindle overload error E-14. How do I troubleshoot that before the LOTO?",
                ],
            ),
            DemoScenario(
                title="Critical Crack on Load-Bearing Bracket",
                description="A hairline crack is spotted on a structural component — worst-case defect scenario.",
                steps=[
                    "There's a hairline crack on the left load-bearing bracket. How do I classify this?",
                    "This is a critical defect. What are the immediate steps I need to take?",
                    "Can you generate a defect report so I can attach it to the NCR?",
                ],
            ),
            DemoScenario(
                title="Torque Spec for Gearbox Cover Assembly",
                description="An operator is assembling a gearbox and needs the correct torque sequence for M12 bolts.",
                steps=[
                    "What's the torque specification for M12 bolts on a gearbox cover?",
                    "Should I use a thread-locking compound? And in what order do I tighten the bolts?",
                    "After torquing, how long do I wait before pressure-testing?",
                ],
            ),
            DemoScenario(
                title="Paint Defect on Class A Panel",
                description="An orange peel texture is found on an exterior panel — minor defect edge case.",
                steps=[
                    "I found an orange peel texture on a painted exterior panel. Is this a major or minor defect?",
                    "What's the SOP for doing a spot repair on a paint defect?",
                    "The DOI reading on our BYK scanner is 82. Should the panel be rejected?",
                ],
            ),
        ],
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
        available=True,
        supported_languages=_ALL_LANGUAGES,
        demo_scenarios=[
            DemoScenario(
                title="Delayed Shipment — Customs Hold in Abu Dhabi",
                description="A high-value textile shipment is stuck at UAE customs with no ETA update.",
                steps=[
                    "I need a status update on shipment SHP-20240310-AUH. What's happening?",
                    "It's been 5 days — can you flag it as delayed and note the certificate of origin issue?",
                    "Who's the carrier on this and what's their on-time rate for UAE routes?",
                ],
            ),
            DemoScenario(
                title="Carrier Performance Review — Air Arabia",
                description="Operations manager reviewing carrier reliability before Q2 bookings.",
                steps=[
                    "Give me a performance brief on Air Arabia Cargo.",
                    "11 open incidents sounds high — should we look for an alternative carrier for the Dhaka routes?",
                    "What about FedEx for the same South Asia to UAE corridor? How do they compare?",
                ],
            ),
            DemoScenario(
                title="Proactive Delay Escalation — DHL Truck Breakdown",
                description="A truck breakdown is threatening an SLA on a wine and spirits shipment to Milan.",
                steps=[
                    "What's the status of SHP-20240320-LIN?",
                    "A 2-day delay on wine and spirits going to Milan is going to breach our SLA. Flag it now.",
                    "Is there any other DHL freight in transit that might be affected by the same driver shortage?",
                ],
            ),
            DemoScenario(
                title="Multi-Shipment Morning Briefing",
                description="Logistics manager reviewing overnight updates across the active shipment portfolio.",
                steps=[
                    "Can you pull up SHP-20240315-MXP? That's the Milan machinery shipment.",
                    "Also check SHP-20240318-FJR — that's the construction materials vessel.",
                    "Which of our active shipments is currently at the highest risk of missing its ETA?",
                ],
            ),
            DemoScenario(
                title="Unknown Tracking ID — Edge Case",
                description="An operator pastes an incorrect or expired tracking ID to test system behaviour.",
                steps=[
                    "Can you track this shipment: SHP-FAKE-99999?",
                    "That tracking ID came from an old email — how do I find the correct one?",
                    "What carriers do we usually use for shipments from Karachi to the UAE?",
                ],
            ),
        ],
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
