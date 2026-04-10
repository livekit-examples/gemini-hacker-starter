"""Tests for agent_runner.start_agent_server().

We patch asyncio.create_subprocess_exec so no real subprocess is launched.
The patch raises immediately, causing _agent_loop to enter its retry sleep —
which keeps the Task alive (not done).
"""
import asyncio
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

import app.agent_runner as agent_runner_module
from app.agent_runner import start_agent_server


def _make_failing_subprocess():
    """Return a mock subprocess that exits with a non-zero code immediately."""
    proc = MagicMock()
    proc.pid = 99999
    proc.returncode = 1
    proc.wait = AsyncMock(return_value=1)
    proc.terminate = MagicMock()
    proc.kill = MagicMock()
    return proc


@pytest.mark.asyncio
async def test_start_agent_server_returns_task():
    """start_agent_server() must return an asyncio.Task without raising."""
    with patch(
        "app.agent_runner.asyncio.create_subprocess_exec",
        return_value=_make_failing_subprocess(),
    ):
        task = await start_agent_server()

    assert isinstance(task, asyncio.Task), "start_agent_server() must return an asyncio.Task"

    # Clean up: cancel and drain
    task.cancel()
    await asyncio.gather(task, return_exceptions=True)


@pytest.mark.asyncio
async def test_task_not_done_immediately_after_creation():
    """The returned task must still be running immediately after creation.

    The mock subprocess exits with code 1, so _agent_loop catches the error
    and sleeps for 5 s — the task is alive (not done) at that point.
    """
    with patch(
        "app.agent_runner.asyncio.create_subprocess_exec",
        return_value=_make_failing_subprocess(),
    ):
        task = await start_agent_server()
        # Yield one iteration so _agent_loop can enter its except/sleep branch.
        await asyncio.sleep(0)

    assert not task.done(), "Task must still be running (in retry sleep), not done"

    task.cancel()
    await asyncio.gather(task, return_exceptions=True)
