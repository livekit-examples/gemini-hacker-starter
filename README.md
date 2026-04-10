# Exodia Multimodal Agent Demo

A minimal starting point for building with **Gemini 3.1**, **NanoBanana 2**, and **Lyria RealTime** on LiveKit. Get a working multimodal agent running in under 10 minutes, then make it your own.

Built for the **Google DeepMind × YC Hackathon**.

---

## What's included

| Model | What it does in this starter |
|---|---|
| **Gemini 3.1 Flash Audio** | Real-time voice conversation with native audio and video understanding |
| **NanoBanana 2** (`gemini-3.1-flash-image-preview`) | Generates images from text prompts — agent calls it as a function tool and sends the result to your browser |
| **Lyria RealTime** (`models/lyria-realtime-exp`) | Streams generative music into the LiveKit room as a live audio track |

The agent can see your camera, hear you speak, generate images on demand, and play real-time music — all through a single LiveKit room.

---

## Install the LiveKit MCP server

Install this before you start. It gives your AI coding assistant direct access to LiveKit documentation so you get accurate, current help as you build.

**Cursor** — click to install:

[![Install MCP Server in Cursor](https://cursor.com/deeplink/mcp-install-dark.svg)](https://cursor.com/en-US/install-mcp?name=livekit-docs&config=eyJ1cmwiOiJodHRwczovL2RvY3MubGl2ZWtpdC5pby9tY3AifQ%3D%3D)

Or add manually to your MCP settings:

```json
{
  "livekit-docs": {
    "url": "https://docs.livekit.io/mcp"
  }
}
```

**Claude Code**

```bash
claude mcp add --transport http livekit-docs https://docs.livekit.io/mcp
```

**Gemini CLI**

```bash
gemini mcp add --transport http livekit-docs https://docs.livekit.io/mcp
```

---

## Prerequisites

- Python 3.10–3.13
- Node.js 18+
- [uv](https://docs.astral.sh/uv/getting-started/installation/) (Python package manager)
- LiveKit CLI:
  - macOS: `brew install livekit-cli`
  - Linux: `curl -sSL https://get.livekit.io/cli | bash`
  - Windows: `winget install LiveKit.LiveKitCLI`
- [LiveKit Cloud account](https://cloud.livekit.io) (free)
- Google API key with access to Gemini 3.1, NanoBanana 2, and Lyria

---

## Quick start

### 1. Set up the agent

```bash
cd agent
uv sync
cp .env.example .env.local
```

Edit `.env.local` with your credentials:

```env
LIVEKIT_URL=wss://your-project.livekit.cloud
LIVEKIT_API_KEY=your_key
LIVEKIT_API_SECRET=your_secret
GOOGLE_API_KEY=your_google_api_key
```

Or use the LiveKit CLI to pull credentials from your cloud project automatically:

```bash
lk cloud auth
lk app env -w -d .env.local
```

### 2. Set up the frontend

```bash
cd ../frontend
pnpm install
cp .env.example .env.local
```

Edit `frontend/.env.local`:

```env
LIVEKIT_URL=wss://your-project.livekit.cloud
LIVEKIT_API_KEY=your_key
LIVEKIT_API_SECRET=your_secret
```

Or use the LiveKit CLI:

```bash
lk app env -w
```

### 3. Run the agent

```bash
cd agent
uv run agent.py dev
```

### 4. Run the frontend

In a new terminal:

```bash
cd frontend
pnpm dev
```

Open [http://localhost:3000](http://localhost:3000), click **Start hacking**, and talk to your agent.

---

## Try it out

Once running, try these prompts:

- *"Generate an image of a neon-lit street at night in the style of a Studio Ghibli film"*
- *"Play some calm ambient music"*
- *"Stop the music"*
- *"What do you see through my camera?"*
- *"Generate a logo for a company called Quantum Noodle"*

---

## Customization

All the extension points are marked with `# HACK HERE:` comments in `agent/agent.py`. Here are the main ones.

### Change the agent's persona

Edit `PERSONA_INSTRUCTIONS` at the top of `agent/agent.py`:

```python
PERSONA_INSTRUCTIONS = """You are a live sports commentator.
Watch the game through the user's camera and provide real-time strategic analysis.
Call out key moments, track the score, and keep energy high."""
```

### Add a function tool

```python
from livekit.agents import function_tool, RunContext

@function_tool()
async def search_the_web(self, context: RunContext, query: str) -> str:
    """Search the web for current information.
    
    Args:
        query: The search query
    """
    # your implementation here
    return "results..."
```

### Adjust video frame rate

By default, video frames are sampled based on voice activity. For continuous commentary (e.g., watching a game), use a constant frame rate:

```python
from livekit.agents import voice

session = AgentSession(
    llm=google.realtime.RealtimeModel(...),
    video_sampler=voice.VoiceActivityVideoSampler(speaking_fps=1.0, silent_fps=1.0)
)
```

### Swap the Gemini voice

Change the `voice` parameter in `agent.py`:

```python
llm=google.realtime.RealtimeModel(
    model=REALTIME_MODEL,
    voice="Kore",  # Options: Aoede, Charon, Fenrir, Kore, Puck
)
```

### Customize image generation

The `generate_image` tool in `HackathonAgent` sends the result as a data message to the frontend. You can extend it to:
- Apply a style prefix to every prompt (e.g., always render in watercolor)
- Send multiple images
- Log prompts and images for a gallery view

### Customize Lyria music

The `start_music` tool accepts a `prompt` (text description) and `bpm`. You can extend it to expose more Lyria controls like `density`, `brightness`, and `scale`. See the [Lyria RealTime docs](https://ai.google.dev/gemini-api/docs/music-generation) for all available config options.

---

## Project ideas

These are just starting points. Build whatever seems interesting.

**Live foley engine** — Agent watches your video feed and generates matching ambient sounds and music in real time using Lyria. Point the camera at rain, a fire, a crowd — the agent creates a matching soundscape.

**Live game asset generator** — Sketch character designs or level layouts on paper, show them to the camera, and ask the agent to render polished versions using NanoBanana 2.

**Interactive storytelling** — Narrate a scene out loud. The agent listens, generates an image of what you describe, and plays mood-appropriate music — all simultaneously.

**Spatial design tool** — Point your camera at a room and describe how you'd redesign it. The agent generates photo-realistic renders of the redesigned space.

**Accessibility scene describer** — Agent watches a live video feed and generates detailed audio descriptions plus spatial soundscapes for visually impaired users.

**Real-time style transfer** — Capture frames from the camera, send them through the image model with style prompts, and stream the stylized output back to the screen continuously.

---

## Architecture

```
Frontend (Next.js + Agents UI)
├── Microphone + camera → LiveKit room → agent receives audio/video
├── Agent speech → LiveKit room → browser plays audio
├── "generated-image" data message → browser renders image panel
└── Lyria audio track → browser plays music

Agent (Python)
├── Gemini 3.1 Flash Audio — realtime voice + vision
├── generate_image tool → NanoBanana 2 → publish_data("generated-image")
├── start_music tool → Lyria RealTime → publish AudioTrack
└── stop_music tool → unpublish AudioTrack
```

---

## Resources

- [LiveKit Agents documentation](https://docs.livekit.io/agents/)
- [Gemini Live API documentation](https://ai.google.dev/gemini-api/docs/live)
- [Lyria RealTime documentation](https://ai.google.dev/gemini-api/docs/music-generation)
- [Lyria RealTime cookbook](https://github.com/google-gemini/cookbook/blob/main/quickstarts/Get_started_LyriaRealTime.ipynb)
- [LiveKit Cloud](https://cloud.livekit.io)
- [Google AI Studio](https://aistudio.google.com)

Good luck — build something weird.
