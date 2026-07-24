from datetime import datetime, timezone
from enum import Enum
from uuid import uuid4

from pydantic import BaseModel, Field


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


class Severity(str, Enum):
    low = "low"
    medium = "medium"
    high = "high"
    critical = "critical"


class ChatRequest(BaseModel):
    message: str
    session_id: str | None = None


class ChatResponse(BaseModel):
    session_id: str
    reply: str
    timestamp: datetime = Field(default_factory=utcnow)


class DiagnoseRequest(BaseModel):
    source: str = Field(..., description="Where this signal came from, e.g. 'nginx', 'k8s-pod', 'postgres'")
    logs: str = Field(..., description="Raw log or metric snippet to analyze")


class DiagnoseResponse(BaseModel):
    incident_id: str = Field(default_factory=lambda: str(uuid4()))
    severity: Severity
    root_cause: str
    recommended_actions: list[str]
    timestamp: datetime = Field(default_factory=utcnow)


class IncidentSummary(BaseModel):
    incident_id: str
    source: str
    severity: Severity
    root_cause: str
    timestamp: datetime
