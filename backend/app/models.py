from pydantic import BaseModel

from app.demo_configs import DemoConfig  # noqa: F401 — re-exported for routers


class HealthResponse(BaseModel):
    status: str
    version: str


class ConnectionDetailsResponse(BaseModel):
    serverUrl: str
    roomName: str
    participantToken: str
    participantName: str


class AppConfigResponse(BaseModel):
    agentName: str
    industry: str
    language: str
    accent: str
    title: str


class DemoSummary(BaseModel):
    slug: str
    name: str


class DemosResponse(BaseModel):
    demos: list[DemoConfig]


class DemoConfigResponse(DemoConfig):
    pass


class VoicesResponse(BaseModel):
    voices: list[str]
