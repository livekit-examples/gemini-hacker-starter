# Agent Setup

## Installation

### Using uv

```bash
uv sync
```

This will create a virtual environment and install all dependencies.

## Environment Variables

Copy the example environment file:

```bash
cp .env.example .env.local
```

Then edit `.env.local` with your credentials:

- `LIVEKIT_API_KEY` - Your LiveKit API key
- `LIVEKIT_API_SECRET` - Your LiveKit API secret
- `LIVEKIT_URL` - Your LiveKit server URL (e.g., `wss://your-project.livekit.cloud`)
- `GOOGLE_API_KEY` - Your Google/Gemini API key
- `REALTIME_MODEL` (optional) - Gemini Live model override. If omitted, the agent uses `gemini-2.5-flash-native-audio-latest`.
- `REALTIME_VOICE` (optional) - Gemini realtime voice (for example: `Aoede`, `Kore`, `Puck`, `Charon`, `Fenrir`). Default is `Aoede`.

Or use the LiveKit CLI to auto-populate:

```bash
lk app env -w
```

## Running the Agent

This starter uses LiveKit's latest `MultilingualModel` end-of-turn detector for pause-aware turn taking.

Before first run (one-time), download model assets used by LiveKit plugins:

```bash
uv run agent.py download-files
```

### Start with uv

```bash
uv run python agent.py dev
```

The agent will connect to LiveKit and wait for incoming sessions.
