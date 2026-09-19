from fastapi import APIRouter

from app.api.deps import CurrentUser
from app.schemas.assistant import ChatRequest, ChatResponse
from app.services.assistant_service import chat

router = APIRouter(prefix="/assistant", tags=["assistant"])


@router.post("/chat", response_model=ChatResponse)
async def assistant_chat(request: ChatRequest, current_user: CurrentUser) -> ChatResponse:
    return await chat(request)
