import logging

logger = logging.getLogger(__name__)

STABLE_FALLBACK_REALTIME_MODEL = "gemini-2.5-flash-native-audio-latest"
UNSUPPORTED_REALTIME_MODELS = {"gemini-3.1-flash-live-preview"}


def resolve_realtime_model(requested_model: str) -> str:
    """Resolve realtime model with guardrails for known incompatible models."""
    normalized = requested_model.strip()

    if not normalized:
        logger.warning(
            "Realtime model was empty; falling back to '%s'.",
            STABLE_FALLBACK_REALTIME_MODEL,
        )
        return STABLE_FALLBACK_REALTIME_MODEL

    if normalized.lower() in UNSUPPORTED_REALTIME_MODELS:
        logger.warning(
            "Realtime model '%s' is incompatible with tool follow-up generation; "
            "falling back to '%s'.",
            normalized,
            STABLE_FALLBACK_REALTIME_MODEL,
        )
        return STABLE_FALLBACK_REALTIME_MODEL

    return normalized
