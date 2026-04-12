"""Standalone entry point for the LiveKit agent worker.

This module is executed as a subprocess by agent_runner.py so that the
LiveKit worker can run on its own main thread (required for signal handlers
and plugin registration) while FastAPI occupies the parent process.
"""
import json
import logging
import sys
import asyncio

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

from livekit import agents
from livekit.agents import AgentServer, AgentSession, TurnHandlingOptions
from livekit.plugins import google as lk_google

from app.agents.hackathon import ALLOWED_REALTIME_VOICES
from app.agents.registry import get_agent
from app.agent_settings import resolve_realtime_model
from app.config import settings

server = AgentServer()


@server.rtc_session(agent_name="gemini-hackathon-agent")
async def entrypoint(ctx: agents.JobContext):
    await ctx.connect()

    selected_voice = settings.realtime_voice
    selected_industry = settings.default_industry
    selected_model = resolve_realtime_model(settings.realtime_model)

    # Give the user participant a moment to join so token metadata is available.
    for _ in range(20):
        if ctx.room.remote_participants:
            break
        await asyncio.sleep(0.1)

    for participant in ctx.room.remote_participants.values():
        metadata = participant.metadata
        if metadata:
            try:
                parsed = json.loads(metadata)

                requested_industry = parsed.get("industry")
                if isinstance(requested_industry, str) and requested_industry.strip():
                    selected_industry = requested_industry.strip()

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
            model=selected_model,
            voice=selected_voice,
        ),
        turn_handling=TurnHandlingOptions(
            endpointing={
                "mode": "dynamic",
                "min_delay": 0.4,
                "max_delay": 2.8,
            },
        ),
    )

    agent = get_agent(selected_industry, ctx.room)
    logger.info(
        "Dispatching industry='%s' → %s",
        selected_industry,
        type(agent).__name__,
    )

    await session.start(
        room=ctx.room,
        agent=agent,
    )


if __name__ == "__main__":
    sys.argv = ["agent", "start"]
    agents.cli.run_app(server)
