"""LogisticsAgent — shipment tracking and carrier performance persona.

Persona: Elena, Head of Logistics Operations.
Sharp, fast, operationally focused. Tracks shipments, flags delays, and
briefs carrier performance with the precision of someone who has managed
complex supply chains across multiple continents.
"""

from __future__ import annotations

from livekit import rtc
from livekit.agents import RunContext, function_tool

from app.agents.persona import PersonaAgent
from app.tools.logistics_tools import (
    lookup_shipment as _lookup_shipment,
    flag_delay as _flag_delay,
    generate_carrier_brief as _generate_carrier_brief,
)


class LogisticsAgent(PersonaAgent):
    """Elena — Head of Logistics Operations for EXODIA Voice Intelligence logistics demos."""

    persona_name = "Elena"
    persona_instructions = (
        "You are Elena, Head of Logistics Operations at EXODIA Voice Intelligence. "
        "You are sharp, fast, and operationally focused — you cut through ambiguity "
        "immediately and give the team the clarity they need to keep freight moving. "
        "When the user provides a tracking ID, call lookup_shipment without delay "
        "and read back the key facts — status, carrier, ETA, and any delay — in "
        "a single, structured brief; never ask the user to check the system themselves "
        "when you can pull the data directly. "
        "When a shipment has a delay or a hold, proactively assess the impact and "
        "ask whether you should flag it using flag_delay — do not wait for the user "
        "to request the flag; your job is to stay ahead of disruptions, not react to them. "
        "When asked about a carrier's performance, call generate_carrier_brief and "
        "provide a direct operational assessment: on-time rate, open incidents, and "
        "a clear recommendation — do not soften bad news about underperforming carriers. "
        "If a shipment is in customs hold, flag the relevant documentation gap immediately "
        "and suggest the fastest resolution path based on the destination country's known "
        "import procedures. "
        "Keep your communication dense and precise — this is an operations environment, "
        "not a customer-service chat; bullet points and short declarative sentences are "
        "preferred over flowing prose. "
        "Always confirm the next action at the end of each turn: escalate, flag, re-route, "
        "or monitor — never leave a briefing without a clear next step."
    )

    def __init__(self, room: rtc.Room) -> None:
        super().__init__(room=room)

    def _register_tools(self) -> None:
        self.register_tool(self.lookup_shipment)
        self.register_tool(self.flag_delay)
        self.register_tool(self.generate_carrier_brief)

    @function_tool()
    async def lookup_shipment(
        self,
        context: RunContext,
        tracking_id: str,
    ) -> dict:
        """Look up a shipment by its tracking ID and return full status details.

        Call this whenever the user mentions a tracking ID or asks for a shipment
        status update. Read back origin, destination, carrier, ETA, and delay
        information in a structured brief.

        Args:
            tracking_id: Shipment tracking identifier, e.g. ``"SHP-20240312-AUH"``.
        """
        result = _lookup_shipment(tracking_id)
        await self._publish_tool_output("shipment_lookup", result)
        await self._speak_tool_followup(context, "shipment_lookup", result)
        return result

    @function_tool()
    async def flag_delay(
        self,
        context: RunContext,
        tracking_id: str,
        reason: str,
    ) -> str:
        """Flag a shipment as delayed and notify the operations team.

        Call this when a delay has been identified and needs to be escalated
        in the operations workflow. Publishes a delay-flag card to the
        dashboard panel.

        Args:
            tracking_id: Shipment tracking identifier to flag.
            reason: Clear explanation of the delay cause, e.g.
                    ``"Customs hold at Abu Dhabi — certificate of origin under review"``.
        """
        confirmation = _flag_delay(tracking_id, reason)
        await self._publish_tool_output(
            "delay_flag",
            {
                "tracking_id": tracking_id,
                "reason": reason,
                "confirmation": confirmation,
            },
        )
        await self._speak_tool_followup(
            context,
            "delay_flag",
            {
                "tracking_id": tracking_id,
                "reason": reason,
                "confirmation": confirmation,
            },
        )
        return confirmation

    @function_tool()
    async def generate_carrier_brief(
        self,
        context: RunContext,
        carrier_name: str,
    ) -> dict:
        """Generate a performance brief for a named logistics carrier.

        Call this when the user asks about a carrier's reliability, performance
        metrics, or wants a recommendation. Returns on-time rate, average delay,
        open incidents, and a direct operational recommendation.

        Args:
            carrier_name: Carrier name or partial name, e.g. ``"Emirates"``,
                          ``"DHL"``, ``"FedEx"``, ``"Agility"``.
        """
        result = _generate_carrier_brief(carrier_name)
        await self._publish_tool_output("carrier_brief", result)
        await self._speak_tool_followup(context, "carrier_brief", result)
        return result
