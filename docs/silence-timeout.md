# Silence Timeout & Auto-Shutdown

The agent monitors user speech activity and gracefully ends a session when the user has been silent for a configurable duration. Before disconnecting, it speaks a localised farewell in the active language.

---

## How It Works

```
entrypoint()
  └── _silence_watchdog()          ← asyncio task, runs alongside the session
        ├── polls every check_interval_s
        ├── _has_remote_speech_activity() → resets idle clock on speech
        └── on timeout → _shutdown_due_to_silence()
              ├── _say_farewell()  ← speaks localised goodbye first
              └── tries shutdown in order: ctx.shutdown → session.aclose
                  → session.close → session.stop → room.disconnect
```

### 1. Watchdog loop (`_silence_watchdog`)

Started as an `asyncio.create_task` in `entrypoint()` immediately before `session.start()`. It polls `room.active_speakers` and `room.remote_participants` for audio levels above the threshold. Any audio above the threshold resets the idle clock; when the idle duration exceeds the timeout the shutdown sequence begins. The task is cancelled in the `finally` block if the session ends for any other reason.

### 2. Speech detection (`_has_remote_speech_activity`)

Checks two sources on the LiveKit room object:
- `room.active_speakers` — participants flagged as currently speaking
- `room.remote_participants` — all remote participants, checked by `audio_level`

Either source returning a level ≥ `threshold` is enough to count as activity.

### 3. Farewell utterance (`_say_farewell`)

Before any shutdown attempt, the agent calls `session.say()` with a short, natural phrase in the session language. Phrases are defined in `_SILENCE_FAREWELL_PHRASES` in `agent_main.py`:

| Language | Phrase |
|---|---|
| `en` | "It looks like you've stepped away. I'll end the session now — feel free to reconnect whenever you're ready." |
| `it` | "Sembra che tu ti sia allontanato. Concludo la sessione — puoi riconnetterti quando vuoi." |
| `ar-EG` | "يبدو إنك مشغول. هخلي الجلسة دلوقتي — تقدر ترجع أي وقت." |
| `ar-AE` | "يبدو أنك ابتعدت. سأنهي الجلسة الآن — يمكنك الاتصال مجدداً متى شئت." |

If `say()` is not available on the session object, or if it throws, the failure is logged as a warning and shutdown continues normally.

The active language is read from participant metadata (`preferredLanguage` key) at session start, matching the same field the frontend writes when the user picks a language.

### 4. Shutdown cascade (`_shutdown_due_to_silence`)

Tries shutdown methods in order until one succeeds, logging each attempt:

1. `ctx.shutdown()`
2. `session.aclose()`
3. `session.close()`
4. `session.stop()`
5. `ctx.room.disconnect()`

The cascade exists because the LiveKit Agents SDK API surface differs between versions. Each method is attempted with `try/except` so a failure in one does not prevent the next from being tried.

---

## Configuration

All settings are read via `pydantic-settings` from environment variables (or `.env.local`):

| Variable | Default | Description |
|---|---|---|
| `SILENCE_TIMEOUT_SECONDS` | `45.0` | Seconds of silence before shutdown. Set to `0` or negative to disable entirely. |
| `SILENCE_CHECK_INTERVAL_SECONDS` | `1.0` | How often the watchdog polls for speech activity. |
| `SILENCE_AUDIO_LEVEL_THRESHOLD` | `0.02` | Minimum audio level (0–1) that counts as speech. |

**To disable the timeout completely**, set `SILENCE_TIMEOUT_SECONDS=0`.

---

## Relevant Files

| File | Role |
|---|---|
| `backend/app/agent_main.py` | Watchdog, farewell, and shutdown logic |
| `backend/app/config.py` | `silence_*` settings |
