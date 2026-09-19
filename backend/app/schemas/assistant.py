from datetime import date, datetime
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


class ChatTaskDraft(BaseModel):
    title: str = Field(min_length=1)
    durationMin: int = Field(ge=1, le=1440)
    priority: Literal["Core", "Optional"] = "Core"


class ChatTodayDraft(BaseModel):
    type: Literal["today"]
    availability: AvailabilityDraft
    tasks: list[ChatTaskDraft] = Field(default_factory=list)


class AvailabilityWindowDraft(BaseModel):
    start: str = Field(pattern=r"^([01][0-9]|2[0-3]):[0-5][0-9]$")
    end: str = Field(pattern=r"^([01][0-9]|2[0-3]):[0-5][0-9]$")

class TaskDraft(BaseModel):
    id: str = Field(min_length=1)
    title: str = Field(min_length=1)
    durationMin: int = Field(ge=1, le=1440)
    priority: Literal["URGENT", "HIGH", "MEDIUM", "LOW"] = "MEDIUM"
    deadline: datetime | None = None
    schedulingType: Literal["FLEXIBLE", "FIXED"] = "FLEXIBLE"
    fixedStart: datetime | None = None
    fixedEnd: datetime | None = None
    dependencies: list[str] = Field(default_factory=list)
    splittable: bool = False

class TodayDraft(BaseModel):
    type: Literal["today"] = "today"
    planDate: date
    timezone: str = "UTC"
    windows: list[AvailabilityWindowDraft] = Field(default_factory=list)
    tasks: list[TaskDraft] = Field(default_factory=list)


class ChatResponse(BaseModel):
    reply: str = Field(min_length=1)
    draft: RoadmapDraft | ChatTodayDraft | TodayDraft | None = None
