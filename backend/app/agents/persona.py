"""PersonaAgent — adds language, persona, and tool registry to BaseAgent.

Subclasses set `persona_name` and `persona_instructions` as instance
attributes *before* calling ``super().__init__(room)`` so that
``build_system_prompt()`` picks them up during construction.
"""
from __future__ import annotations

import logging
from typing import Any

from livekit import rtc

from app.agents.base import BaseAgent

logger = logging.getLogger(__name__)


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
    language_profile: Any = None

    def __init__(self, room: rtc.Room) -> None:
        self._tool_registry: list = []
        instructions = self.build_system_prompt()
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

        if self.persona_instructions:
            parts.append(self.persona_instructions)

        if self.language_profile is not None:
            lang_instructions = getattr(self.language_profile, "system_instructions", None)
            if lang_instructions:
                parts.append(lang_instructions)

        return "\n\n".join(filter(None, parts))

    def switch_language(self, code: str) -> None:
        """Update language_profile by code and rebuild system prompt.

        Wired to the language detector introduced in Session 10. A graceful
        no-op is performed if the detector module is not yet available.
        """
        try:
            from app.languages.detector import detect_language  # Session 10

            self.language_profile = detect_language({"preferredLanguage": code}, "en")
            logger.info("Switched language to %s", code)
        except ImportError:
            logger.debug(
                "Language detector not available yet (implemented in Session 10); "
                "language code '%s' stored but not applied.",
                code,
            )
