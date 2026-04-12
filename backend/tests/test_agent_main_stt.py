"""Regression tests for AgentSession configuration.

Ensures realtime sessions do not force LiveKit Inference STT.
"""

from unittest.mock import patch


def test_build_agent_session_does_not_set_explicit_stt():
    from app import agent_main

    selected_model = "gemini-3.1-flash-live-preview"
    selected_voice = "Aoede"

    with (
        patch("app.agent_main.AgentSession") as mock_session,
        patch("app.agent_main.lk_google.realtime.RealtimeModel") as mock_rt,
    ):
        agent_main._build_agent_session(selected_model, selected_voice)

    mock_rt.assert_called_once_with(
        model=selected_model,
        voice=selected_voice,
    )
    _, kwargs = mock_session.call_args
    assert "stt" not in kwargs
