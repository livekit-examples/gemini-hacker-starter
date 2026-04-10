"""Tests for agent_runner.start_agent_server().

We patch _blocking_agent_start so no real LiveKit connection is attempted.
The patch makes it raise immediately, causing _agent_loop to catch the error
and enter its retry sleep — which keeps the Task alive (not done).
"""
import asyncio
from unittest.mock import patch

import pytest

import app.agent_runner as agent_runner_module
from app.agent_runner import start_agent_server


@pytest.mark.asyncio
async def test_start_agent_server_returns_task():
    """start_agent_server() must return an asyncio.Task without raising."""
    with patch.object(
        agent_runner_module,
        "_blocking_agent_start",
        side_effect=RuntimeError("no livekit in tests"),
    ):
        task = await start_agent_server()

    assert isinstance(task, asyncio.Task), "start_agent_server() must return an asyncio.Task"

    # Clean up: cancel and drain
    task.cancel()
    await asyncio.gather(task, return_exceptions=True)


@pytest.mark.asyncio
async def test_task_not_done_immediately_after_creation():
    """The returned task must still be running immediately after creation.

    _blocking_agent_start is patched to raise immediately.  _agent_loop
    catches the exception and sleeps for 5 s, so the task is alive.
    """
    with patch.object(
        agent_runner_module,
        "_blocking_agent_start",
        side_effect=RuntimeError("no livekit in tests"),
    ):
        task = await start_agent_server()
        # Yield one iteration so _agent_loop can enter its except/sleep branch.
        await asyncio.sleep(0)

    assert not task.done(), "Task must still be running (in retry sleep), not done"

    task.cancel()
    await asyncio.gather(task, return_exceptions=True)
