"""BaseAgent — core LiveKit wiring.

No persona, no tools, no language. Handles room reference and track
subscription lifecycle callbacks that all industry agents share.
"""
import logging

from livekit import rtc
from livekit.agents import Agent

logger = logging.getLogger(__name__)

BASE_VIDEO_AWARENESS = (
    "You can only see video when the user enables their camera or screenshare.\n"
    "When asked about visuals:\n"
    "- Only describe what you can actually see in provided video frames.\n"
    "- Never invent visual details that are not present.\n"
    "- If no camera is active, tell the user to enable it."
)


class BaseAgent(Agent):
    """Wraps livekit.agents.Agent. Holds room + session.

    Provides track subscription lifecycle hooks. No persona, no tools,
    no language — those are added by PersonaAgent.
    """

    BASE_VIDEO_AWARENESS: str = BASE_VIDEO_AWARENESS

    def __init__(self, room: rtc.Room, **kwargs) -> None:
        super().__init__(**kwargs)
        self._room = room
        self._has_video: bool = False

        room.on("track_subscribed", self._on_track_subscribed)
        room.on("track_unsubscribed", self._on_track_unsubscribed)

    def _on_track_subscribed(
        self,
        track: rtc.Track,
        publication: rtc.TrackPublication,
        participant: rtc.RemoteParticipant,
    ) -> None:
        if track.kind == rtc.TrackKind.KIND_VIDEO:
            self._has_video = True
            logger.info("Video track subscribed from %s", participant.identity)

    def _on_track_unsubscribed(
        self,
        track: rtc.Track,
        publication: rtc.TrackPublication,
        participant: rtc.RemoteParticipant,
    ) -> None:
        if track.kind == rtc.TrackKind.KIND_VIDEO:
            self._has_video = any(
                pub.track and pub.track.kind == rtc.TrackKind.KIND_VIDEO
                for p in self._room.remote_participants.values()
                for pub in p.track_publications.values()
                if pub.subscribed
            )
