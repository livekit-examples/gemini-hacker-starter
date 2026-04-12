"""Tools for the SalesAgent — sales strategy and screen analysis.

Each function is a plain Python callable that the agent registers via
``self.register_tool(fn)``. They perform deterministic analysis based on
the provided text so the frontend panel can render structured cards.
"""
from __future__ import annotations

import re

# ---------------------------------------------------------------------------
# Heuristic helpers
# ---------------------------------------------------------------------------

_HIGH_PRIORITY_SIGNALS = {
    "urgent", "critical", "deadline", "close", "decision", "budget",
    "contract", "sign", "deal", "opportunity", "q4", "quarter",
    "renewal", "expir", "compet",
}
_LOW_PRIORITY_SIGNALS = {
    "info", "general", "overview", "intro", "awareness", "background",
    "explore", "curious",
}

_PROPOSAL_TEMPLATES: dict[str, str] = {
    "executive_summary": (
        "This proposal outlines a tailored solution for {context}, designed to "
        "deliver measurable ROI within the first quarter of deployment. "
        "Our approach combines proven methodology with hands-on support, ensuring "
        "a smooth onboarding and rapid time-to-value."
    ),
    "problem_statement": (
        "Organisations in the {context} space face mounting pressure from "
        "escalating operational costs and fragmented tooling. "
        "Without a unified solution, teams lose significant hours to manual "
        "reconciliation — time that could be directed toward revenue-generating activities."
    ),
    "solution_overview": (
        "Our platform addresses the core challenges of {context} by integrating "
        "real-time data intelligence with automated workflow execution. "
        "Deployable in under two weeks, it replaces legacy spreadsheet-driven "
        "processes with a single, auditable source of truth."
    ),
    "value_proposition": (
        "Clients in the {context} sector report an average 34% reduction in "
        "administrative overhead within 90 days of go-live. "
        "The platform pays for itself in operational savings alone — "
        "with strategic upsell and cross-sell potential captured on top."
    ),
    "pricing": (
        "Pricing for {context} engagements is structured as a transparent monthly "
        "subscription with no hidden implementation fees. "
        "Volume discounts apply above 50 seats, and multi-year terms unlock "
        "an additional 15% saving over the list rate."
    ),
    "next_steps": (
        "To move forward with {context}, we recommend scheduling a 30-minute "
        "technical discovery call this week. "
        "Our team will prepare a tailored environment for a live demonstration "
        "aligned to your specific use-case and stakeholder priorities."
    ),
}

_DEFAULT_TEMPLATE = (
    "Regarding {context}: our team has deep expertise in this area and can "
    "provide a customised approach that aligns with your strategic objectives. "
    "We look forward to exploring the specifics with you in detail."
)


# ---------------------------------------------------------------------------
# Tool functions
# ---------------------------------------------------------------------------


def analyze_screen_content(summary: str) -> dict:
    """Analyse a textual summary of screen content and return sales insights.

    Performs keyword-based analysis to surface relevant findings and
    actionable recommendations for the sales representative.

    Args:
        summary: A plain-text description of what is currently visible on
                 the screen, e.g. "CRM showing 3 open opportunities worth $120k".

    Returns::

        {
            "findings":        list[str],
            "recommendations": list[str],
            "priority":        "high" | "medium" | "low",
        }
    """
    lower = summary.lower()
    tokens = set(re.split(r"[\s,./;:!?()-]+", lower))

    # Determine priority via signal intersection.
    if tokens & _HIGH_PRIORITY_SIGNALS:
        priority: str = "high"
    elif tokens & _LOW_PRIORITY_SIGNALS:
        priority = "low"
    else:
        priority = "medium"

    # Build findings.
    findings: list[str] = []

    if any(kw in lower for kw in ("crm", "pipeline", "opportunity", "opportunit")):
        findings.append("Active CRM pipeline data is visible — review open opportunity stages.")
    if any(kw in lower for kw in ("email", "inbox", "message")):
        findings.append("Unread communications detected — check for pending prospect replies.")
    if any(kw in lower for kw in ("proposal", "quote", "contract", "pricing")):
        findings.append("A proposal or contract document is open — confirm all figures are current.")
    if any(kw in lower for kw in ("competitor", "compet", "alternative")):
        findings.append("Competitive context present — prepare differentiation talking points.")
    if any(kw in lower for kw in ("meeting", "call", "demo", "presentation")):
        findings.append("Meeting or demo context identified — confirm agenda and attendee roles.")
    if not findings:
        findings.append("Screen content noted — no specific sales signals detected in the summary.")

    # Build recommendations.
    recommendations: list[str] = []

    if priority == "high":
        recommendations.append("Prioritise this account immediately — high-value signals present.")
        recommendations.append("Prepare a closing argument and address any outstanding objections.")
    elif priority == "medium":
        recommendations.append("Follow up within 24 hours to maintain deal momentum.")
        recommendations.append("Send a brief recap email after the call to reinforce key points.")
    else:
        recommendations.append("Log this interaction in your CRM and set a nurture cadence.")
        recommendations.append("Share relevant case studies to build awareness and interest.")

    return {
        "findings": findings,
        "recommendations": recommendations,
        "priority": priority,
    }


def generate_proposal_section(section: str, context: str) -> str:
    """Generate a proposal section tailored to the given context.

    Produces polished, professional copy for a named proposal section.
    The section name is normalised (lowercased, spaces → underscores) before
    matching against the built-in template library.

    Args:
        section: Proposal section name, e.g. "executive_summary",
                 "value_proposition", "next_steps", "pricing".
        context: Free-text description of the prospect / deal, e.g.
                 "SMB logistics company with 80 drivers".

    Returns:
        A multi-sentence string of proposal copy ready for use or editing.
    """
    normalised = section.strip().lower().replace(" ", "_")
    template = _PROPOSAL_TEMPLATES.get(normalised, _DEFAULT_TEMPLATE)
    # Trim context to a reasonable length for inline use.
    trimmed_context = context.strip()[:120] if context else "your organisation"
    return template.format(context=trimmed_context)


def log_talking_points(points: list[str]) -> str:
    """Format a list of talking points for display and return a confirmation.

    In the live agent context the containing agent method publishes this
    output to the LiveKit ``tool-output`` data topic so the frontend
    ``SalesPanel`` can render it as a prioritised bullet list.

    Args:
        points: Ordered list of talking-point strings, e.g.
                ["Build rapport", "Ask about Q4 targets", "Present ROI slide"].

    Returns:
        A short confirmation string confirming the points were sent.
    """
    if not points:
        return "No talking points provided — nothing sent."
    formatted = "; ".join(f"{i + 1}. {p.strip()}" for i, p in enumerate(points))
    return f"Talking points published to output panel: {formatted}"
