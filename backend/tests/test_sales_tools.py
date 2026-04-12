"""Tests for SalesAgent tools — Sessions 14 & 15."""
import pytest
from unittest.mock import MagicMock, AsyncMock

from app.tools.sales_tools import (
    analyze_screen_content,
    generate_proposal_section,
    log_talking_points,
)

VALID_PRIORITIES = {"high", "medium", "low"}

# ---------------------------------------------------------------------------
# analyze_screen_content
# ---------------------------------------------------------------------------


def test_analyze_returns_all_three_keys():
    result = analyze_screen_content("CRM showing 3 open opportunities")
    assert "findings" in result
    assert "recommendations" in result
    assert "priority" in result


def test_analyze_priority_is_valid_value():
    result = analyze_screen_content("CRM showing 3 open opportunities")
    assert result["priority"] in VALID_PRIORITIES


def test_analyze_high_priority_for_competitor_and_contract():
    result = analyze_screen_content("Contract stage deal — competitor mentioned in notes")
    assert result["priority"] == "high"


def test_analyze_high_priority_for_executive():
    result = analyze_screen_content("CEO and CFO are now involved in the procurement")
    assert result["priority"] == "high"


def test_analyze_high_priority_for_renewal():
    result = analyze_screen_content("Renewal is expiring next month, urgent to close")
    assert result["priority"] == "high"


def test_analyze_low_priority_for_cold_lead():
    result = analyze_screen_content("Early stage discovery, cold prospect, no budget yet")
    assert result["priority"] == "low"


def test_analyze_medium_priority_for_generic_description():
    result = analyze_screen_content("Sales dashboard with some pipeline data")
    assert result["priority"] == "medium"


def test_analyze_findings_is_list_of_strings():
    result = analyze_screen_content("Proposal stage deal with competitor")
    assert isinstance(result["findings"], list)
    assert all(isinstance(f, str) for f in result["findings"])


def test_analyze_recommendations_is_list_of_strings():
    result = analyze_screen_content("Proposal stage deal with competitor")
    assert isinstance(result["recommendations"], list)
    assert all(isinstance(r, str) for r in result["recommendations"])


def test_analyze_findings_non_empty():
    result = analyze_screen_content("Proposal stage with procurement team involved")
    assert len(result["findings"]) > 0


def test_analyze_recommendations_non_empty():
    result = analyze_screen_content("Proposal stage with procurement team involved")
    assert len(result["recommendations"]) > 0


def test_analyze_competitor_mention_in_findings():
    result = analyze_screen_content("Competitor is mentioned in the deal notes")
    combined = " ".join(result["findings"]).lower()
    assert "competitor" in combined


def test_analyze_empty_string_returns_defaults():
    result = analyze_screen_content("")
    assert result["priority"] in VALID_PRIORITIES
    assert len(result["findings"]) > 0
    assert len(result["recommendations"]) > 0


# ---------------------------------------------------------------------------
# generate_proposal_section
# ---------------------------------------------------------------------------


def test_generate_executive_summary_returns_non_empty():
    result = generate_proposal_section("executive_summary", "SMB logistics company")
    assert isinstance(result, str)
    assert len(result) > 0


def test_generate_executive_summary_contains_context():
    result = generate_proposal_section("executive_summary", "SMB logistics company")
    assert "SMB logistics company" in result


def test_generate_problem_statement():
    result = generate_proposal_section("problem_statement", "retail chain")
    assert isinstance(result, str)
    assert "retail chain" in result


def test_generate_solution_overview():
    result = generate_proposal_section("solution_overview", "healthcare provider")
    assert isinstance(result, str)
    assert len(result) > 0


def test_generate_value_proposition():
    result = generate_proposal_section("value_proposition", "manufacturing firm")
    assert isinstance(result, str)
    assert len(result) > 0


def test_generate_pricing_section():
    result = generate_proposal_section("pricing", "fintech startup")
    assert isinstance(result, str)
    assert len(result) > 0


def test_generate_next_steps_section():
    result = generate_proposal_section("next_steps", "logistics company Milan")
    assert "logistics company Milan" in result


def test_generate_normalises_spaces_in_section_name():
    result_underscores = generate_proposal_section("executive_summary", "Acme")
    result_spaces = generate_proposal_section("executive summary", "Acme")
    assert result_underscores == result_spaces


def test_generate_normalises_dashes_in_section_name():
    result_underscores = generate_proposal_section("next_steps", "Acme")
    result_dashes = generate_proposal_section("next-steps", "Acme")
    assert result_underscores == result_dashes


def test_generate_unknown_section_returns_non_empty():
    result = generate_proposal_section("introduction", "some company")
    assert isinstance(result, str)
    assert len(result) > 0


def test_generate_empty_context_uses_fallback():
    result = generate_proposal_section("executive_summary", "")
    assert isinstance(result, str)
    assert len(result) > 0


# ---------------------------------------------------------------------------
# log_talking_points
# ---------------------------------------------------------------------------


def test_log_returns_string():
    result = log_talking_points(["Build rapport", "Ask about Q4 targets"])
    assert isinstance(result, str)


def test_log_confirmation_contains_published_or_sent():
    result = log_talking_points(["Build rapport", "Ask about Q4 targets"])
    assert "published" in result.lower() or "sent" in result.lower()


def test_log_includes_talking_points_content():
    points = ["Lead with ROI", "Address security objections"]
    result = log_talking_points(points)
    assert "Lead with ROI" in result
    assert "Address security objections" in result


def test_log_empty_list_returns_non_empty_string():
    result = log_talking_points([])
    assert isinstance(result, str)
    assert len(result) > 0


def test_log_single_point():
    result = log_talking_points(["Close the deal by Friday"])
    assert "Close the deal by Friday" in result


def test_log_many_points():
    points = [f"Point {i}" for i in range(10)]
    result = log_talking_points(points)
    assert isinstance(result, str)
    assert "Point 0" in result
    assert "Point 9" in result


# ---------------------------------------------------------------------------
# SalesAgent registry integration
# ---------------------------------------------------------------------------


def test_sales_agent_registered_in_registry():
    from app.agents.registry import REGISTRY, get_agent
    assert "sales" in REGISTRY


def test_get_sales_agent_returns_sales_agent():
    from app.agents.registry import get_agent
    from app.agents.sales import SalesAgent
    mock_room = MagicMock()
    agent = get_agent("sales", mock_room)
    assert isinstance(agent, SalesAgent)


def test_sales_agent_instantiates_without_error():
    from app.agents.sales import SalesAgent
    mock_room = MagicMock()
    agent = SalesAgent(room=mock_room)
    assert agent.persona_name == "Aria"


def test_sales_agent_has_correct_persona_role():
    from app.agents.sales import SalesAgent
    mock_room = MagicMock()
    agent = SalesAgent(room=mock_room)
    assert "Sales Strategist" in agent.persona_instructions or "sales" in agent.persona_instructions.lower()


def test_sales_agent_has_three_tools():
    from app.agents.sales import SalesAgent
    mock_room = MagicMock()
    agent = SalesAgent(room=mock_room)
    assert len(agent._tool_registry) == 3


def test_sales_agent_build_system_prompt_non_empty():
    from app.agents.sales import SalesAgent
    mock_room = MagicMock()
    agent = SalesAgent(room=mock_room)
    prompt = agent.build_system_prompt()
    assert len(prompt) > 50
    assert "Aria" in prompt
