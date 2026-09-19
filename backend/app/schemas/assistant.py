from datetime import date
from typing import Literal

from pydantic import BaseModel, Field


class ChatTurn(BaseModel):
    role: Literal["user", "assistant"]
    content: str = Field(min_length=1, max_length=4000)


class ChatRequest(BaseModel):
    message: str = Field(min_length=1, max_length=4000)
    history: list[ChatTurn] = Field(default_factory=list, max_length=20)


class MilestoneDraft(BaseModel):
    title: str = Field(min_length=1)
    targetDate: date


class RoadmapDraft(BaseModel):
    type: Literal["roadmap"]
    goalTitle: str = Field(min_length=1)
    goalDescription: str = ""
    targetDate: date
    milestones: list[MilestoneDraft] = Field(default_factory=list)


class AvailabilityDraft(BaseModel):
    start: str
    end: str
    totalHours: float


class TaskDraft(BaseModel):
    title: str = Field(min_length=1)
    durationMin: int = Field(ge=1, le=1440)
    priority: Literal["Core", "Optional"] = "Core"


class TodayDraft(BaseModel):
    type: Literal["today"]
    availability: AvailabilityDraft
    tasks: list[TaskDraft] = Field(default_factory=list)


class ChatResponse(BaseModel):
    reply: str = Field(min_length=1)
    draft: RoadmapDraft | TodayDraft | None = None
