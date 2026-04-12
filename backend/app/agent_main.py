"""Standalone entry point for the LiveKit agent worker.

This module is executed as a subprocess by agent_runner.py so that the
LiveKit worker can run on its own main thread (required for signal handlers
and plugin registration) while FastAPI occupies the parent process.
"""

import json
import logging
import sys
import asyncio
import inspect
import time
from collections.abc import Callable
from typing import Any

from livekit import agents

from livekit.agents import AgentServer, AgentSession, TurnHandlingOptions
from livekit.plugins import google as lk_google

from app.agents.hackathon import ALLOWED_REALTIME_VOICES
from app.agents.persona import PersonaAgent
from app.agents.registry import get_agent
from app.agent_settings import resolve_realtime_model
from app.config import settings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


server = AgentServer()


async def _call_maybe_async(fn: Callable[..., Any]) -> None:
    result = fn()
    if inspect.isawaitable(result):
        await result


def _has_remote_speech_activity(room: Any, threshold: float) -> bool:
    """Best-effort speech activity detection from room participant levels."""
    active_speakers = getattr(room, "active_speakers", []) or []
    for participant in active_speakers:
        if float(getattr(participant, "audio_level", 0.0) or 0.0) >= threshold:
            return True

    remote_participants = getattr(room, "remote_participants", {}) or {}
    for participant in remote_participants.values():
        if float(getattr(participant, "audio_level", 0.0) or 0.0) >= threshold:
            return True

    return False


_SILENCE_FAREWELL_PHRASES: dict[str, str] = {
    "en": "It looks like you've stepped away. I'll end the session now — feel free to reconnect whenever you're ready.",
    "it": "Sembra che tu ti sia allontanato. Concludo la sessione — puoi riconnetterti quando vuoi.",
    "ar-EG": "يبدو إنك مشغول. هخلي الجلسة دلوقتي — تقدر ترجع أي وقت.",
    "ar-AE": "يبدو أنك ابتعدت. سأنهي الجلسة الآن — يمكنك الاتصال مجدداً متى شئت.",
    "it-NAP": "Uè, sembra ca te ne sì gghiuto. Mo chiudo la sessione — torna quanno vuò!",
    "it-SIC": "Pari ca t'alluntanasti. Chiudu la sibbira ora — torna quannu voli!",
}


def _current_language(agent: "PersonaAgent", fallback: str) -> str:
    """Return the agent's active language code, falling back to *fallback*."""
    profile = getattr(agent, "language_profile", None)
    code = getattr(profile, "code", None)
    return code if isinstance(code, str) and code.strip() else fallback


async def _say_farewell(session: AgentSession, language_code: str) -> None:
    """Speak a short farewell before disconnecting due to silence."""
    phrase = _SILENCE_FAREWELL_PHRASES.get(language_code) or _SILENCE_FAREWELL_PHRASES["en"]
    say_fn = getattr(session, "say", None)
    if not callable(say_fn):
        return
    try:
        speech = say_fn(phrase, add_to_chat_ctx=False)
        if inspect.isawaitable(speech):
            await speech
        elif hasattr(speech, "wait_for_playout"):
            await speech.wait_for_playout()
    except Exception as exc:
        logger.warning("Silence farewell utterance failed: %s", exc)


async def _shutdown_due_to_silence(
    ctx: agents.JobContext, session: AgentSession, agent: "PersonaAgent", fallback_language: str = "en"
) -> None:
    """Speak a farewell in the agent's current language, then shut down gracefully."""
    language_code = _current_language(agent, fallback_language)
    await _say_farewell(session, language_code)

    shutdown_targets: list[tuple[str, Any]] = [
        ("job_context.shutdown", getattr(ctx, "shutdown", None)),
        ("session.aclose", getattr(session, "aclose", None)),
        ("session.close", getattr(session, "close", None)),
        ("session.stop", getattr(session, "stop", None)),
        ("room.disconnect", getattr(ctx.room, "disconnect", None)),
    ]

    for label, shutdown_fn in shutdown_targets:
        if not callable(shutdown_fn):
            continue

        try:
            await _call_maybe_async(shutdown_fn)
            logger.info("Silence timeout: shutdown executed via %s", label)
            return
        except Exception as exc:
            logger.warning(
                "Silence timeout: shutdown via %s failed: %s",
                label,
                exc,
            )

    logger.warning("Silence timeout reached, but no supported shutdown method was found")


async def _silence_watchdog(
    ctx: agents.JobContext,
    session: AgentSession,
    agent: "PersonaAgent",
    fallback_language: str = "en",
) -> None:
    timeout_s = settings.silence_timeout_seconds
    if timeout_s <= 0:
        return

    check_interval_s = max(0.2, settings.silence_check_interval_seconds)
    threshold = max(0.0, settings.silence_audio_level_threshold)
    last_activity_at = time.monotonic()

    logger.info(
        "Silence watchdog enabled (timeout=%.1fs, interval=%.1fs, threshold=%.3f)",
        timeout_s,
        check_interval_s,
        threshold,
    )

    while True:
        await asyncio.sleep(check_interval_s)

        if _has_remote_speech_activity(ctx.room, threshold):
            last_activity_at = time.monotonic()
            continue

        idle_for = time.monotonic() - last_activity_at
        if idle_for >= timeout_s:
            logger.info(
                "Silence timeout reached after %.1fs without user speech activity",
                idle_for,
            )
            await _shutdown_due_to_silence(ctx, session, agent, fallback_language)
            return


def _build_agent_session(selected_model: str, selected_voice: str) -> AgentSession:
    """Build an AgentSession for Google realtime voice.

    For realtime models, do not force LiveKit Inference STT. Let the
    realtime model handle speech recognition natively to avoid gateway
    rate-limit handshakes.
    """
    return AgentSession(
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


@server.rtc_session(agent_name="gemini-hackathon-agent")
async def entrypoint(ctx: agents.JobContext):
    await ctx.connect()

    selected_voice = settings.realtime_voice
    selected_industry = settings.default_industry
    selected_model = resolve_realtime_model(settings.realtime_model)
    selected_language = settings.default_language

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

                requested_language = parsed.get("preferredLanguage")
                if isinstance(requested_language, str) and requested_language.strip():
                    selected_language = requested_language.strip()
                    logger.info(
                        "Using requested language from participant metadata: %s",
                        selected_language,
                    )
                    break
            except (json.JSONDecodeError, TypeError):
                logger.debug("Participant metadata was not valid JSON")

    agent = get_agent(selected_industry, ctx.room)
    logger.info(
        "Dispatching industry='%s' → %s",
        selected_industry,
        type(agent).__name__,
    )

    session = _build_agent_session(selected_model, selected_voice)
    watchdog_task = asyncio.create_task(
        _silence_watchdog(ctx, session, agent, selected_language)
    )

    try:
        await session.start(
            room=ctx.room,
            agent=agent,
        )
    finally:
        watchdog_task.cancel()
        await asyncio.gather(watchdog_task, return_exceptions=True)


if __name__ == "__main__":
    sys.argv = ["agent", "start"]
    agents.cli.run_app(server)
