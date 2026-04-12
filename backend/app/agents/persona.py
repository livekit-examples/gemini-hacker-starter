"""PersonaAgent — adds language, persona, and tool registry to BaseAgent.

Subclasses set `persona_name` and `persona_instructions` as instance
attributes *before* calling ``super().__init__(room)`` so that
``build_system_prompt()`` picks them up during construction.
"""

from __future__ import annotations

import asyncio
import json
import logging
from typing import Any

from livekit import rtc
from livekit.agents import RunContext

from app.agents.base import BaseAgent
from app.config import settings
from app.languages.detector import detect_language
from app.languages.profiles import LanguageProfile

logger = logging.getLogger(__name__)

TOOL_FOLLOW_UP_RULE = (
    "Tool-use speaking rule: after every tool call, immediately deliver a spoken "
    "response to the user that summarizes the result and gives a clear next step or "
    "question. Never end a turn silently after using a tool."
)


class PersonaAgent(BaseAgent):
    """Extends BaseAgent with persona identity, tool registry, and language support.

    Subclass pattern::

        class MySalesAgent(PersonaAgent):
            def __init__(self, room):
                self.persona_name = "Aria"
                self.persona_instructions = "You are a senior sales strategist..."
                super().__init__(room)

            def _register_tools(self):
                self.register_tool(self.analyze_screen_content)
    """

    # Class-level defaults — subclasses override via instance attrs in __init__.
    persona_name: str = ""
    persona_instructions: str = ""
    language_profile: LanguageProfile | None = None

    def __init__(self, room: rtc.Room) -> None:
        self._tool_registry: list = []
        self.language_profile = detect_language(None, settings.default_language)
        instructions = self.build_system_prompt()
        self._system_prompt = instructions
        super().__init__(room=room, instructions=instructions)
        self._register_tools()

    # ------------------------------------------------------------------
    # Subclass hooks
    # ------------------------------------------------------------------

    def _register_tools(self) -> None:
        """Override in subclasses to call self.register_tool() for each tool."""

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def register_tool(self, fn: Any) -> None:
        """Add *fn* to the tool registry list."""
        self._tool_registry.append(fn)

    def build_system_prompt(self) -> str:
        """Build the full system prompt from BASE_VIDEO_AWARENESS + persona + language."""
        parts: list[str] = [self.BASE_VIDEO_AWARENESS]

        parts.append(TOOL_FOLLOW_UP_RULE)

        if self.persona_instructions:
            parts.append(self.persona_instructions)

        if self.language_profile is not None:
            lang_instructions = getattr(
                self.language_profile, "system_instructions", None
            )
            if lang_instructions:
                parts.append(lang_instructions)

        return "\n\n".join(filter(None, parts))

    def switch_language(self, code: str) -> None:
        """Update language profile and refresh the composed system prompt."""
        self.language_profile = detect_language(
            {"preferredLanguage": code},
            settings.default_language,
        )
        self._system_prompt = self.build_system_prompt()
        logger.info("Switched language to %s", self.language_profile.code)

    async def _publish_tool_output(self, tool_name: str, result: dict) -> None:
        """Publish a tool result to the LiveKit 'tool-output' data channel.

        The frontend's ToolOutputPanel listens on this topic and renders
        a structured card for each message received.
        """
        try:
            payload = json.dumps({"type": tool_name, **result}).encode()
            await asyncio.wait_for(
                self._room.local_participant.publish_data(payload, topic="tool-output"),
                timeout=1.0,
            )
            logger.debug("Published tool output: %s", tool_name)
        except TimeoutError:
            logger.warning(
                "Timed out publishing tool output for '%s'; continuing without UI payload",
                tool_name,
            )
        except Exception as exc:
            logger.warning("Failed to publish tool output for '%s': %s", tool_name, exc)

    async def _speak_tool_followup(
        self,
        context: RunContext,
        tool_name: str,
        result: Any,
    ) -> None:
        """No-op: Gemini native audio models generate speech after tool calls automatically.

        The TOOL_FOLLOW_UP_RULE in the system prompt instructs the model to deliver
        a spoken summary after every tool call. Calling session.say() here would fail
        because native audio pipelines have no separate TTS stage.
        """
        logger.debug("_speak_tool_followup called for '%s' (no-op for native audio)", tool_name)

