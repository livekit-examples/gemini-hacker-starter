"""SalesAgent — sales strategy and proposal generation persona.

Persona: Aria, Senior Sales Strategist.
Confident, direct, commercially sharp. Helps sales reps close more deals by
analysing prospect screens, generating tailored proposal copy, and surfacing
contextual talking points in real time.
"""
from __future__ import annotations

from livekit import rtc
from livekit.agents import RunContext, function_tool

from app.agents.persona import PersonaAgent
from app.tools.sales_tools import (
    analyze_screen_content as _analyze_screen_content,
    generate_proposal_section as _generate_proposal_section,
    log_talking_points as _log_talking_points,
)


class SalesAgent(PersonaAgent):
    """Aria — Senior Sales Strategist for EXODIA Voice Intelligence demos."""

    persona_name = "Aria"
    persona_instructions = (
        "You are Aria, a Senior Sales Strategist embedded in EXODIA Voice Intelligence. "
        "Your role is to help sales professionals close more deals — faster, smarter, "
        "and with greater confidence. You think in terms of pipeline stages, stakeholder "
        "dynamics, competitive positioning, and economic outcomes. "
        "When a rep shares their screen or describes what they see, immediately analyse "
        "the context and surface the three most relevant insights: what is happening, "
        "what the risk or opportunity is, and what the rep should do next. "
        "You speak directly and commercially — avoid vague encouragement. "
        "Use the analyze_screen_content tool whenever the rep describes or shares "
        "anything visible on screen, such as a CRM record, email thread, or proposal draft. "
        "When asked to help with written copy, use generate_proposal_section with the "
        "specific section name and the prospect context the rep provides. "
        "Use log_talking_points to record and display a prioritised list of talking points "
        "whenever you identify key messages the rep should communicate in the meeting. "
        "Push back gently but firmly when a rep is about to give a discount without "
        "confirming budget authority or deal stage — protect margin. "
        "Always end your analysis with a clear, single recommended action the rep should "
        "take in the next five minutes."
    )

    def __init__(self, room: rtc.Room) -> None:
        super().__init__(room=room)

    def _register_tools(self) -> None:
        self.register_tool(self.analyze_screen_content)
        self.register_tool(self.generate_proposal_section)
        self.register_tool(self.log_talking_points)

    @function_tool()
    async def analyze_screen_content(
        self,
        context: RunContext,
        summary: str,
    ) -> dict:
        """Analyse a plain-text description of what is currently on screen.

        Use this whenever the sales rep describes or shares what they can see —
        a CRM dashboard, email, proposal, or any other sales artefact.

        Args:
            summary: Free-text description of the screen content, e.g.
                     "CRM showing 3 open opportunities — one at proposal stage,
                     competitor mentioned in the Acme deal notes."
        """
        result = _analyze_screen_content(summary)
        await self._publish_tool_output("talking_points", result)
        return result

    @function_tool()
    async def generate_proposal_section(
        self,
        context: RunContext,
        section: str,
        prospect_context: str,
    ) -> str:
        """Generate tailored proposal copy for a specific section.

        Args:
            section: The section to generate. Supported: ``executive_summary``,
                     ``problem_statement``, ``solution_overview``,
                     ``value_proposition``, ``pricing``, ``next_steps``.
            prospect_context: Brief description of the prospect, e.g.
                              "SMB logistics company based in Milan, 120 employees,
                              struggling with manual shipment tracking."
        """
        result = _generate_proposal_section(section, prospect_context)
        await self._publish_tool_output(
            "proposal_section",
            {"section": section, "content": result, "context": prospect_context},
        )
        return result

    @function_tool()
    async def log_talking_points(
        self,
        context: RunContext,
        points: list[str],
    ) -> str:
        """Log and display a prioritised list of talking points for the current meeting.

        Args:
            points: Ordered list of talking points, e.g.
                    ["Lead with ROI story", "Address security objection early",
                     "Confirm Q4 budget cycle closes Nov 30"].
        """
        result = _log_talking_points(points)
        await self._publish_tool_output(
            "talking_points",
            {"points": points, "count": len(points)},
        )
        return result
