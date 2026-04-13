"""Agent registry — maps industry slug → agent class.

Usage::

    from app.agents.registry import get_agent

    agent = get_agent("comune", room)   # returns ComuneAgent instance
    agent = get_agent("unknown", room)  # returns DefaultAgent instance

New industry agents are added by subclassing PersonaAgent and adding a
single entry to REGISTRY — nothing else changes.
"""
from __future__ import annotations

import logging

from livekit import rtc

from app.agents.persona import PersonaAgent

logger = logging.getLogger(__name__)


class DefaultAgent(PersonaAgent):
    """Placeholder agent for industries that haven't been implemented yet.

    Returns a friendly "coming soon" response so the demo platform never
    shows a broken page.
    """

    persona_name = "EXODIA AI"
    persona_instructions = (
        "You are EXODIA Voice Intelligence, a multimodal AI assistant. "
        "Greet the user warmly and let them know that this particular demo is coming soon. "
        "Offer to answer general questions about the EXODIA platform while they wait."
    )


def _build_registry() -> dict[str, type[PersonaAgent]]:
    """Build the initial registry with all known agents.

    Heavy imports are deferred here so circular-import issues cannot arise
    when individual agent modules import from registry.
    """
    from app.agents.hackathon import HackathonAgent
    from app.agents.comune import ComuneAgent
    from app.agents.sales import SalesAgent
    from app.agents.manufacturing import ManufacturingAgent

    return {
        "hackathon": HackathonAgent,
        "comune": ComuneAgent,
        "sales": SalesAgent,
        "manufacturing": ManufacturingAgent,
        # Industry agents — implemented in later sessions:
        "logistics": DefaultAgent,
        "real_estate": DefaultAgent,
        "dental": DefaultAgent,
    }


REGISTRY: dict[str, type[PersonaAgent]] = _build_registry()


def get_agent(industry: str, room: rtc.Room) -> PersonaAgent:
    """Return an instantiated agent for the given industry slug.

    Falls back to DefaultAgent for unknown slugs — never raises.
    """
    agent_class = REGISTRY.get(industry, DefaultAgent)
    if agent_class is DefaultAgent and industry not in REGISTRY:
        logger.warning(
            "Unknown industry slug '%s' — falling back to DefaultAgent.", industry
        )
    return agent_class(room=room)
