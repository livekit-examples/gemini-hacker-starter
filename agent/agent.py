import asyncio
import logging
import os

from dotenv import load_dotenv
from google import genai
from google.genai import types as genai_types
from livekit import agents, rtc
from livekit.agents import (
    Agent,
    AgentServer,
    AgentSession,
    RunContext,
    TurnHandlingOptions,
    function_tool,
    inference,
)
from livekit.plugins import google
from livekit.plugins.turn_detector.multilingual import MultilingualModel

load_dotenv(".env.local")

logger = logging.getLogger(__name__)

# ─────────────────────────────────────────────
# HACK HERE: swap model IDs to experiment
# ─────────────────────────────────────────────
# Use a model that's broadly available for Gemini Live via API keys.
REALTIME_MODEL = os.getenv("REALTIME_MODEL", "gemini-2.5-flash-native-audio-latest")
IMAGE_MODEL = "gemini-3.1-flash-image-preview"  # NanoBanana 2
LYRIA_MODEL = "models/lyria-realtime-exp"

# ─────────────────────────────────────────────
# HACK HERE: change the agent's persona
# ─────────────────────────────────────────────
PERSONA_INSTRUCTIONS = """You are a creative multimodal AI assistant at a Google DeepMind x YC hackathon.
You can see through the user's camera, hear them speak, generate images, and play real-time music.

Your capabilities:
- generate_image: Create images with NanoBanana 2 (Gemini 3.1 Flash Image). Use this when asked to generate, create, render, or visualize anything.
- start_music: Play real-time generative music with Lyria RealTime. Use this for soundtracks, ambience, or any audio atmosphere.
- stop_music: Stop the current music.

IMPORTANT: When the user asks you to generate an image, ALWAYS say a brief acknowledgment first (like "On it!" or "Let me create that for you") before calling generate_image. The image takes a few seconds to generate, so the user needs to know you heard them.

Be concise and creative. Lean into the multimodal possibilities — when a user describes something, offer to generate it."""


