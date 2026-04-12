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
            lang_instructions = getattr(self.language_profile, "system_instructions", None)
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
        """Speak a realtime-safe post-tool summary to avoid silent tool turns.

        Google realtime preview models do not support AgentSession.generate_reply.
        Use AgentSession.say instead so tool calls can always complete with speech.
        """
        code = (self.language_profile.code if self.language_profile else "en").strip()
        followup_text = self._build_tool_followup_text(code, tool_name, result)

        try:
            # add_to_chat_ctx=False avoids unsupported update_chat_ctx calls on preview models.
            speech = context.session.say(followup_text, add_to_chat_ctx=False)
            await speech.wait_for_playout()
        except Exception as exc:
            logger.warning(
                "Failed to speak post-tool follow-up for '%s': %s",
                tool_name,
                exc,
            )

    def _build_tool_followup_text(self, code: str, tool_name: str, result: Any) -> str:
        """Build a short localized spoken summary after a tool call."""
        tool_labels = {
            "service_requirements": {"en": "service requirements", "it": "i requisiti del servizio", "ar-EG": "متطلبات الخدمة", "ar-AE": "متطلبات الخدمة"},
            "application_status": {"en": "application status", "it": "lo stato della pratica", "ar-EG": "حالة الطلب", "ar-AE": "حالة الطلب"},
            "appointment_confirmation": {"en": "appointment booking", "it": "la prenotazione dell'appuntamento", "ar-EG": "حجز الموعد", "ar-AE": "حجز الموعد"},
        }
        localized_label = tool_labels.get(tool_name, {}).get(code, tool_name.replace("_", " "))

        summary = self._summarize_tool_result(result)

        if code == "it":
            return f"Ho controllato {localized_label}. {summary} Come desidera procedere?"
        if code == "ar-EG":
            return f"راجعت {localized_label}. {summary} تحب نعمل إيه بعد كده؟"
        if code == "ar-AE":
            return f"تمت مراجعة {localized_label}. {summary} تفضل ماذا نفعل بعد ذلك؟"
        return f"I checked {localized_label}. {summary} What would you like to do next?"

    def _summarize_tool_result(self, result: Any) -> str:
        """Return a compact textual summary from tool output."""
        if isinstance(result, dict):
            if result.get("found") is False:
                return "No exact match was found in the records."

            parts: list[str] = []
            for key in ("service", "status", "date", "time", "office", "confirmation_id"):
                value = result.get(key)
                if value:
                    parts.append(f"{key.replace('_', ' ')}: {value}")
                if len(parts) >= 2:
                    break

            required_documents = result.get("required_documents")
            if isinstance(required_documents, list) and required_documents:
                parts.append(f"required documents: {len(required_documents)}")

            if parts:
                return "; ".join(parts) + "."

        try:
            serialized = json.dumps(result, ensure_ascii=False, default=str)
            if len(serialized) > 120:
                serialized = serialized[:117] + "..."
            return f"Result ready: {serialized}"
        except TypeError:
            text = str(result)
            if len(text) > 120:
                text = text[:117] + "..."
            return f"Result ready: {text}"
