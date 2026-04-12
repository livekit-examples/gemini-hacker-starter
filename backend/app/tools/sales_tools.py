"""Tools for the SalesAgent — sales strategy and proposal generation.

Each function is a plain Python callable that the agent registers via
``self.register_tool(fn)``.  They operate on the text/context the agent
receives (screen descriptions, notes, section requests) and return typed
dicts or strings that the frontend SalesPanel can render.
"""
from __future__ import annotations

import re

# ---------------------------------------------------------------------------
# Priority-keyword tables
# ---------------------------------------------------------------------------

_HIGH_PRIORITY_KEYWORDS = {
    "urgent",
    "closing",
    "decision",
    "budget approved",
    "final stage",
    "procurement",
    "contract",
    "competitive",
    "competitor",
    "churn",
    "at risk",
    "loss",
    "deadline",
    "executive",
    "c-suite",
    "ceo",
    "cfo",
    "cto",
    "vp",
    "board",
    "renewal",
    "expiring",
    "escalation",
    "escalated",
    "priority",
}

_LOW_PRIORITY_KEYWORDS = {
    "early stage",
    "discovery",
    "research",
    "exploratory",
    "prospect",
    "lead",
    "unqualified",
    "cold",
    "long-term",
    "backlog",
    "parked",
    "on hold",
    "waiting",
}

# ---------------------------------------------------------------------------
# Proposal section templates
# ---------------------------------------------------------------------------

_SECTION_TEMPLATES: dict[str, str] = {
    "executive_summary": (
        "This proposal outlines how {context} can accelerate growth and operational "
        "efficiency through a targeted partnership. Our solution has delivered "
        "measurable results for similar organisations, and we are confident it will "
        "do the same for your team."
    ),
    "problem_statement": (
        "Organisations like {context} frequently face challenges around manual "
        "processes, fragmented data, and slow decision cycles. These pain points "
        "translate directly into lost revenue and competitive disadvantage — "
        "challenges our platform is purpose-built to solve."
    ),
    "solution_overview": (
        "Our platform provides {context} with a unified, AI-powered layer that "
        "streamlines workflows, surfaces actionable insights in real time, and "
        "integrates seamlessly with your existing technology stack — with zero "
        "rip-and-replace risk."
    ),
    "value_proposition": (
        "By partnering with us, {context} can expect a 25–40 % reduction in manual "
        "handling time, faster deal cycles, and improved forecast accuracy — backed "
        "by a transparent ROI model tailored to your specific KPIs."
    ),
    "pricing": (
        "We offer flexible commercial models for {context}, including outcome-based "
        "pricing and enterprise licences. A detailed quote will be scoped to your "
        "volume and usage requirements following a brief discovery call."
    ),
    "next_steps": (
        "To move forward, we recommend a 30-minute technical alignment session with "
        "{context}'s operations and IT leads, followed by a pilot scoped to one "
        "business unit. We can have an agreement in place within two weeks."
    ),
}


# ---------------------------------------------------------------------------
# Tool functions
# ---------------------------------------------------------------------------


