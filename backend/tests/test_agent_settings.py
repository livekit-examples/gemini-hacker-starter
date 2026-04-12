from app.agent_settings import resolve_realtime_model


def test_resolve_realtime_model_keeps_gemini_31():
    assert resolve_realtime_model("gemini-3.1-flash-live-preview") == "gemini-3.1-flash-live-preview"


def test_resolve_realtime_model_trims_whitespace():
    assert resolve_realtime_model("  gemini-3.1-flash-live-preview  ") == "gemini-3.1-flash-live-preview"


def test_resolve_realtime_model_falls_back_when_empty():
    assert resolve_realtime_model("") == "gemini-2.5-flash-native-audio-latest"
