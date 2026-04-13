"""Tests for the manufacturing SOP data file — Session 16.

Verifies that the JSON data meets the structural requirements:
- Exactly 20 entries
- All entries have required fields
- Steps list is non-empty for all entries
"""
import json
from pathlib import Path

import pytest

_SOP_FILE = Path(__file__).parent.parent / "app" / "data" / "manufacturing_sop.json"


@pytest.fixture(scope="module")
def sop_data() -> list[dict]:
    with _SOP_FILE.open(encoding="utf-8") as f:
        return json.load(f)


def test_sop_file_exists():
    assert _SOP_FILE.exists(), f"SOP data file not found at {_SOP_FILE}"


def test_sop_has_exactly_20_entries(sop_data):
    assert len(sop_data) == 20, f"Expected 20 SOP entries, got {len(sop_data)}"


def test_all_entries_have_procedure_id(sop_data):
    for entry in sop_data:
        assert "procedure_id" in entry, f"Missing procedure_id: {entry}"
        assert isinstance(entry["procedure_id"], str)
        assert entry["procedure_id"].startswith("SOP-")


def test_all_entries_have_title(sop_data):
    for entry in sop_data:
        assert "title" in entry, f"Missing title: {entry}"
        assert isinstance(entry["title"], str)
        assert len(entry["title"]) > 0, "Title must not be empty"


def test_all_entries_have_keywords(sop_data):
    for entry in sop_data:
        assert "keywords" in entry, f"Missing keywords: {entry}"
        assert isinstance(entry["keywords"], list)
        assert len(entry["keywords"]) > 0, f"Keywords list empty for {entry['procedure_id']}"


def test_all_entries_have_steps(sop_data):
    for entry in sop_data:
        assert "steps" in entry, f"Missing steps: {entry}"
        assert isinstance(entry["steps"], list)


def test_steps_nonempty_for_all_entries(sop_data):
    for entry in sop_data:
        assert len(entry["steps"]) > 0, (
            f"Steps list is empty for {entry['procedure_id']}: {entry['title']}"
        )


def test_procedure_ids_are_unique(sop_data):
    ids = [e["procedure_id"] for e in sop_data]
    assert len(ids) == len(set(ids)), "Duplicate procedure_id values found"


def test_covers_torque_procedures(sop_data):
    """At least one SOP should cover torque specifications."""
    titles = [e["title"].lower() for e in sop_data]
    assert any("torque" in t for t in titles), "No torque specification SOP found"


def test_covers_loto_procedures(sop_data):
    """At least one SOP should cover lockout/tagout."""
    titles = [e["title"].lower() for e in sop_data]
    keywords = [kw for e in sop_data for kw in e.get("keywords", [])]
    assert any("lockout" in t or "loto" in t for t in titles + keywords), (
        "No LOTO procedure found"
    )


def test_covers_inspection_procedures(sop_data):
    """At least one SOP should cover inspection criteria."""
    titles = [e["title"].lower() for e in sop_data]
    assert any("inspection" in t or "inspect" in t for t in titles), (
        "No inspection SOP found"
    )


def test_covers_ppe_procedures(sop_data):
    """At least one SOP should cover PPE requirements."""
    keywords_flat = [kw.lower() for e in sop_data for kw in e.get("keywords", [])]
    assert any("ppe" in kw for kw in keywords_flat), "No PPE procedure found"


def test_covers_machine_error_procedures(sop_data):
    """At least one SOP should cover machine error recovery."""
    keywords_flat = [kw.lower() for e in sop_data for kw in e.get("keywords", [])]
    assert any("error" in kw or "fault" in kw or "alarm" in kw for kw in keywords_flat), (
        "No machine error recovery procedure found"
    )


def test_steps_are_strings(sop_data):
    for entry in sop_data:
        for step in entry["steps"]:
            assert isinstance(step, str), (
                f"Non-string step in {entry['procedure_id']}: {step!r}"
            )


def test_keywords_are_strings(sop_data):
    for entry in sop_data:
        for kw in entry["keywords"]:
            assert isinstance(kw, str), (
                f"Non-string keyword in {entry['procedure_id']}: {kw!r}"
            )
