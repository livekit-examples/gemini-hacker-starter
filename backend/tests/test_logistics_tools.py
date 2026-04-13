"""Tests for LogisticsAgent tools — Session 18.

Verifies that all three logistics tool functions return correctly shaped
outputs and respect the expected contract (status values, found/not-found,
confirmation strings, carrier metrics, etc.).
"""
import pytest

from app.tools.logistics_tools import (
    lookup_shipment,
    flag_delay,
    generate_carrier_brief,
)

VALID_STATUSES = {"in_transit", "delayed", "delivered", "customs_hold"}


# ---------------------------------------------------------------------------
# lookup_shipment
# ---------------------------------------------------------------------------


def test_lookup_shipment_known_id_returns_found():
    result = lookup_shipment("SHP-20240312-AUH")
    assert result["found"] is True


def test_lookup_shipment_known_id_has_all_keys():
    result = lookup_shipment("SHP-20240312-AUH")
    for key in ("tracking_id", "origin", "destination", "status", "eta", "carrier", "delay_days"):
        assert key in result, f"Missing key: {key}"


def test_lookup_shipment_status_is_valid():
    result = lookup_shipment("SHP-20240312-AUH")
    assert result["status"] in VALID_STATUSES


def test_lookup_shipment_origin_nonempty():
    result = lookup_shipment("SHP-20240312-AUH")
    assert isinstance(result["origin"], str)
    assert len(result["origin"]) > 0


def test_lookup_shipment_destination_nonempty():
    result = lookup_shipment("SHP-20240312-AUH")
    assert isinstance(result["destination"], str)
    assert len(result["destination"]) > 0


def test_lookup_shipment_carrier_nonempty():
    result = lookup_shipment("SHP-20240312-AUH")
    assert isinstance(result["carrier"], str)
    assert len(result["carrier"]) > 0


def test_lookup_shipment_delay_days_is_int():
    result = lookup_shipment("SHP-20240315-MXP")
    assert isinstance(result["delay_days"], int)


def test_lookup_shipment_delayed_has_nonzero_delay():
    result = lookup_shipment("SHP-20240315-MXP")
    assert result["status"] == "delayed"
    assert result["delay_days"] > 0


def test_lookup_shipment_delivered_status():
    result = lookup_shipment("SHP-20240308-DXB")
    assert result["status"] == "delivered"


def test_lookup_shipment_customs_hold_status():
    result = lookup_shipment("SHP-20240310-AUH")
    assert result["status"] == "customs_hold"


def test_lookup_shipment_case_insensitive():
    result = lookup_shipment("shp-20240312-auh")
    assert result["found"] is True


def test_lookup_shipment_unknown_id_returns_not_found():
    result = lookup_shipment("SHP-FAKE-99999")
    assert result["found"] is False


def test_lookup_shipment_empty_string_returns_not_found():
    result = lookup_shipment("")
    assert result["found"] is False


# ---------------------------------------------------------------------------
# flag_delay
# ---------------------------------------------------------------------------


def test_flag_delay_known_id_returns_string():
    result = flag_delay("SHP-20240315-MXP", "Customs documentation missing")
    assert isinstance(result, str)
    assert len(result) > 0


def test_flag_delay_contains_tracking_id():
    result = flag_delay("SHP-20240315-MXP", "Weather disruption at origin")
    assert "SHP-20240315-MXP" in result


def test_flag_delay_contains_confirmation_word():
    result = flag_delay("SHP-20240315-MXP", "Driver shortage on corridor")
    lower = result.lower()
    assert "flag" in lower or "notif" in lower or "published" in lower or "recorded" in lower


def test_flag_delay_unknown_id_still_returns_string():
    result = flag_delay("SHP-NONEXISTENT-001", "Test reason")
    assert isinstance(result, str)
    assert len(result) > 0


def test_flag_delay_reason_captured():
    reason = "Typhoon season port congestion"
    result = flag_delay("SHP-20240301-SHJ", reason)
    assert isinstance(result, str)


