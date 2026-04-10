"""Tests for the agent class hierarchy (Session 3).

Verifies that BaseAgent → PersonaAgent → HackathonAgent is correctly set up,
that build_system_prompt() produces well-formed output, and that register_tool
populates _tool_registry.
"""
from unittest.mock import MagicMock, patch

import pytest


def make_mock_room() -> MagicMock:
    """Return a minimal mock of livekit.rtc.Room suitable for agent tests."""
    room = MagicMock()
    room.on = MagicMock()
    room.remote_participants = {}
    return room


# ---------------------------------------------------------------------------
# Inheritance chain
# ---------------------------------------------------------------------------


def test_persona_agent_is_subclass_of_base_agent():
    from app.agents.base import BaseAgent
    from app.agents.persona import PersonaAgent

    assert issubclass(PersonaAgent, BaseAgent)


def test_hackathon_agent_is_subclass_of_persona_agent():
    from app.agents.hackathon import HackathonAgent
    from app.agents.persona import PersonaAgent

    assert issubclass(HackathonAgent, PersonaAgent)


# ---------------------------------------------------------------------------
# HackathonAgent instantiation
# ---------------------------------------------------------------------------


def test_hackathon_agent_instantiates_without_error():
    from app.agents.hackathon import HackathonAgent

    with patch("google.genai.Client"):
        agent = HackathonAgent(room=make_mock_room())

    assert agent is not None
    assert isinstance(agent.persona_name, str)
    assert agent.persona_name  # non-empty


def test_hackathon_agent_has_room_reference():
    from app.agents.hackathon import HackathonAgent

    mock_room = make_mock_room()
    with patch("google.genai.Client"):
        agent = HackathonAgent(room=mock_room)

    assert agent._room is mock_room


def test_hackathon_agent_registers_room_event_handlers():
    from app.agents.hackathon import HackathonAgent

    mock_room = make_mock_room()
    with patch("google.genai.Client"):
        HackathonAgent(room=mock_room)

    # BaseAgent registers two event handlers on the room.
    calls = [call.args[0] for call in mock_room.on.call_args_list]
    assert "track_subscribed" in calls
    assert "track_unsubscribed" in calls


# ---------------------------------------------------------------------------
# build_system_prompt
# ---------------------------------------------------------------------------


def test_build_system_prompt_returns_non_empty_string():
    from app.agents.hackathon import HackathonAgent

    with patch("google.genai.Client"):
        agent = HackathonAgent(room=make_mock_room())

    prompt = agent.build_system_prompt()
    assert isinstance(prompt, str)
    assert len(prompt) > 0


def test_build_system_prompt_contains_video_awareness():
    from app.agents.hackathon import HackathonAgent
    from app.agents.base import BASE_VIDEO_AWARENESS

    with patch("google.genai.Client"):
        agent = HackathonAgent(room=make_mock_room())

    prompt = agent.build_system_prompt()
    # The BASE_VIDEO_AWARENESS preamble must appear in the prompt.
    assert BASE_VIDEO_AWARENESS[:50] in prompt


def test_build_system_prompt_contains_persona_instructions():
    from app.agents.hackathon import HackathonAgent, PERSONA_INSTRUCTIONS

    with patch("google.genai.Client"):
        agent = HackathonAgent(room=make_mock_room())

    prompt = agent.build_system_prompt()
    # At least the first 80 chars of persona instructions must appear.
    assert PERSONA_INSTRUCTIONS[:80] in prompt


# ---------------------------------------------------------------------------
# register_tool / _tool_registry
# ---------------------------------------------------------------------------


def test_register_tool_adds_to_tool_registry():
    from app.agents.hackathon import HackathonAgent

    with patch("google.genai.Client"):
        agent = HackathonAgent(room=make_mock_room())

    initial_len = len(agent._tool_registry)

    def dummy_tool():
        pass

    agent.register_tool(dummy_tool)
    assert len(agent._tool_registry) == initial_len + 1
    assert dummy_tool in agent._tool_registry


def test_hackathon_agent_registers_expected_tools():
    from app.agents.hackathon import HackathonAgent

    with patch("google.genai.Client"):
        agent = HackathonAgent(room=make_mock_room())

    # HackathonAgent._register_tools() should add generate_image, start_music, stop_music.
    assert len(agent._tool_registry) >= 3


# ---------------------------------------------------------------------------
# switch_language (graceful no-op before Session 10)
# ---------------------------------------------------------------------------


def test_switch_language_does_not_raise_before_session_10():
    from app.agents.hackathon import HackathonAgent

    with patch("google.genai.Client"):
        agent = HackathonAgent(room=make_mock_room())

    # Language detector module is not yet available — must not raise.
    agent.switch_language("it")
