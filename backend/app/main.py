from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers import config, connection, demos, health

app = FastAPI(
    title="Exodia Backend",
    version="0.1.0",
    description="Exodia Multimodal AI Demo Platform — FastAPI backend",
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
