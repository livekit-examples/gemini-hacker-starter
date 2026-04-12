DEFAULT_GEMINI_VOICES = [
    "Aoede",
    "Kore",
    "Puck",
    "Charon",
    "Fenrir",
    "Zephyr",
    "Leda",
    "Orus",
    "Callirrhoe",
    "Autonoe",
    "Enceladus",
    "Iapetus",
    "Umbriel",
    "Algieba",
    "Despina",
    "Erinome",
    "Algenib",
    "Rasalghul",
    "Laomedeia",
    "Achernar",
    "Alnilam",
    "Schedar",
    "Gacrux",
    "Pulcherrima",
    "Achird",
    "Zubenelgenubi",
    "Vindemiatrix",
    "Sadachbia",
    "Sadaltager",
    "Sulafat",
]


def resolve_voice_catalog(configured_csv: str | None) -> list[str]:
    """Return configured realtime voices or the default Gemini voice catalog.

    `configured_csv` is a comma-separated list, typically from an env var.
    """
    if not configured_csv:
        return DEFAULT_GEMINI_VOICES.copy()

    parsed = [voice.strip() for voice in configured_csv.split(",") if voice.strip()]
    if not parsed:
        return DEFAULT_GEMINI_VOICES.copy()

    # Preserve order while deduplicating.
    unique: list[str] = []
    seen: set[str] = set()
    for voice in parsed:
        key = voice.lower()
        if key in seen:
            continue
        seen.add(key)
        unique.append(voice)

    return unique
