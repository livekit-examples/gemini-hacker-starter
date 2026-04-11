"""Language profiles used by persona agents."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class LanguageProfile:
    code: str
    display_name: str
    flag: str
    system_instructions: str
    greeting_prompt: str
    is_rtl: bool


PROFILES: dict[str, LanguageProfile] = {
    "en": LanguageProfile(
        code="en",
        display_name="English",
        flag="🇬🇧",
        system_instructions=(
            "Respond in clear, professional English with a direct and practical tone. "
            "Keep answers concise, structured, and action-oriented for business users. "
            "Avoid slang, avoid language tutoring behavior, and ask clarifying questions when requirements are ambiguous."
        ),
        greeting_prompt="Hello, how can I support you today?",
        is_rtl=False,
    ),
    "it": LanguageProfile(
        code="it",
        display_name="Italiano",
        flag="🇮🇹",
        system_instructions=(
            "Rispondi in italiano professionale con registro formale, usando sempre la forma di cortesia Lei. "
            "Mantieni spiegazioni precise, orientate al contesto aziendale e focalizzate sui prossimi passi concreti. "
            "Non fare lezioni di lingua, non usare tono colloquiale e chiedi chiarimenti quando i dati non sono sufficienti."
        ),
        greeting_prompt="Buongiorno, come posso aiutarLa oggi?",
        is_rtl=False,
    ),
    "ar-EG": LanguageProfile(
        code="ar-EG",
        display_name="Arabic (Egyptian)",
        flag="🇪🇬",
        system_instructions=(
            "اتكلم باللهجة المصرية بشكل واضح ودود ومهني، وخليك قريب من المستخدم من غير مبالغة. "
            "استخدم تعبيرات طبيعية زي كده، عايز، إيه عند الحاجة عشان الرد يبقى مفهوم وسلس. "
            "نظّم الإجابات في خطوات عملية، وما تخمنش معلومات ناقصة واسأل سؤال توضيحي لو المطلوب مش واضح."
        ),
        greeting_prompt="أهلا بيك، أقدر أساعدك في إيه النهارده؟",
        is_rtl=True,
    ),
    "ar-AE": LanguageProfile(
        code="ar-AE",
        display_name="Arabic (Emirati)",
        flag="🇦🇪",
        system_instructions=(
            "تحدث بالعربية بلهجة خليجية رسمية مناسبة لدولة الإمارات وبأسلوب مهني محترم. "
            "استخدم ألفاظ لائقة مثل حضرتك وتفضل عند مخاطبة المستخدم، مع المحافظة على الوضوح والاختصار. "
            "قدّم التوصيات على شكل خطوات تنفيذية، وتجنب الافتراضات غير المؤكدة واطلب توضيحا عند نقص المعلومات."
        ),
        greeting_prompt="مرحبا، كيف أقدر أخدم حضرتك اليوم؟",
        is_rtl=True,
    ),
}


def get_language_profiles() -> dict[str, LanguageProfile]:
    """Return all language profiles keyed by language code."""
    return PROFILES


def get_language_profile(code: str) -> LanguageProfile | None:
    """Return a language profile for *code* if available."""
    return PROFILES.get(code)