# ---------------------------------------------------------------------------
# generate_carrier_brief
# ---------------------------------------------------------------------------


def test_generate_carrier_brief_emirates_returns_found():
    result = generate_carrier_brief("Emirates SkyCargo")
    assert result["found"] is True


def test_generate_carrier_brief_partial_name_returns_found():
    result = generate_carrier_brief("Emirates")
    assert result["found"] is True


def test_generate_carrier_brief_dhl_returns_found():
    result = generate_carrier_brief("DHL")
    assert result["found"] is True


def test_generate_carrier_brief_fedex_returns_found():
    result = generate_carrier_brief("FedEx")
    assert result["found"] is True


def test_generate_carrier_brief_agility_returns_found():
    result = generate_carrier_brief("Agility")
    assert result["found"] is True


def test_generate_carrier_brief_has_all_keys():
    result = generate_carrier_brief("Emirates")
    for key in ("carrier", "on_time_rate_pct", "avg_delay_days", "open_incidents", "recommendation"):
        assert key in result, f"Missing key: {key}"


def test_generate_carrier_brief_on_time_rate_is_float():
    result = generate_carrier_brief("Emirates")
    assert isinstance(result["on_time_rate_pct"], float)
    assert 0.0 <= result["on_time_rate_pct"] <= 100.0


def test_generate_carrier_brief_avg_delay_is_numeric():
    result = generate_carrier_brief("DHL")
    assert isinstance(result["avg_delay_days"], (int, float))
    assert result["avg_delay_days"] >= 0


def test_generate_carrier_brief_open_incidents_is_int():
    result = generate_carrier_brief("Agility")
    assert isinstance(result["open_incidents"], int)
    assert result["open_incidents"] >= 0


def test_generate_carrier_brief_recommendation_nonempty():
    result = generate_carrier_brief("FedEx")
    assert isinstance(result["recommendation"], str)
    assert len(result["recommendation"]) > 0


def test_generate_carrier_brief_unknown_returns_not_found():
    result = generate_carrier_brief("NonExistentCarrierXYZ999")
    assert result["found"] is False


def test_generate_carrier_brief_case_insensitive():
    result = generate_carrier_brief("fedex international")
    assert result["found"] is True


# ---------------------------------------------------------------------------
# LogisticsAgent instantiation (registry integration)
# ---------------------------------------------------------------------------


def test_logistics_agent_in_registry():
    from app.agents.registry import REGISTRY
    from app.agents.logistics import LogisticsAgent

    assert "logistics" in REGISTRY
    assert REGISTRY["logistics"] is LogisticsAgent


def test_get_agent_logistics_returns_logistics_agent():
    from unittest.mock import MagicMock

    from app.agents.registry import get_agent
    from app.agents.logistics import LogisticsAgent

    room = MagicMock()
    room.on = MagicMock()
    room.remote_participants = {}

    agent = get_agent("logistics", room)
    assert isinstance(agent, LogisticsAgent)


def test_logistics_agent_persona_name():
    from unittest.mock import MagicMock

    from app.agents.logistics import LogisticsAgent

    room = MagicMock()
    room.on = MagicMock()
    room.remote_participants = {}

    agent = LogisticsAgent(room=room)
    assert agent.persona_name == "Elena"


def test_logistics_agent_has_three_tools():
    from unittest.mock import MagicMock

    from app.agents.logistics import LogisticsAgent

    room = MagicMock()
    room.on = MagicMock()
    room.remote_participants = {}

    agent = LogisticsAgent(room=room)
    assert len(agent._tool_registry) == 3


def test_logistics_agent_system_prompt_contains_persona():
    from unittest.mock import MagicMock

    from app.agents.logistics import LogisticsAgent

    room = MagicMock()
    room.on = MagicMock()
    room.remote_participants = {}

    agent = LogisticsAgent(room=room)
    prompt = agent.build_system_prompt()
    assert isinstance(prompt, str)
    assert len(prompt) > 50
    assert "Elena" in prompt or "logistics" in prompt.lower()
