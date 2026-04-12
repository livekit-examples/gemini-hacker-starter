import asyncio
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

import app.agent_runner as agent_runner
from app.routers import config, connection, demos, health, voices

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(_: FastAPI):
    _task: asyncio.Task | None = None
    try:
        _task = await agent_runner.start_agent_server()
        logger.info("Agent server background task started")
    except Exception:
        logger.exception(
            "Failed to start agent server — API will continue without agent"
        )

    yield

    if _task is not None:
        _task.cancel()
        try:
            await _task
        except (asyncio.CancelledError, Exception):
            pass
        logger.info("Agent server task stopped")


app = FastAPI(
    title="Exodia Backend",
    version="0.1.0",
    description="Exodia Multimodal AI Demo Platform — FastAPI backend",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router)
app.include_router(connection.router)
app.include_router(config.router)
app.include_router(demos.router)
app.include_router(voices.router)
