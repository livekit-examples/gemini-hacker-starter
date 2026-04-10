"""Tests that verify the FastAPI lifespan starts without exceptions.

start_agent_server is patched so no real LiveKit connection is attempted.
"""
import asyncio
from unittest.mock import patch

import app.agent_runner as agent_runner_module
from app.main import app
from fastapi.testclient import TestClient


def _make_fake_start():
    """Return an async callable that yields a never-ending background task."""

    async def fake_start_agent_server() -> asyncio.Task:
        return asyncio.create_task(asyncio.sleep(999))

    return fake_start_agent_server


def test_app_starts_with_lifespan():
    """FastAPI must start (and stop) via TestClient without raising."""
    with patch.object(
        agent_runner_module,
        "start_agent_server",
        side_effect=_make_fake_start(),
    ):
        with TestClient(app) as client:
            response = client.get("/api/health")
            assert response.status_code == 200


def test_app_startup_survives_agent_failure():
    """FastAPI must still start even when start_agent_server raises."""

    async def failing_start():
        raise RuntimeError("Intentional agent startup failure")

    with patch.object(
        agent_runner_module,
        "start_agent_server",
        side_effect=failing_start,
    ):
        with TestClient(app) as client:
            response = client.get("/api/health")
            assert response.status_code == 200
