from datetime import date, datetime
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, Field, field_validator

from app.schemas.planning import TaskCategory


class TodayBlock(BaseModel):
    id: UUID
    block_type: Literal["TASK", "BREAK", "BUFFER", "FIXED_EVENT"]
    task_id: UUID | None = None
    title: str | None = None
    description: str | None = None
    category: TaskCategory | None = None
    estimated_duration_minutes: int | None = None
    planned_start_at: datetime
    planned_end_at: datetime
    position: int
    status: str
    is_locked: bool


class TodayResponse(BaseModel):
    plan_date: date
    status: str
    reality_check: str | None = None
    blocks: list[TodayBlock] = Field(default_factory=list)


class TodayNoPlanResponse(BaseModel):
    plan_date: date
    status: Literal["NO_PLAN"] = "NO_PLAN"


class TodayTaskEdit(BaseModel):
    title: str | None = Field(None, min_length=1, max_length=200)
    description: str | None = None
    category: TaskCategory | None = None
    estimated_duration_minutes: int | None = Field(None, gt=0, le=10080)

    @field_validator("title")
    @classmethod
    def validate_title(cls, value: str | None) -> str | None:
        if value is not None and not value.strip():
            raise ValueError("Title must not be empty or whitespace only")
        return value.strip() if value else value


class TodayTaskStatusUpdate(BaseModel):
    status: Literal["PENDING", "IN_PROGRESS", "COMPLETED", "SKIPPED", "CANCELLED"]