class HackathonAgent(Agent):
    BASE_VIDEO_AWARENESS = """You can only see video when the user enables their camera or screenshare.
When asked about visuals:
- Only describe what you can actually see in provided video frames.
- Never invent visual details that are not present.
- If no camera is active, tell the user to enable it."""

    def __init__(self, room: rtc.Room) -> None:
        full_instructions = f"{self.BASE_VIDEO_AWARENESS}\n\n{PERSONA_INSTRUCTIONS}"
        super().__init__(instructions=full_instructions)

        self._room = room
        self._music_task: asyncio.Task | None = None
        self._music_stop_event = asyncio.Event()
        self._music_track_pub = None

        # Standard client for image generation (NanoBanana 2)
        self._image_client = genai.Client(api_key=os.environ["GOOGLE_API_KEY"])

        # v1alpha client required for Lyria RealTime
        self._lyria_client = genai.Client(
            api_key=os.environ["GOOGLE_API_KEY"],
            http_options={"api_version": "v1alpha"},
        )

    # ─────────────────────────────────────────
    # HACK HERE: customize the image generation prompt or post-processing
    # ─────────────────────────────────────────
    @function_tool()
    async def generate_image(
        self,
        context: RunContext,
        prompt: str,
    ) -> str:
        """Generate an image using NanoBanana 2 and display it on the user's screen.

        Call this whenever the user asks you to create, generate, render, or visualize something.

        Args:
            prompt: A detailed description of the image to generate. Be specific about style,
                    composition, lighting, and content.
        """
        logger.info("Generating image: %s", prompt)
        try:
            response = await asyncio.to_thread(
                self._image_client.models.generate_content,
                model=IMAGE_MODEL,
                contents=prompt,
                config=genai_types.GenerateContentConfig(
                    response_modalities=["Text", "Image"]
                ),
            )

            image_bytes = None
            mime_type = "image/png"
            for part in response.candidates[0].content.parts:
                if part.inline_data is not None:
                    image_bytes = part.inline_data.data
                    mime_type = part.inline_data.mime_type or "image/png"
                    break

            if image_bytes is None:
                return "Image generation did not return any image data."

            writer = await self._room.local_participant.stream_bytes(
                name="generated-image",
                mime_type=mime_type,
                total_size=len(image_bytes),
                topic="generated-image",
                attributes={"prompt": prompt},
            )
            await writer.write(image_bytes)
            await writer.aclose()

            return f"Image generated and sent to the screen. Prompt used: {prompt}"

        except Exception as exc:
            logger.error("Image generation failed: %s", exc)
            return f"Image generation failed: {exc}"

    # ─────────────────────────────────────────
    # HACK HERE: customize Lyria prompts or add BPM/density controls
    # ─────────────────────────────────────────
    @function_tool()
    async def start_music(
        self,
        context: RunContext,
        prompt: str,
        bpm: int = 120,
    ) -> str:
        """Start streaming real-time generative music using Lyria RealTime.

        Music plays continuously until stop_music is called. Use this for soundtracks,
        atmospheric audio, or any mood-setting music.

        Args:
            prompt: Description of the music to generate, e.g. "upbeat electronic", "calm ambient piano",
                    "epic orchestral score", "jazzy lounge". Can combine styles: "lo-fi hip-hop with strings".
            bpm: Beats per minute (default: 120). Lower values (60-90) feel slower and more ambient;
                 higher values (120-160) feel energetic.
        """
        await self._stop_music_internal()
        logger.info("Starting Lyria music: %s @ %d BPM", prompt, bpm)
        self._music_stop_event.clear()
        self._music_task = asyncio.create_task(self._stream_lyria(prompt, bpm))
        return f"Music started: {prompt} at {bpm} BPM. Call stop_music to stop it."

    @function_tool()
    async def stop_music(self, context: RunContext) -> str:
        """Stop the currently playing Lyria music."""
        if self._music_task is None or self._music_task.done():
            return "No music is currently playing."
        await self._stop_music_internal()
        return "Music stopped."

    async def _stop_music_internal(self) -> None:
        if self._music_task and not self._music_task.done():
            self._music_stop_event.set()
            self._music_task.cancel()
            try:
                await self._music_task
            except (asyncio.CancelledError, Exception):
                pass
        self._music_task = None

        if self._music_track_pub is not None:
            try:
                await self._room.local_participant.unpublish_track(self._music_track_pub.sid)
            except Exception:
                pass
            self._music_track_pub = None

    async def _stream_lyria(self, prompt: str, bpm: int) -> None:
        """Stream Lyria audio into the LiveKit room as a published audio track."""
        SAMPLE_RATE = 48000
        NUM_CHANNELS = 2

        audio_source = rtc.AudioSource(sample_rate=SAMPLE_RATE, num_channels=NUM_CHANNELS)
        track = rtc.LocalAudioTrack.create_audio_track("lyria-music", audio_source)
        options = rtc.TrackPublishOptions(source=rtc.TrackSource.SOURCE_UNKNOWN)

        pub = await self._room.local_participant.publish_track(track, options)
        self._music_track_pub = pub

        try:
            async with self._lyria_client.aio.live.music.connect(model=LYRIA_MODEL) as session:
                await session.set_weighted_prompts(
                    prompts=[genai_types.WeightedPrompt(text=prompt, weight=1.0)]
                )
                await session.set_music_generation_config(
                    config=genai_types.LiveMusicGenerationConfig(bpm=bpm)
                )
                await session.play()

                async for message in session.receive():
                    if self._music_stop_event.is_set():
                        break

                    chunks = message.server_content.audio_chunks
                    if chunks:
                        audio_bytes = chunks[0].data
                        if audio_bytes:
                            # 16-bit stereo = 4 bytes per sample pair
                            samples_per_channel = len(audio_bytes) // (NUM_CHANNELS * 2)
                            frame = rtc.AudioFrame(
                                data=audio_bytes,
                                sample_rate=SAMPLE_RATE,
                                num_channels=NUM_CHANNELS,
                                samples_per_channel=samples_per_channel,
                            )
                            await audio_source.capture_frame(frame)

        except asyncio.CancelledError:
            pass
        except Exception as exc:
            logger.error("Lyria streaming error: %s", exc)
        finally:
            if self._music_track_pub is not None:
                try:
                    await self._room.local_participant.unpublish_track(
                        self._music_track_pub.sid
                    )
                except Exception:
                    pass
                self._music_track_pub = None


server = AgentServer()


@server.rtc_session(agent_name="gemini-hackathon-agent")
async def entrypoint(ctx: agents.JobContext):
    has_video = False

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
        for publication in participant.track_publications.values():
            if (
                publication.subscribed
                and publication.track
                and publication.track.kind == rtc.TrackKind.KIND_VIDEO
            ):
                has_video = True
                break

    session = AgentSession(
        llm=google.realtime.RealtimeModel(
            model=REALTIME_MODEL,
            voice="Aoede",
        ),
        # Use LiveKit's context-aware turn detector for improved human pause handling.
        stt=inference.STT(language="multi"),
        turn_handling=TurnHandlingOptions(
            turn_detection=MultilingualModel(),
            endpointing={
                "mode": "dynamic",
                "min_delay": 0.4,
                "max_delay": 2.8,
            },
        ),
    )

    await session.start(
        room=ctx.room,
        agent=HackathonAgent(room=ctx.room),
    )

    await ctx.connect()

    try:
        await session.generate_reply(
            instructions="Greet the user. Let them know you can generate images with NanoBanana 2 and play real-time music with Lyria. Mention they can enable their camera for visual context."
        )
    except Exception as exc:
        logger.warning("Initial greeting failed: %s", exc)


if __name__ == "__main__":
    agents.cli.run_app(server)
