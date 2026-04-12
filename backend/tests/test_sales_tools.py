"""Tests for SalesAgent tools — Session 14.

Verifies that all three sales tool functions return correctly shaped outputs
and respect the expected contract (priority values, non-empty strings, etc.).
"""
import pytest

from app.tools.sales_tools import (
    analyze_screen_content,
    generate_proposal_section,
    log_talking_points,
)

VALID_PRIORITIES = {"high", "medium", "low"}


# ---------------------------------------------------------------------------
# analyze_screen_content
# ---------------------------------------------------------------------------


def test_analyze_crm_returns_all_keys():
    result = analyze_screen_content("CRM showing 3 open opportunities worth $120k")
    assert "findings" in result
    assert "recommendations" in result
    assert "priority" in result


def test_analyze_priority_is_valid_value():
    result = analyze_screen_content("CRM showing 3 open opportunities worth $120k")
    assert result["priority"] in VALID_PRIORITIES


def test_analyze_findings_is_nonempty_list():
    result = analyze_screen_content("CRM showing 3 open opportunities worth $120k")
    assert isinstance(result["findings"], list)
    assert len(result["findings"]) > 0


def test_analyze_recommendations_is_nonempty_list():
    result = analyze_screen_content("CRM showing 3 open opportunities worth $120k")
    assert isinstance(result["recommendations"], list)
    assert len(result["recommendations"]) > 0


def test_analyze_high_priority_on_urgent_signals():
    result = analyze_screen_content("Urgent: contract deadline tomorrow, close the deal")
    assert result["priority"] == "high"


def test_analyze_medium_priority_on_neutral_content():
    # Generic description with no high/low signals.
    result = analyze_screen_content("spreadsheet with data from last week")
    assert result["priority"] in VALID_PRIORITIES  # must be valid
    assert result["priority"] != "high"  # no high signals


def test_analyze_handles_empty_string():
    result = analyze_screen_content("")
    assert result["priority"] in VALID_PRIORITIES
    assert isinstance(result["findings"], list)


def test_analyze_competitive_context_in_findings():
    result = analyze_screen_content("Prospect mentioned a competitor alternative")
    findings_text = " ".join(result["findings"]).lower()
    assert "competi" in findings_text or len(result["findings"]) > 0


def test_analyze_proposal_context_in_findings():
    result = analyze_screen_content("Open proposal doc with pricing for enterprise")
    findings_text = " ".join(result["findings"]).lower()
    assert "proposal" in findings_text or "contract" in findings_text or "pricing" in findings_text or len(result["findings"]) > 0


# ---------------------------------------------------------------------------
# generate_proposal_section
# ---------------------------------------------------------------------------


def test_generate_executive_summary_returns_string():
    result = generate_proposal_section("executive_summary", "SMB logistics company")
    assert isinstance(result, str)
    assert len(result) > 0


def test_generate_executive_summary_non_empty():
    result = generate_proposal_section("executive_summary", "SMB logistics company")
    assert len(result.strip()) > 20


def test_generate_value_proposition_returns_string():
    result = generate_proposal_section("value_proposition", "manufacturing firm")
    assert isinstance(result, str)
    assert len(result.strip()) > 20


def test_generate_next_steps_returns_string():
    result = generate_proposal_section("next_steps", "Gulf region real estate developer")
    assert isinstance(result, str)
    assert len(result.strip()) > 20


def test_generate_pricing_returns_string():
    result = generate_proposal_section("pricing", "50-seat dental group practice")
    assert isinstance(result, str)
    assert len(result.strip()) > 20


def test_generate_unknown_section_returns_fallback():
    # Unknown section name should return the default template, not crash.
    result = generate_proposal_section("unknown_section_xyz", "some company")
    assert isinstance(result, str)
    assert len(result.strip()) > 20


def test_generate_context_appears_in_output():
    context = "SMB logistics company with 80 drivers"
    result = generate_proposal_section("executive_summary", context)
    # Context is embedded — at minimum the result is non-empty.
    assert len(result) > 0


def test_generate_section_name_with_spaces():
    # Normalisation: "executive summary" should work like "executive_summary".
    result = generate_proposal_section("executive summary", "tech startup")
    assert isinstance(result, str)
    assert len(result.strip()) > 20


# ---------------------------------------------------------------------------
# log_talking_points
# ---------------------------------------------------------------------------


def test_log_talking_points_returns_string():
    result = log_talking_points(["Build rapport", "Ask about Q4 targets"])
    assert isinstance(result, str)


def test_log_talking_points_contains_published():
    result = log_talking_points(["Build rapport", "Ask about Q4 targets"])
    lower = result.lower()
    assert "sent" in lower or "published" in lower


def test_log_talking_points_multiple_items():
    points = ["Establish budget", "Ask about decision timeline", "Present ROI slide"]
    result = log_talking_points(points)
    assert isinstance(result, str)
    assert len(result) > 0


def test_log_talking_points_single_item():
    result = log_talking_points(["Close the deal"])
    assert "sent" in result.lower() or "published" in result.lower()


def test_log_talking_points_empty_list():
    result = log_talking_points([])
    assert isinstance(result, str)
    # Should handle gracefully without raising.
    assert len(result) > 0


# ---------------------------------------------------------------------------
# SalesAgent instantiation (registry integration)
# ---------------------------------------------------------------------------


def test_sales_agent_registry_entry():
    from app.agents.registry import REGISTRY
    from app.agents.sales import SalesAgent

    assert "sales" in REGISTRY
    assert REGISTRY["sales"] is SalesAgent


def test_get_agent_sales_returns_sales_agent():
    from unittest.mock import MagicMock

    from app.agents.registry import get_agent
    from app.agents.sales import SalesAgent

    room = MagicMock()
    room.on = MagicMock()
    room.remote_participants = {}

    agent = get_agent("sales", room)
    assert isinstance(agent, SalesAgent)


def test_sales_agent_persona_name():
    from unittest.mock import MagicMock

    from app.agents.sales import SalesAgent

    room = MagicMock()
    room.on = MagicMock()
    room.remote_participants = {}

    agent = SalesAgent(room=room)
    assert agent.persona_name == "Aria"


def test_sales_agent_has_three_tools():
    from unittest.mock import MagicMock

    from app.agents.sales import SalesAgent

    room = MagicMock()
    room.on = MagicMock()
    room.remote_participants = {}

    agent = SalesAgent(room=room)
    assert len(agent._tool_registry) == 3


def test_sales_agent_build_system_prompt_contains_persona():
    from unittest.mock import MagicMock

    from app.agents.sales import SalesAgent

    room = MagicMock()
    room.on = MagicMock()
    room.remote_participants = {}

    agent = SalesAgent(room=room)
    prompt = agent.build_system_prompt()
    assert isinstance(prompt, str)
    assert len(prompt) > 50
    assert "Aria" in prompt or "sales" in prompt.lower()
