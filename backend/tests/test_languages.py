"""Session 10 language profile and detector tests."""

from unittest.mock import MagicMock, patch

from app.languages.detector import detect_language
from app.languages.profiles import get_language_profile, get_language_profiles


REQUIRED_CODES = ("en", "it", "ar-EG", "ar-AE")



def make_mock_room() -> MagicMock:
    room = MagicMock()
    room.on = MagicMock()
    room.remote_participants = {}
    return room



def test_all_profiles_load_without_error():
    profiles = get_language_profiles()

    for code in REQUIRED_CODES:
        assert code in profiles
        assert profiles[code] is not None



def test_rtl_flags_match_expected_languages():
    assert get_language_profile("ar-EG").is_rtl is True
    assert get_language_profile("ar-AE").is_rtl is True
    assert get_language_profile("en").is_rtl is False
    assert get_language_profile("it").is_rtl is False



def test_system_instructions_are_non_empty_and_long_enough():
    for code in REQUIRED_CODES:
        profile = get_language_profile(code)
        assert profile is not None
        assert profile.system_instructions
        assert len(profile.system_instructions) >= 50



def test_greeting_prompts_are_non_empty():
    for code in REQUIRED_CODES:
        profile = get_language_profile(code)
        assert profile is not None
        assert profile.greeting_prompt



def test_detect_language_returns_italian_profile():
    profile = detect_language({"preferredLanguage": "it"}, "en")
    assert profile.code == "it"



def test_detect_language_uses_fallback_for_unknown_code():
    profile = detect_language({"preferredLanguage": "xx-UNKNOWN"}, "en")
    assert profile.code == "en"



def test_detect_language_uses_fallback_for_missing_metadata():
    profile = detect_language(None, "en")
    assert profile.code == "en"



def test_switch_language_updates_profile_and_prompt():
    from app.agents.hackathon import HackathonAgent

    with patch("google.genai.Client"):
        agent = HackathonAgent(room=make_mock_room())

    agent.switch_language("it")

    assert agent.language_profile is not None
    assert agent.language_profile.code == "it"
    assert "Rispondi in italiano professionale" in agent.build_system_prompt()
