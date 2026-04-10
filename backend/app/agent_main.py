"""Standalone entry point for the LiveKit agent worker.

This module is executed as a subprocess by agent_runner.py so that the
LiveKit worker can run on its own main thread (required for signal handlers
and plugin registration) while FastAPI occupies the parent process.
"""
import json
import logging
import sys

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

from livekit import agents
from livekit.agents import AgentServer, AgentSession, TurnHandlingOptions, inference
from livekit.plugins import google as lk_google

from app.agents.hackathon import REALTIME_MODEL, REALTIME_VOICE, ALLOWED_REALTIME_VOICES
from app.agents.registry import get_agent
from app.config import settings

server = AgentServer()


@server.rtc_session(agent_name="gemini-hackathon-agent")
async def entrypoint(ctx: agents.JobContext):
    selected_voice = REALTIME_VOICE

    for participant in ctx.room.remote_participants.values():
        metadata = participant.metadata
        if metadata:
            try:
                parsed = json.loads(metadata)
                requested_voice = parsed.get("realtimeVoice")
                if (
                    isinstance(requested_voice, str)
                    and requested_voice in ALLOWED_REALTIME_VOICES
                ):
                    selected_voice = requested_voice
                    logger.info(
                        "Using requested realtime voice from participant metadata: %s",
                        selected_voice,
                    )
                    break
            except (json.JSONDecodeError, TypeError):
                logger.debug("Participant metadata was not valid JSON")

    session = AgentSession(
        llm=lk_google.realtime.RealtimeModel(
            model=REALTIME_MODEL,
            voice=selected_voice,
        ),
        stt=inference.STT(language="multi"),
        turn_handling=TurnHandlingOptions(
            endpointing={
                "mode": "dynamic",
                "min_delay": 0.4,
                "max_delay": 2.8,
            },
        ),
    )

    agent = get_agent(settings.default_industry, ctx.room)
    logger.info(
        "Dispatching industry='%s' → %s",
        settings.default_industry,
        type(agent).__name__,
    )

    await session.start(
        room=ctx.room,
        agent=agent,
    )

    await ctx.connect()


if __name__ == "__main__":
    sys.argv = ["agent", "start"]
    agents.cli.run_app(server)
