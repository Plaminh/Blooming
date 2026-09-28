from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import CurrentUser, get_db_session
from app.schemas.assistant import ChatRequest, ChatResponse, SessionResponse
from app.schemas.patches import ApplyPatchRequest, ApplyPatchResponse

from app.services.assistant_orchestrator import (
    process_chat,
    get_latest_session,
    get_session,
    process_apply_patch,
    process_action,
    process_event,
)

router = APIRouter(prefix="/assistant", tags=["assistant"])


@router.post("/chat", response_model=ChatResponse)
async def assistant_chat(
    request: ChatRequest,
    current_user: CurrentUser,
    session: AsyncSession = Depends(get_db_session),
) -> ChatResponse:
    return await process_chat(request, session, current_user.id)


@router.get("/sessions/latest", response_model=SessionResponse)
async def get_latest_assistant_session(
    current_user: CurrentUser,
    session: AsyncSession = Depends(get_db_session),
) -> SessionResponse:
    return await get_latest_session(session, current_user.id)


@router.get("/sessions/{session_id}", response_model=SessionResponse)
async def get_assistant_session(
    session_id: UUID,
    current_user: CurrentUser,
    session: AsyncSession = Depends(get_db_session),
) -> SessionResponse:
    return await get_session(session, current_user.id, session_id)


@router.post("/apply-patch", response_model=ApplyPatchResponse)
async def apply_draft_patch(
    request: ApplyPatchRequest,
    current_user: CurrentUser,
    session: AsyncSession = Depends(get_db_session),
) -> ApplyPatchResponse:
    return await process_apply_patch(request, session, current_user.id)


@router.post("/actions/{name}")
async def assistant_action(
    name: str,
    current_user: CurrentUser,
    session: AsyncSession = Depends(get_db_session),
):
    return await process_action(name, session, current_user.id)


@router.post("/events")
async def assistant_event(
    body: dict,
    current_user: CurrentUser,
    session: AsyncSession = Depends(get_db_session),
):
    return await process_event(body, session, current_user.id)
