from app.agent_settings import resolve_stt_model


def test_resolve_stt_model_keeps_explicit_value():
    assert resolve_stt_model("deepgram/nova-3") == "deepgram/nova-3"


def test_resolve_stt_model_falls_back_when_empty():
    assert resolve_stt_model("") == "auto"


def test_resolve_stt_model_trims_whitespace():
    assert resolve_stt_model("  auto  ") == "auto"
