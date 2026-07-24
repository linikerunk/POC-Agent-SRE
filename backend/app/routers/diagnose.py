from fastapi import APIRouter

from app.models.schemas import DiagnoseRequest, DiagnoseResponse, IncidentSummary
from app.services import agent_service

router = APIRouter(tags=["diagnose"])


@router.post("/diagnose", response_model=DiagnoseResponse)
def diagnose(request: DiagnoseRequest):
    return agent_service.diagnose(request.source, request.logs)


@router.get("/incidents", response_model=list[IncidentSummary])
def list_incidents():
    return agent_service.list_incidents()
