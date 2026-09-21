from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field, model_validator

from app.ai.patches import PatchOp
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


class QuickReply(BaseModel):
    label: str = Field(min_length=1, max_length=80)
    action: str | None = None
    send_text: str | None = Field(default=None, min_length=1, max_length=4000)
    patch: list[PatchOp] | None = Field(default=None, min_length=1, max_length=10)

    @model_validator(mode="after")
    def one_command(self) -> "QuickReply":
        if sum(value is not None for value in (self.action, self.send_text, self.patch)) != 1:
            raise ValueError("Quick reply needs exactly one command")
        return self


class Assumption(BaseModel):
    id: str
    kind: str
    text: str
    task_id: str | None = None


class ChatResponse(BaseModel):
    reply: str = Field(min_length=1)
    session_id: str | None = None
    intent: str | None = None
    tier: str = "PARSER"
    degraded: str | None = None
    draft: RoadmapDraft | TodayDraft | None = None
    preview: dict | None = None
    goal_created: dict | None = None
    suggestions: list[QuickReply] = Field(default_factory=list, max_length=3)
    assumptions: list[Assumption] = Field(default_factory=list)
    question: str | None = None


class SessionMessage(BaseModel):
    role: Literal["user", "assistant"]
    content: str
    structured_payload: dict | None = None
    created_at: datetime


class SessionResponse(BaseModel):
    session_id: str
    status: str
    messages: list[SessionMessage]
