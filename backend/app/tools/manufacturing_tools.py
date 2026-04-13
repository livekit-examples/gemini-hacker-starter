"""Tools for the ManufacturingAgent — visual defect detection, SOP lookup,
and defect report generation.

Each function is a plain Python callable registered by the agent via
``self.register_tool(fn)``. The SOP library is loaded once from the JSON
data file on first import.
"""
from __future__ import annotations

import json
import re
from functools import lru_cache
from pathlib import Path

# ---------------------------------------------------------------------------
# Data loading
# ---------------------------------------------------------------------------

_DATA_DIR = Path(__file__).parent.parent / "data"
_SOP_FILE = _DATA_DIR / "manufacturing_sop.json"


@lru_cache(maxsize=1)
def _load_sop() -> list[dict]:
    """Load and cache the SOP entries from JSON."""
    with _SOP_FILE.open(encoding="utf-8") as f:
        return json.load(f)


# ---------------------------------------------------------------------------
# Defect type / severity heuristics
# ---------------------------------------------------------------------------

_DEFECT_KEYWORDS: dict[str, dict] = {
    "crack": {
        "defect_type": "structural_crack",
        "severity": "critical",
        "area": "load-bearing surface",
        "recommended_action": "Remove part from line immediately. Do not rework. Tag with NCR and quarantine.",
    },
    "fracture": {
        "defect_type": "structural_fracture",
        "severity": "critical",
        "area": "structural zone",
        "recommended_action": "Stop production and raise a Non-Conformance Report. Root-cause analysis required before resuming.",
    },
    "delamination": {
        "defect_type": "delamination",
        "severity": "critical",
        "area": "composite or coated surface",
        "recommended_action": "Quarantine affected batch. Investigate adhesion process parameters.",
    },
    "weld": {
        "defect_type": "weld_defect",
        "severity": "major",
        "area": "weld bead",
        "recommended_action": "Mark defect with red chalk, tag with red NCR label, and route to weld rework station.",
    },
    "porosity": {
        "defect_type": "weld_porosity",
        "severity": "major",
        "area": "weld zone",
        "recommended_action": "Grind out porosity and re-weld. Re-inspect per SOP-MFG-003 before release.",
    },
    "burr": {
        "defect_type": "burr_or_sharp_edge",
        "severity": "minor",
        "area": "machined edge or drilled hole",
        "recommended_action": "Deburr with hand tool and re-inspect surface finish. Log on In-Process Inspection Record.",
    },
    "scratch": {
        "defect_type": "surface_scratch",
        "severity": "minor",
        "area": "exterior surface",
        "recommended_action": "Assess scratch depth. If < 0.1 mm, polish and re-inspect. If deeper, escalate to Quality Engineer.",
    },
    "dent": {
        "defect_type": "dent_or_impact_mark",
        "severity": "minor",
        "area": "sheet metal panel",
        "recommended_action": "Measure dent depth. Dents > 1 mm in Class A surfaces require rework per SOP-MFG-019.",
    },
    "corrosion": {
        "defect_type": "corrosion",
        "severity": "major",
        "area": "metal surface",
        "recommended_action": "Quarantine corroded parts. Investigate storage conditions and protective coating effectiveness.",
    },
    "rust": {
        "defect_type": "corrosion",
        "severity": "major",
        "area": "metal surface",
        "recommended_action": "Quarantine corroded parts. Review storage and coating specifications.",
    },
    "misalignment": {
        "defect_type": "dimensional_misalignment",
        "severity": "major",
        "area": "assembly joint",
        "recommended_action": "Measure deviation with CMM. Any out-of-tolerance critical dimension stops further assembly.",
    },
    "flash": {
        "defect_type": "moulding_flash",
        "severity": "minor",
        "area": "parting line",
        "recommended_action": "Remove flash manually with a trimming knife. Inspect per SOP-MFG-009 criteria.",
    },
    "sink": {
        "defect_type": "sink_mark",
        "severity": "major",
        "area": "injection-moulded surface",
        "recommended_action": "Reject part. Investigate mould tool packing pressure and cooling time.",
    },
    "burn": {
        "defect_type": "burn_mark",
        "severity": "major",
        "area": "injection-moulded gate area",
        "recommended_action": "Reject part. Check mould venting and material moisture content.",
    },
    "cold joint": {
        "defect_type": "cold_solder_joint",
        "severity": "major",
        "area": "PCB solder pad",
        "recommended_action": "Rework joint with fresh solder. Re-inspect per SOP-MFG-015 after rework.",
    },
    "bridge": {
        "defect_type": "solder_bridge",
        "severity": "critical",
        "area": "PCB adjacent pads",
        "recommended_action": "Reject immediately. Rework to remove bridge with solder wick, re-inspect before re-test.",
    },
    "paint": {
        "defect_type": "paint_defect",
        "severity": "minor",
        "area": "painted exterior surface",
        "recommended_action": "Assess defect type and location. Spot repair per SOP-MFG-019 if Class A surface affected.",
    },
    "run": {
        "defect_type": "paint_run_or_sag",
        "severity": "minor",
        "area": "painted surface",
        "recommended_action": "Sand and re-coat affected area per SOP-MFG-019 spot-repair procedure.",
    },
}

