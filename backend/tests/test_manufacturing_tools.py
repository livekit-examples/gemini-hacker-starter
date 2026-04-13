"""Tests for ManufacturingAgent tools — Session 16.

Verifies that all three manufacturing tool functions return correctly shaped
outputs and respect the expected contract (severity values, SOP found/not-found,
report format, etc.).
"""
import pytest

from app.tools.manufacturing_tools import (
    detect_visual_defect,
    generate_defect_report,
    lookup_sop,
)

VALID_SEVERITIES = {"critical", "major", "minor"}


# ---------------------------------------------------------------------------
# detect_visual_defect
# ---------------------------------------------------------------------------


def test_detect_returns_all_four_keys():
    result = detect_visual_defect("hairline crack visible on the left load-bearing bracket")
    assert "defect_type" in result
    assert "severity" in result
    assert "area" in result
    assert "recommended_action" in result


def test_detect_severity_is_valid_value():
    result = detect_visual_defect("weld porosity on the frame cross-member")
    assert result["severity"] in VALID_SEVERITIES


def test_detect_crack_is_critical():
    result = detect_visual_defect("hairline crack visible on structural bracket")
    assert result["severity"] == "critical"


def test_detect_weld_defect_is_major():
    result = detect_visual_defect("weld undercut on the frame joint")
    assert result["severity"] in {"critical", "major"}


def test_detect_burr_is_minor():
    result = detect_visual_defect("small burr on drilled hole edge")
    assert result["severity"] == "minor"


def test_detect_scratch_returns_minor():
    result = detect_visual_defect("surface scratch on the exterior panel")
    assert result["severity"] == "minor"


def test_detect_solder_bridge_is_critical():
    result = detect_visual_defect("solder bridge between adjacent PCB pads")
    assert result["severity"] == "critical"


def test_detect_unknown_defect_returns_default():
    result = detect_visual_defect("something unusual that does not match any keyword")
    assert result["severity"] in VALID_SEVERITIES
    assert isinstance(result["recommended_action"], str)
    assert len(result["recommended_action"]) > 0


def test_detect_recommended_action_is_nonempty():
    result = detect_visual_defect("paint run on class A panel surface")
    assert isinstance(result["recommended_action"], str)
    assert len(result["recommended_action"]) > 0


def test_detect_area_is_nonempty():
    result = detect_visual_defect("delamination on composite panel")
    assert isinstance(result["area"], str)
    assert len(result["area"]) > 0


def test_detect_defect_type_is_nonempty():
    result = detect_visual_defect("corrosion on steel bracket")
    assert isinstance(result["defect_type"], str)
    assert len(result["defect_type"]) > 0


# ---------------------------------------------------------------------------
# generate_defect_report
# ---------------------------------------------------------------------------


def test_generate_report_returns_string():
    defects = [
        {
            "defect_type": "structural_crack",
            "severity": "critical",
            "area": "load-bearing bracket",
            "recommended_action": "Quarantine and raise NCR.",
        }
    ]
    report = generate_defect_report(defects)
    assert isinstance(report, str)
    assert len(report) > 0


def test_generate_report_contains_defect_type():
    defects = [
        {
            "defect_type": "weld_porosity",
            "severity": "major",
            "area": "weld bead",
            "recommended_action": "Grind and re-weld.",
        }
    ]
    report = generate_defect_report(defects)
    assert "weld_porosity" in report


def test_generate_report_contains_severity():
    defects = [
        {
            "defect_type": "burr_or_sharp_edge",
            "severity": "minor",
            "area": "drilled hole",
            "recommended_action": "Deburr and re-inspect.",
        }
    ]
    report = generate_defect_report(defects)
    assert "MINOR" in report or "minor" in report


def test_generate_report_multiple_defects():
    defects = [
        {
            "defect_type": "structural_crack",
            "severity": "critical",
            "area": "bracket",
            "recommended_action": "Stop production.",
        },
        {
            "defect_type": "surface_scratch",
            "severity": "minor",
            "area": "panel",
            "recommended_action": "Polish and re-inspect.",
        },
    ]
    report = generate_defect_report(defects)
    assert "structural_crack" in report
    assert "surface_scratch" in report
    assert "Total defects: 2" in report


