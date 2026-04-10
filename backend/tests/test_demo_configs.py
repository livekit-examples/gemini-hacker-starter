"""Unit tests for DemoConfig objects defined in demo_configs.py."""

import pytest

from app.demo_configs import DEMO_CONFIGS

EXPECTED_SLUGS = {"sales", "manufacturing", "logistics", "real_estate", "dental"}
EXPECTED_LANGUAGES = {"en", "it", "ar-EG", "ar-AE"}


def test_all_five_slugs_present():
    assert set(DEMO_CONFIGS.keys()) == EXPECTED_SLUGS


@pytest.mark.parametrize("slug", sorted(EXPECTED_SLUGS))
def test_persona_fields_non_empty(slug):
    cfg = DEMO_CONFIGS[slug]
    assert cfg.persona_name, f"{slug}: persona_name is empty"
    assert cfg.persona_initials, f"{slug}: persona_initials is empty"
    assert cfg.persona_role, f"{slug}: persona_role is empty"


@pytest.mark.parametrize("slug", sorted(EXPECTED_SLUGS))
def test_value_prop_non_empty(slug):
    assert DEMO_CONFIGS[slug].value_prop


@pytest.mark.parametrize("slug", sorted(EXPECTED_SLUGS))
def test_accent_non_empty(slug):
    assert DEMO_CONFIGS[slug].accent


@pytest.mark.parametrize("slug", sorted(EXPECTED_SLUGS))
def test_available_is_bool(slug):
    assert isinstance(DEMO_CONFIGS[slug].available, bool)


@pytest.mark.parametrize("slug", sorted(EXPECTED_SLUGS))
def test_supported_languages_contains_all_four(slug):
    langs = set(DEMO_CONFIGS[slug].supported_languages)
    assert langs == EXPECTED_LANGUAGES, (
        f"{slug}: expected {EXPECTED_LANGUAGES}, got {langs}"
    )


@pytest.mark.parametrize("slug", sorted(EXPECTED_SLUGS))
def test_persona_initials_two_or_three_uppercase_chars(slug):
    initials = DEMO_CONFIGS[slug].persona_initials
    assert 2 <= len(initials) <= 3, f"{slug}: initials '{initials}' not 2–3 chars"
    assert initials == initials.upper(), f"{slug}: initials '{initials}' not uppercase"


def test_dental_disclaimer_has_all_language_keys():
    disclaimer = DEMO_CONFIGS["dental"].disclaimer
    assert set(disclaimer.keys()) == EXPECTED_LANGUAGES


def test_dental_disclaimer_non_empty_strings():
    disclaimer = DEMO_CONFIGS["dental"].disclaimer
    for lang, text in disclaimer.items():
        assert len(text) >= 20, f"dental disclaimer for '{lang}' is too short"


def test_non_dental_no_disclaimer():
    for slug in EXPECTED_SLUGS - {"dental"}:
        assert DEMO_CONFIGS[slug].disclaimer == {}, (
            f"{slug} should have an empty disclaimer dict"
        )
