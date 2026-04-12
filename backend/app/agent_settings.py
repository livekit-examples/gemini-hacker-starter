import logging

logger = logging.getLogger(__name__)

STABLE_FALLBACK_REALTIME_MODEL = "gemini-2.5-flash-native-audio-latest"
STABLE_FALLBACK_STT_MODEL = "auto"


def resolve_realtime_model(requested_model: str) -> str:
    """Choose a realtime model compatible with the current agent session flow."""
    if requested_model.strip() == "gemini-3.1-flash-live-preview":
        logger.warning(
            "REALTIME_MODEL '%s' has known LiveKit compatibility limitations; "
            "falling back to '%s' for stable tool follow-up responses.",
            requested_model,
            STABLE_FALLBACK_REALTIME_MODEL,
        )
        return STABLE_FALLBACK_REALTIME_MODEL

    return requested_model


def resolve_stt_model(requested_model: str) -> str:
    """Resolve STT model for LiveKit inference, never returning an empty value."""
    if requested_model.strip():
        return requested_model.strip()

    logger.warning(
        "STT model was empty; falling back to '%s' to avoid NOT_GIVEN gateway calls.",
        STABLE_FALLBACK_STT_MODEL,
    )
    return STABLE_FALLBACK_STT_MODEL
