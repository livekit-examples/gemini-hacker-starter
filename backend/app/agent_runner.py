"""Launch the LiveKit agent worker as a managed child subprocess.

``agents.cli.run_app`` calls ``signal.signal()`` which Python only permits on the
main thread.  FastAPI/uvicorn owns the main thread, so the worker cannot run
inside a thread pool.  Running it as a subprocess gives it its own main thread
while keeping it inside the same Docker image (single deployable unit).

Stdout/stderr are *not* captured so agent log lines flow straight through to the
container log alongside the FastAPI lines.
"""
import asyncio
import logging
import sys

logger = logging.getLogger(__name__)


async def start_agent_server() -> asyncio.Task:
    """Start the agent subprocess loop as a background asyncio Task."""
    task = asyncio.create_task(_agent_loop())
    return task


async def _agent_loop() -> None:
    """Spawn the agent subprocess; restart with back-off on unexpected exit."""
    proc: asyncio.subprocess.Process | None = None

    while True:
        try:
            proc = await asyncio.create_subprocess_exec(
                sys.executable,
                "-m",
                "app.agent_main",
                # Inherit stdout/stderr so logs appear in docker compose output.
            )
            logger.info("Agent subprocess started (pid=%d)", proc.pid)
            returncode = await proc.wait()

            # SIGTERM (−15) or exit 0 means intentional shutdown — don't retry.
            if returncode in (0, -15):
                logger.info("Agent subprocess exited cleanly (code=%d)", returncode)
                return

            raise RuntimeError(f"Agent subprocess exited with code {returncode}")

        except asyncio.CancelledError:
            logger.info("Agent runner cancelled — terminating subprocess")
            if proc and proc.returncode is None:
                proc.terminate()
                try:
                    await asyncio.wait_for(proc.wait(), timeout=5.0)
                except asyncio.TimeoutError:
                    proc.kill()
            raise

        except Exception:
            logger.exception("Agent server error — retrying in 5 s")
            await asyncio.sleep(5)