_DEFAULT_DEFECT = {
    "defect_type": "unclassified_defect",
    "severity": "minor",
    "area": "general component surface",
    "recommended_action": "Document defect with photograph and raise with the Quality Engineer for classification.",
}

_SEVERITY_ORDER = {"critical": 3, "major": 2, "minor": 1}


# ---------------------------------------------------------------------------
# Tool: detect_visual_defect
# ---------------------------------------------------------------------------


def detect_visual_defect(description: str) -> dict:
    """Analyse a text description of a visual defect and classify it.

    Uses keyword matching against the defect taxonomy to infer the defect
    type, severity, affected area, and recommended corrective action.

    Args:
        description: Free-text description of the observed defect, e.g.
                     "hairline crack visible on the left load-bearing bracket".

    Returns::

        {
            "defect_type":        str,
            "severity":           "critical" | "major" | "minor",
            "area":               str,
            "recommended_action": str,
        }
    """
    lower = description.lower()

    # Find all matching keywords and pick the most severe match.
    matches = [
        data
        for keyword, data in _DEFECT_KEYWORDS.items()
        if keyword in lower
    ]

    if not matches:
        return dict(_DEFAULT_DEFECT)

    # Return the highest-severity match to surface the most critical issue first.
    best = max(matches, key=lambda d: _SEVERITY_ORDER.get(d["severity"], 0))
    return dict(best)


# ---------------------------------------------------------------------------
# Tool: generate_defect_report
# ---------------------------------------------------------------------------


def generate_defect_report(defects: list[dict]) -> str:
    """Generate a formatted defect report from a list of detected defect dicts.

    The report is published by the agent to the LiveKit ``tool-output`` topic
    so the frontend ManufacturingPanel can display it as a structured card.

    Args:
        defects: List of dicts with at least ``defect_type``, ``severity``,
                 ``area``, and ``recommended_action`` keys.

    Returns:
        A multi-line formatted report string, or a note if the list is empty.
    """
    if not defects:
        return "No defects provided. Report not generated."

    lines = ["DEFECT REPORT", "=" * 40]
    for idx, defect in enumerate(defects, start=1):
        severity = defect.get("severity", "unknown").upper()
        defect_type = defect.get("defect_type", "unclassified")
        area = defect.get("area", "N/A")
        action = defect.get("recommended_action", "Review with Quality Engineer.")
        lines.append(f"\nDefect #{idx}  [{severity}]")
        lines.append(f"  Type  : {defect_type}")
        lines.append(f"  Area  : {area}")
        lines.append(f"  Action: {action}")

    lines.append("\n" + "=" * 40)
    lines.append(f"Total defects: {len(defects)}")
    critical_count = sum(1 for d in defects if d.get("severity") == "critical")
    if critical_count:
        lines.append(f"CRITICAL DEFECTS FOUND: {critical_count} — production stop recommended.")

    report = "\n".join(lines)
    return report


# ---------------------------------------------------------------------------
# Tool: lookup_sop
# ---------------------------------------------------------------------------


def lookup_sop(keyword: str) -> dict:
    """Search the SOP library for a procedure matching the given keyword.

    Performs case-insensitive partial matching against procedure titles,
    keyword tags, and step text. Returns the best-matching entry or
    indicates that no match was found.

    Args:
        keyword: Search term, e.g. "torque", "loto", "weld inspection".

    Returns::

        {
            "procedure_id": str,
            "title":        str,
            "steps":        list[str],
            "found":        bool,
        }
    """
    sops = _load_sop()
    lower_kw = keyword.strip().lower()
    kw_tokens = set(re.split(r"[\s/,-]+", lower_kw))

    best_match: dict | None = None
    best_score = 0

    for sop in sops:
        score = 0
        title_lower = sop["title"].lower()

        # Direct keyword list match (strongest signal)
        if any(lower_kw in k.lower() for k in sop.get("keywords", [])):
            score += 10
        if any(kw_token in k.lower() for k in sop.get("keywords", []) for kw_token in kw_tokens):
            score += 5

        # Title partial match
        if lower_kw in title_lower:
            score += 8
        if any(t in title_lower for t in kw_tokens if len(t) > 2):
            score += 3

        # Procedure ID match
        if lower_kw in sop["procedure_id"].lower():
            score += 12

        # Step text match (weak signal)
        for step in sop.get("steps", []):
            if lower_kw in step.lower():
                score += 1
                break

        if score > best_score:
            best_score = score
            best_match = sop

    if best_match is None or best_score < 3:
        return {"procedure_id": "", "title": "", "steps": [], "found": False}

    return {
        "procedure_id": best_match["procedure_id"],
        "title": best_match["title"],
        "steps": best_match["steps"],
        "found": True,
    }
