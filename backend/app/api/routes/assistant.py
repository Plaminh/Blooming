from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import CurrentUser, get_db_session
from app.core.config import settings
from app.core.rate_limit import SlidingWindowRateLimiter
from app.schemas.assistant import ChatRequest, ChatResponse
from app.services.assistant_service import chat
from app.db.models.users import UserSettings

router = APIRouter(prefix="/assistant", tags=["assistant"])

chat_rate_limiter = SlidingWindowRateLimiter(limit=settings.AI_CHAT_RATE_LIMIT_PER_MIN)

@router.post("/chat", response_model=ChatResponse)
async def assistant_chat(request: ChatRequest, current_user: CurrentUser, session: AsyncSession = Depends(get_db_session)) -> ChatResponse:
    if not chat_rate_limiter.is_allowed(str(current_user.id)):
        raise HTTPException(status_code=429, detail="rate_limit")

    stmt = select(UserSettings.timezone).where(UserSettings.user_id == current_user.id)
    result = await session.execute(stmt)
    timezone = result.scalar_one_or_none() or "UTC"

    return await chat(request, timezone=timezone)
