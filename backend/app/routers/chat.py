from uuid import uuid4

from fastapi import APIRouter

from app.models.schemas import ChatRequest, ChatResponse
from app.services import agent_service

router = APIRouter(prefix="/chat", tags=["chat"])


@router.post("", response_model=ChatResponse)
async def send_message(request: ChatRequest):
    reply = await agent_service.chat(request.message)
    new_deployment = await agent_service.create_new_deployment(request.message)
    return ChatResponse(session_id=request.session_id or str(uuid4()), reply=reply)
