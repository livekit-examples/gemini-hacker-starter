"""SalesAgent — sales strategy and screen analysis persona.

Persona: Aria, Senior Sales Strategist.
Confident, direct, commercially sharp. Helps sales professionals close
deals faster by analysing screen content, generating proposal copy, and
surfacing the right talking points at the right moment.
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
    """Aria — Senior Sales Strategist for EXODIA Voice Intelligence sales demos."""

    persona_name = "Aria"
    persona_instructions = (
        "You are Aria, a Senior Sales Strategist at EXODIA Voice Intelligence. "
        "You are confident, commercially sharp, and always speak with purpose — "
        "every sentence you deliver should either move the deal forward or build "
        "genuine rapport that earns the right to do so. "
        "When the user shares their screen or describes what they are looking at, "
        "immediately use analyze_screen_content to surface the key findings and "
        "recommend the highest-impact next action for the sales conversation. "
        "When asked to draft or improve proposal language, use generate_proposal_section "
        "to produce polished, client-ready copy — never leave the user with rough notes "
        "when professional prose is within reach. "
        "When the conversation surfaces key points the rep should raise, call "
        "log_talking_points to publish them to the output panel so the rep can "
        "reference them at a glance without losing eye contact with the prospect. "
        "Push back respectfully when a rep is about to discount prematurely or "
        "skip qualification — your job is to protect margin and pipeline quality, "
        "not just validate whatever the user suggests. "
        "Keep your tone direct and peer-to-peer; avoid corporate filler phrases "
        "like 'certainly' or 'absolutely' — respond as a trusted colleague would. "
        "When the context indicates high priority or an imminent close, increase "
        "urgency appropriately and help the rep prepare for objection handling. "
        "Always end a screen-analysis turn by asking what the rep wants to tackle next."
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
        """Analyse visible screen content and return sales-relevant findings.

        Call this whenever the user describes or shares their screen so you can
        surface findings, recommendations, and a priority assessment for the
        current sales situation.

        Args:
            summary: Plain-text description of the screen content, e.g.
                     "CRM showing 3 open opportunities worth $120k, one near close".
        """
        result = _analyze_screen_content(summary)
        await self._publish_tool_output("screen_analysis", result)
        await self._speak_tool_followup(context, "screen_analysis", result)
        return result

    @function_tool()
    async def generate_proposal_section(
        self,
        context: RunContext,
        section: str,
        prospect_context: str,
    ) -> str:
        """Generate a polished proposal section tailored to the prospect.

        Use this when the user asks you to write or improve any section of a
        sales proposal — executive summary, value proposition, pricing, next steps, etc.

        Args:
            section: The proposal section to generate, e.g. "executive_summary",
                     "value_proposition", "next_steps", "pricing".
            prospect_context: Brief description of the prospect and deal, e.g.
                              "SMB logistics company with 80 drivers in the UAE".
        """
        text = _generate_proposal_section(section, prospect_context)
        await self._publish_tool_output(
            "proposal_section",
            {"section": section, "context": prospect_context, "content": text},
        )
        await self._speak_tool_followup(
            context,
            "proposal_section",
            {"section": section, "context": prospect_context, "content": text},
        )
        return text

    @function_tool()
    async def log_talking_points(
        self,
        context: RunContext,
        points: list[str],
    ) -> str:
        """Log and display a prioritised list of talking points for the rep.

        Call this to push a formatted list of talking points to the sales
        dashboard panel so the rep can reference them during the conversation
        without breaking eye contact with the prospect.

        Args:
            points: Ordered list of talking points, e.g.
                    ["Establish budget range", "Ask about Q4 targets", "Present ROI slide"].
        """
        confirmation = _log_talking_points(points)
        await self._publish_tool_output(
            "talking_points",
            {"points": points, "confirmation": confirmation},
        )
        await self._speak_tool_followup(
            context,
            "talking_points",
            {"points": points, "confirmation": confirmation},
        )
        return confirmation
