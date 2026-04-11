"""ComuneAgent — public administration / municipal services persona.

Persona: Giulia, Municipal Services AI.
Patient, precise, empathetic. Bridges the gap between bureaucratic complexity
and the citizen who just needs to get things done.
"""
from __future__ import annotations

from livekit import rtc
from livekit.agents import RunContext, function_tool

from app.agents.persona import PersonaAgent
from app.tools.comune_tools import (
    book_appointment as _book_appointment,
    check_application_status as _check_application_status,
    lookup_service_requirements as _lookup_service_requirements,
)


class ComuneAgent(PersonaAgent):
    """Giulia — Municipal Services AI for Italian public administration demos."""

    persona_name = "Giulia"
    persona_instructions = (
        "You are Giulia, the Municipal Services AI for EXODIA Voice Intelligence. "
        "Your role is to help citizens navigate Italian municipal bureaucracy clearly "
        "and compassionately — you translate complex administrative requirements into "
        "plain, actionable language that anyone can understand. "
        "You always explain which documents are needed, how long the process takes, "
        "and what the associated fees are, without embellishment or guesswork. "
        "You never invent document requirements, fees, or processing times — you cite "
        "only what the official service catalogue returns from your tools. "
        "When a citizen asks about a service, always use the lookup_service_requirements "
        "tool to retrieve the authoritative document list before answering. "
        "At the end of every service enquiry, offer to book an appointment if the service "
        "supports online booking — phrase this as a natural, helpful suggestion, not a "
        "scripted prompt. "
        "For application status checks, always use check_application_status and relay "
        "the result faithfully, including any notes about required documents or delays. "
        "You are especially attentive to citizens from immigrant communities who may be "
        "unfamiliar with Italian administrative processes — be patient, use simple "
        "language, and never make them feel judged for asking basic questions. "
        "When the user speaks Arabic (Egyptian or Emirati dialect), switch fully to that "
        "dialect and maintain it for the entire conversation. When speaking Italian, use "
        "the formal 'Lei' register. In English, be warm and professional."
    )

    def __init__(self, room: rtc.Room) -> None:
        super().__init__(room=room)

    def _register_tools(self) -> None:
        self.register_tool(self.lookup_service_requirements)
        self.register_tool(self.check_application_status)
        self.register_tool(self.book_appointment)

    @function_tool()
    async def lookup_service_requirements(
        self,
        context: RunContext,
        service_name: str,
    ) -> dict:
        """Look up required documents and details for a municipal service.

        Use this whenever a citizen asks what they need to do or bring for any
        municipal service (residency, permits, certificates, social services, etc.).

        Args:
            service_name: Name or keyword for the service, e.g. "residenza",
                          "carta d'identità", "permesso di costruire".
        """
        result = _lookup_service_requirements(service_name)
        await self._publish_tool_output("lookup_service_requirements", result)
        return result

    @function_tool()
    async def check_application_status(
        self,
        context: RunContext,
        application_id: str,
    ) -> dict:
        """Retrieve the current status of a submitted municipal application.

        Use this when a citizen provides an application ID and wants to know
        whether their request has been approved, rejected, or is still pending.

        Args:
            application_id: The application reference number, e.g. "APP-2024-ANA-00341".
        """
        result = _check_application_status(application_id)
        await self._publish_tool_output("check_application_status", result)
        return result

    @function_tool()
    async def book_appointment(
        self,
        context: RunContext,
        service: str,
        citizen_name: str,
        preferred_date: str,
    ) -> dict:
        """Book an appointment for a municipal service that supports online booking.

        Always call lookup_service_requirements first to confirm the service is
        bookable online before calling this. If it is not bookable online, do not
        call this tool — instead inform the citizen of the walk-in office and hours.

        Args:
            service: The service name or keyword (must match a known service).
            citizen_name: Full name of the citizen making the appointment.
            preferred_date: Requested date in ISO format (YYYY-MM-DD).
        """
        result = _book_appointment(service, citizen_name, preferred_date)
        await self._publish_tool_output("book_appointment", result)
        return result
