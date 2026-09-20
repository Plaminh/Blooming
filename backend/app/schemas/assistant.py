from datetime import date, datetime
from typing import Literal

from pydantic import BaseModel, Field

from app.schemas.drafts import RoadmapDraft, ChatTodayDraft, TodayDraft

class ChatTurn(BaseModel):
    role: Literal["user", "assistant"]
    content: str = Field(min_length=1, max_length=4000)


class ChatRequest(BaseModel):
    message: str = Field(min_length=1, max_length=4000)
    history: list[ChatTurn] = Field(default_factory=list, max_length=20)


class ChatResponse(BaseModel):
    reply: str = Field(min_length=1)
    draft: RoadmapDraft | ChatTodayDraft | TodayDraft | None = None
