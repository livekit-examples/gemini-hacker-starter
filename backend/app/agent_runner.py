import asyncio
import json
import logging
import sys

logger = logging.getLogger(__name__)


async def start_agent_server() -> asyncio.Task:
    """Start the LiveKit agent server as an asyncio background task.

    Returns a Task that runs the agent server loop. The task retries on failure
    so it remains alive even if the initial LiveKit connection is refused.
    """
    task = asyncio.create_task(_agent_loop())
    return task


async def _agent_loop() -> None:
    """Run the agent server in a thread; retry with back-off on failure."""
    while True:
        try:
            await asyncio.to_thread(_blocking_agent_start)
        except asyncio.CancelledError:
            logger.info("Agent server task cancelled")
            raise
        except Exception:
            logger.exception("Agent server error — retrying in 5 s")
            await asyncio.sleep(5)


def _blocking_agent_start() -> None:
    """Instantiate and run the AgentServer in a dedicated thread.

    This function runs ``agents.cli.run_app`` which creates its own event loop,
    so it must be called from a thread (via ``asyncio.to_thread``), never from
    the FastAPI event loop directly.
    """
    from livekit import agents
    from livekit.agents import AgentServer, AgentSession, TurnHandlingOptions, inference
    from livekit.plugins import google as lk_google
    from livekit.plugins.turn_detector.multilingual import MultilingualModel
    from livekit import rtc

    from app.agents.hackathon import (
        HackathonAgent,
        REALTIME_MODEL,
        REALTIME_VOICE,
        ALLOWED_REALTIME_VOICES,
    )

    server = AgentServer()

    @server.rtc_session(agent_name="gemini-hackathon-agent")
    async def entrypoint(ctx: agents.JobContext):
        has_video = False
        selected_voice = REALTIME_VOICE

        def on_track_subscribed(
            track: rtc.Track,
            publication: rtc.TrackPublication,
            participant: rtc.RemoteParticipant,
        ):
            nonlocal has_video
            if track.kind == rtc.TrackKind.KIND_VIDEO:
                has_video = True
                logger.info("Video track subscribed from %s", participant.identity)

        def on_track_unsubscribed(
            track: rtc.Track,
            publication: rtc.TrackPublication,
            participant: rtc.RemoteParticipant,
        ):
            nonlocal has_video
            if track.kind == rtc.TrackKind.KIND_VIDEO:
                has_video = any(
                    pub.track and pub.track.kind == rtc.TrackKind.KIND_VIDEO
                    for p in ctx.room.remote_participants.values()
                    for pub in p.track_publications.values()
                    if pub.subscribed
                )

        ctx.room.on("track_subscribed", on_track_subscribed)
        ctx.room.on("track_unsubscribed", on_track_unsubscribed)

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

            for publication in participant.track_publications.values():
                if (
                    publication.subscribed
                    and publication.track
                    and publication.track.kind == rtc.TrackKind.KIND_VIDEO
                ):
                    has_video = True
                    break

        turn_handling = TurnHandlingOptions(
            turn_detection=MultilingualModel(),
            endpointing={
                "mode": "dynamic",
                "min_delay": 0.4,
                "max_delay": 2.8,
            },
        )

        session = AgentSession(
            llm=lk_google.realtime.RealtimeModel(
                model=REALTIME_MODEL,
                voice=selected_voice,
            ),
            stt=inference.STT(language="multi"),
            turn_handling=turn_handling,
        )

        await session.start(
            room=ctx.room,
            agent=HackathonAgent(room=ctx.room),
        )

        await ctx.connect()

        try:
            await session.generate_reply(
                instructions=(
                    "Greet the user. Let them know you can generate images with NanoBanana 2 "
                    "and play real-time music with Lyria. Mention they can enable their camera "
                    "for visual context."
                )
            )
        except Exception as exc:
            logger.warning("Initial greeting failed: %s", exc)

    # Simulate a CLI `start` invocation so run_app picks up the right sub-command.
    orig_argv = sys.argv
    sys.argv = ["agent", "start"]
    try:
        agents.cli.run_app(server)
    finally:
        sys.argv = orig_argv
