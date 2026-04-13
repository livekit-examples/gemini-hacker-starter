"""ManufacturingAgent — process quality and visual defect analysis persona.

Persona: Marco, Process & Quality Engineer.
Methodical, precise, no-nonsense. Detects defects from visual descriptions,
retrieves the correct SOP in seconds, and generates structured defect reports
to feed directly into the quality management workflow.
"""

from __future__ import annotations

from livekit import rtc
from livekit.agents import RunContext, function_tool

from app.agents.persona import PersonaAgent
from app.tools.manufacturing_tools import (
    detect_visual_defect as _detect_visual_defect,
    generate_defect_report as _generate_defect_report,
    lookup_sop as _lookup_sop,
)


class ManufacturingAgent(PersonaAgent):
    """Marco — Process & Quality Engineer for EXODIA Voice Intelligence manufacturing demos."""

    persona_name = "Marco"
    persona_instructions = (
        "You are Marco, a Process & Quality Engineer at EXODIA Voice Intelligence. "
        "You are methodical, precise, and direct — you say what you see and call out "
        "non-conformances without softening the message, because production quality "
        "depends on clear, unambiguous communication. "
        "When the user describes a defect they have found on the production line or "
        "in a quality inspection, use detect_visual_defect immediately to classify the "
        "defect type, severity, and recommend the correct corrective action — never "
        "guess verbally when the tool can give a definitive answer. "
        "When multiple defects have been identified in a session, use generate_defect_report "
        "to compile them into a structured report that can be attached to the NCR workflow; "
        "always offer to generate a report at the end of a defect-classification sequence. "
        "When the user asks for a procedure — whether for lockout-tagout, torque specs, "
        "PPE requirements, inspection criteria, or error code recovery — call lookup_sop "
        "and read back the relevant steps clearly and in order; do not paraphrase safety "
        "steps, as accuracy is critical. "
        "If a defect is classified as critical, escalate immediately: state that production "
        "should stop, the affected batch should be quarantined, and a root-cause investigation "
        "must be opened before resuming. "
        "Keep your register professional and efficient — the factory floor has no tolerance "
        "for ambiguity or wasted words. "
        "Always confirm with the user whether they want to log the defect, retrieve the SOP, "
        "or both — never assume which action is needed without asking."
    )

    def __init__(self, room: rtc.Room) -> None:
        super().__init__(room=room)

    def _register_tools(self) -> None:
        self.register_tool(self.detect_visual_defect)
        self.register_tool(self.generate_defect_report)
        self.register_tool(self.lookup_sop)

    @function_tool()
    async def detect_visual_defect(
        self,
        context: RunContext,
        description: str,
    ) -> dict:
        """Classify a visual defect observed on the production line or in inspection.

        Call this whenever the user describes or shows a defect so you can
        classify its type, severity level, and surface the recommended action.

        Args:
            description: Free-text description of the visual defect, e.g.
                         "hairline crack visible on the left load-bearing bracket"
                         or "weld porosity on the frame cross-member".
        """
        result = _detect_visual_defect(description)
        await self._publish_tool_output("defect_detection", result)
        await self._speak_tool_followup(context, "defect_detection", result)
        return result

    @function_tool()
    async def generate_defect_report(
        self,
        context: RunContext,
        defects: list[dict],
    ) -> str:
        """Compile a list of defects into a formatted quality report.

        Call this when the user has finished identifying defects and wants
        a structured report for the NCR or quality management workflow.

        Args:
            defects: List of defect dicts, each with at minimum ``defect_type``,
                     ``severity``, ``area``, and ``recommended_action`` keys.
                     These are typically the outputs from prior detect_visual_defect calls.
        """
        report = _generate_defect_report(defects)
        await self._publish_tool_output(
            "defect_report",
            {"report": report, "defect_count": len(defects)},
        )
        await self._speak_tool_followup(
            context,
            "defect_report",
            {"report": report, "defect_count": len(defects)},
        )
        return report

    @function_tool()
    async def lookup_sop(
        self,
        context: RunContext,
        keyword: str,
    ) -> dict:
        """Look up a Standard Operating Procedure from the SOP library.

        Call this whenever the user asks for a procedure — torque specs,
        LOTO steps, PPE requirements, inspection criteria, or error recovery.
        Read the returned steps back clearly and in order.

        Args:
            keyword: Search term for the procedure, e.g. "torque M12",
                     "lockout hydraulic press", "weld inspection", "E-14 error".
        """
        result = _lookup_sop(keyword)
        await self._publish_tool_output("sop_lookup", result)
        await self._speak_tool_followup(context, "sop_lookup", result)
        return result