def analyze_screen_content(summary: str) -> dict:
    """Analyse a plain-text description of screen content and return sales insights.

    Classifies the situation by priority, identifies relevant findings, and
    recommends concrete next steps the rep can take immediately.

    Args:
        summary: Free-text description of what is visible on screen,
                 e.g. "CRM showing 3 open opportunities — one at proposal stage,
                 two in discovery. Competitor mentioned in notes for Acme deal."

    Returns::

        {
            "findings": list[str],
            "recommendations": list[str],
            "priority": "high" | "medium" | "low",
        }
    """
    summary_lower = summary.lower()

    # Determine priority — use word-boundary matching so multi-word phrases
    # like "board" don't match inside "dashboard".
    def _word_match(keyword: str, text: str) -> bool:
        escaped = re.escape(keyword)
        return bool(re.search(r'\b' + escaped + r'\b', text))

    if any(_word_match(kw, summary_lower) for kw in _HIGH_PRIORITY_KEYWORDS):
        priority = "high"
    elif any(_word_match(kw, summary_lower) for kw in _LOW_PRIORITY_KEYWORDS):
        priority = "low"
    else:
        priority = "medium"

    # Extract findings from summary keywords
    findings: list[str] = []
    if "opportunity" in summary_lower or "opportunit" in summary_lower:
        findings.append("Active sales opportunities detected in the pipeline.")
    if "competitor" in summary_lower or "competitive" in summary_lower:
        findings.append("Competitor presence noted — differentiation messaging required.")
    if "proposal" in summary_lower:
        findings.append("Deal is at proposal stage — pricing and ROI are top of mind.")
    if "discovery" in summary_lower:
        findings.append("Discovery-stage deals present — focus on pain identification.")
    if "contract" in summary_lower or "procurement" in summary_lower:
        findings.append("Contract or procurement phase detected — legal and compliance likely involved.")
    if "renewal" in summary_lower or "expiring" in summary_lower:
        findings.append("Renewal risk identified — act before competitor can enter.")
    if "budget" in summary_lower:
        findings.append("Budget signals visible — confirm approval authority and timeline.")
    if "executive" in summary_lower or any(t in summary_lower for t in ("ceo", "cfo", "cto", "vp")):
        findings.append("Executive-level stakeholder detected — tailor messaging to strategic outcomes.")
    if not findings:
        findings.append("Screen content noted — no specific opportunity signals flagged.")

    # Build recommendations based on priority and findings
    recommendations: list[str] = []
    if priority == "high":
        recommendations.append("Escalate engagement — reach out to the economic buyer directly.")
        recommendations.append("Prepare a one-page executive summary focusing on ROI and risk reduction.")
    if "Competitor" in " ".join(findings):
        recommendations.append("Lead with a competitive battle card — highlight three unique differentiators.")
    if "proposal" in summary_lower:
        recommendations.append("Follow up on the proposal within 24 hours to address open questions.")
    if "discovery" in summary_lower:
        recommendations.append("Run a structured discovery call to confirm budget, authority, need, and timeline.")
    if priority == "low":
        recommendations.append("Nurture through content and light-touch follow-ups until intent signals emerge.")
    if not recommendations:
        recommendations.append("Continue relationship-building and surface deeper pain points in the next call.")
        recommendations.append("Log key insights in CRM and schedule a follow-up touch point.")

    return {
        "findings": findings,
        "recommendations": recommendations,
        "priority": priority,
    }


def generate_proposal_section(section: str, context: str) -> str:
    """Generate a tailored proposal section for a given business context.

    Args:
        section: The section to generate. Supported values:
                 ``executive_summary``, ``problem_statement``,
                 ``solution_overview``, ``value_proposition``,
                 ``pricing``, ``next_steps``.
                 Spaces are normalised to underscores automatically.
        context: Brief description of the prospect, e.g.
                 "SMB logistics company based in Milan with 120 employees".

    Returns:
        A non-empty string of proposal copy for the requested section.
    """
    # Normalise section key
    key = section.strip().lower().replace(" ", "_").replace("-", "_")
    template = _SECTION_TEMPLATES.get(key)

    if template:
        return template.format(context=context.strip() or "your organisation")

    # Graceful fallback for unknown sections
    return (
        f"[{section.replace('_', ' ').title()}] "
        f"This section will be customised for {context.strip() or 'your organisation'} "
        "following the discovery process. Please reach out to your account executive "
        "for a tailored draft."
    )


def log_talking_points(points: list[str]) -> str:
    """Format and publish a structured list of talking points.

    In a live agent context the agent wrapper publishes the payload to the
    LiveKit ``tool-output`` data topic so the SalesPanel can render it.
    This function returns a confirmation string and is kept side-effect-free
    so it is easily unit-testable.

    Args:
        points: Ordered list of talking points for the current conversation.

    Returns:
        A confirmation string indicating the payload was published.
    """
    if not points:
        return "No talking points provided — nothing published."

    formatted = "\n".join(f"{i + 1}. {pt.strip()}" for i, pt in enumerate(points))
    return f"Talking points published ({len(points)} items):\n{formatted}"
