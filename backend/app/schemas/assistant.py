from datetime import datetime
from typing import Literal, Any, Annotated

from pydantic import BaseModel, Field, field_validator, model_validator

from app.schemas.patches import PatchOp
from app.schemas.drafts import RoadmapDraft, TodayDraft
from app.schemas.today import TodayPreviewResponse


class ChatTurn(BaseModel):
    role: Literal["user", "assistant"]
    content: str = Field(min_length=1, max_length=4000)


class GardenContext(BaseModel):
    stage: str
    inventory: dict[str, int] = Field(default_factory=dict)
    active_plant: str | None = None


class ChatRequest(BaseModel):
    message: str = Field(min_length=1, max_length=2000)
    session_id: str | None = None
    history: list[ChatTurn] = Field(default_factory=list, max_length=20)
    current_draft: Annotated[RoadmapDraft | TodayDraft, Field(discriminator="type")] | None = None
    garden: GardenContext | None = None
    tz: str = "UTC"

    @field_validator("message", mode="before")
    @classmethod
    def check_not_empty_after_strip(cls, value: Any) -> Any:
        if isinstance(value, str):
            value = value.strip()
            if not value:
                raise ValueError("message cannot be empty or whitespace only")
        return value


class QuickReply(BaseModel):
    label: str = Field(min_length=1, max_length=80)
    action: str | None = None
    send_text: str | None = Field(default=None, min_length=1, max_length=4000)
    patch: list[PatchOp] | None = Field(default=None, min_length=1, max_length=10)

    @field_validator("label", mode="before")
    @classmethod
    def truncate_label(cls, value: Any) -> Any:
        if isinstance(value, str) and len(value) > 80:
            return value[:80]
        return value

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
    draft: Annotated[RoadmapDraft | TodayDraft, Field(discriminator="type")] | None = None
    preview: TodayPreviewResponse | None = None
    goal_created: dict | None = None
    suggestions: list[QuickReply] = Field(default_factory=list, max_length=4)
    assumptions: list[Assumption] = Field(default_factory=list)
    question: str | None = None

    @field_validator("suggestions", mode="before")
    @classmethod
    def truncate_suggestions(cls, value: list | None) -> list | None:
        if isinstance(value, list) and len(value) > 4:
            return value[:4]
        return value


class SessionMessage(BaseModel):
    role: Literal["user", "assistant"]
    content: str
    structured_payload: dict | None = None
    created_at: datetime


class SessionResponse(BaseModel):
    session_id: str
    status: str
    messages: list[SessionMessage]
