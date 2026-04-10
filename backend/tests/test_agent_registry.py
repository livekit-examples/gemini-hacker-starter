"""Tests for the agent registry (Session 3).

Verifies that REGISTRY contains expected industry slugs, that get_agent()
returns correctly typed instances, and that unknown slugs fall back to
DefaultAgent without raising.
"""
from unittest.mock import MagicMock, patch


def make_mock_room() -> MagicMock:
    room = MagicMock()
    room.on = MagicMock()
    room.remote_participants = {}
    return room


# ---------------------------------------------------------------------------
# REGISTRY contents
# ---------------------------------------------------------------------------


def test_registry_contains_hackathon_key():
    from app.agents.registry import REGISTRY

    assert "hackathon" in REGISTRY


def test_registry_contains_all_expected_industry_slugs():
    from app.agents.registry import REGISTRY

    expected_slugs = {"hackathon", "sales", "manufacturing", "logistics", "real_estate", "dental", "comune"}
    for slug in expected_slugs:
        assert slug in REGISTRY, f"Missing slug '{slug}' in REGISTRY"


def test_registry_values_are_persona_agent_subclasses():
    from app.agents.persona import PersonaAgent
    from app.agents.registry import REGISTRY

    for slug, agent_class in REGISTRY.items():
        assert issubclass(agent_class, PersonaAgent), (
            f"REGISTRY['{slug}'] = {agent_class} is not a PersonaAgent subclass"
        )


# ---------------------------------------------------------------------------
# get_agent — known industry
# ---------------------------------------------------------------------------


def test_get_agent_hackathon_returns_hackathon_agent():
    from app.agents.hackathon import HackathonAgent
    from app.agents.registry import get_agent

    with patch("google.genai.Client"):
        agent = get_agent("hackathon", make_mock_room())

    assert isinstance(agent, HackathonAgent)


# ---------------------------------------------------------------------------
# get_agent — unknown industry (graceful fallback)
# ---------------------------------------------------------------------------


def test_get_agent_unknown_returns_default_agent():
    from app.agents.registry import DefaultAgent, get_agent

    agent = get_agent("unknown_industry_xyz_999", make_mock_room())
    assert isinstance(agent, DefaultAgent)


def test_get_agent_unknown_does_not_raise():
    from app.agents.registry import get_agent

    # Must not raise for any unknown slug.
    agent = get_agent("totally_nonexistent_slug", make_mock_room())
    assert agent is not None


def test_default_agent_has_persona_name():
    from app.agents.registry import DefaultAgent, get_agent

    agent = get_agent("unknown_slug", make_mock_room())
    assert isinstance(agent, DefaultAgent)
    assert agent.persona_name  # non-empty


# ---------------------------------------------------------------------------
# DefaultAgent itself
# ---------------------------------------------------------------------------


def test_default_agent_instantiates_directly():
    from app.agents.registry import DefaultAgent

    agent = DefaultAgent(room=make_mock_room())
    assert agent is not None
    assert agent.persona_name
    assert agent.persona_instructions


def test_default_agent_build_system_prompt_non_empty():
    from app.agents.registry import DefaultAgent

    agent = DefaultAgent(room=make_mock_room())
    prompt = agent.build_system_prompt()
    assert isinstance(prompt, str)
    assert len(prompt) > 50
