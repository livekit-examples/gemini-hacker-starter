"""Language detection helpers for agent metadata."""

from __future__ import annotations

from app.languages.profiles import LanguageProfile, get_language_profile



def detect_language(metadata: dict | None, fallback: str) -> LanguageProfile:
    """Detect language from participant metadata with fallback safety."""
    requested_code = None
    if metadata:
        requested_code = metadata.get("preferredLanguage")

    if isinstance(requested_code, str):
        profile = get_language_profile(requested_code)
        if profile is not None:
            return profile

    fallback_profile = get_language_profile(fallback)
    if fallback_profile is not None:
        return fallback_profile

    # Final guardrail to guarantee a profile is always returned.
    default_profile = get_language_profile("en")
    if default_profile is None:
        raise RuntimeError("English language profile is missing")
    return default_profile
