from pydantic import BaseModel


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
    demos: list[DemoSummary]
