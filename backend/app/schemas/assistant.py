from datetime import date, datetime
from typing import Literal

from pydantic import BaseModel, Field

from app.schemas.drafts import RoadmapDraft, TodayDraft

class ChatTurn(BaseModel):
    role: Literal["user", "assistant"]
    content: str = Field(min_length=1, max_length=4000)

class GardenContext(BaseModel):
    stage: str
    inventory: dict[str, int] = Field(default_factory=dict)
    active_plant: str | None = None

class ChatRequest(BaseModel):
    message: str = Field(min_length=1, max_length=4000)
    session_id: str | None = None
    history: list[ChatTurn] = Field(default_factory=list, max_length=20)
    current_draft: RoadmapDraft | TodayDraft | None = None
    garden: GardenContext | None = None
    tz: str = "UTC"

class ChatResponse(BaseModel):
    reply: str = Field(min_length=1)
    session_id: str | None = None
    intent: str | None = None
    tier: str = "PARSER"
    degraded: str | None = None
    draft: RoadmapDraft | TodayDraft | None = None
    preview: dict | None = None
    goal_created: dict | None = None