def test_generate_report_critical_flag():
    defects = [
        {
            "defect_type": "structural_fracture",
            "severity": "critical",
            "area": "structural zone",
            "recommended_action": "Stop production.",
        }
    ]
    report = generate_defect_report(defects)
    assert "CRITICAL" in report


def test_generate_report_empty_list():
    report = generate_defect_report([])
    assert isinstance(report, str)
    assert "No defects" in report or len(report) > 0


# ---------------------------------------------------------------------------
# lookup_sop
# ---------------------------------------------------------------------------


def test_lookup_sop_torque_returns_found():
    result = lookup_sop("torque")
    assert result["found"] is True


def test_lookup_sop_torque_has_nonempty_steps():
    result = lookup_sop("torque")
    assert isinstance(result["steps"], list)
    assert len(result["steps"]) > 0


def test_lookup_sop_torque_has_procedure_id():
    result = lookup_sop("torque")
    assert isinstance(result["procedure_id"], str)
    assert result["procedure_id"].startswith("SOP-")


def test_lookup_sop_loto_returns_found():
    result = lookup_sop("lockout")
    assert result["found"] is True


def test_lookup_sop_weld_inspection_returns_found():
    result = lookup_sop("weld inspection")
    assert result["found"] is True


def test_lookup_sop_ppe_grinding_returns_found():
    result = lookup_sop("ppe grinding")
    assert result["found"] is True


def test_lookup_sop_unknown_returns_not_found():
    result = lookup_sop("xyznotexist_procedure_abc123")
    assert result["found"] is False
    assert result["steps"] == []


def test_lookup_sop_result_has_all_keys():
    result = lookup_sop("torque")
    assert "procedure_id" in result
    assert "title" in result
    assert "steps" in result
    assert "found" in result


def test_lookup_sop_steps_are_strings():
    result = lookup_sop("torque")
    assert all(isinstance(s, str) for s in result["steps"])


def test_lookup_sop_error_code_e14_returns_found():
    result = lookup_sop("E-14")
    assert result["found"] is True


def test_lookup_sop_forklift_returns_found():
    result = lookup_sop("forklift")
    assert result["found"] is True


# ---------------------------------------------------------------------------
# ManufacturingAgent instantiation (registry integration)
# ---------------------------------------------------------------------------


def test_manufacturing_agent_in_registry():
    from app.agents.registry import REGISTRY
    from app.agents.manufacturing import ManufacturingAgent

    assert "manufacturing" in REGISTRY
    assert REGISTRY["manufacturing"] is ManufacturingAgent


def test_get_agent_manufacturing_returns_manufacturing_agent():
    from unittest.mock import MagicMock

    from app.agents.registry import get_agent
    from app.agents.manufacturing import ManufacturingAgent

    room = MagicMock()
    room.on = MagicMock()
    room.remote_participants = {}

    agent = get_agent("manufacturing", room)
    assert isinstance(agent, ManufacturingAgent)


def test_manufacturing_agent_persona_name():
    from unittest.mock import MagicMock

    from app.agents.manufacturing import ManufacturingAgent

    room = MagicMock()
    room.on = MagicMock()
    room.remote_participants = {}

    agent = ManufacturingAgent(room=room)
    assert agent.persona_name == "Marco"


def test_manufacturing_agent_has_three_tools():
    from unittest.mock import MagicMock

    from app.agents.manufacturing import ManufacturingAgent

    room = MagicMock()
    room.on = MagicMock()
    room.remote_participants = {}

    agent = ManufacturingAgent(room=room)
    assert len(agent._tool_registry) == 3


def test_manufacturing_agent_system_prompt_contains_persona():
    from unittest.mock import MagicMock

    from app.agents.manufacturing import ManufacturingAgent

    room = MagicMock()
    room.on = MagicMock()
    room.remote_participants = {}

    agent = ManufacturingAgent(room=room)
    prompt = agent.build_system_prompt()
    assert isinstance(prompt, str)
    assert len(prompt) > 50
    assert "Marco" in prompt or "quality" in prompt.lower()
