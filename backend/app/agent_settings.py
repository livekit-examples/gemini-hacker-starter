import logging

logger = logging.getLogger(__name__)

STABLE_FALLBACK_REALTIME_MODEL = "gemini-2.5-flash-native-audio-latest"


def resolve_realtime_model(requested_model: str) -> str:
    """Resolve realtime model, falling back only when unset."""
    normalized = requested_model.strip()

    if not normalized:
        logger.warning(
            "Realtime model was empty; falling back to '%s'.",
            STABLE_FALLBACK_REALTIME_MODEL,
        )
        return STABLE_FALLBACK_REALTIME_MODEL

    return normalized
