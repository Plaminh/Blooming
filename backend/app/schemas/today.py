from datetime import date, datetime
from typing import Any, Literal
from uuid import UUID

from pydantic import BaseModel, Field, field_validator

from app.schemas.planning import TaskCategory
from app.schemas.drafts import TodayDraft


class TodayBlock(BaseModel):
    id: UUID
    block_type: Literal["TASK", "BREAK", "BUFFER", "FIXED_EVENT"]
    task_id: UUID | None = None
    title: str | None = None
    description: str | None = None
    category: TaskCategory | None = None
    estimated_duration_minutes: int | None = None
    importance: Literal["CORE", "OPTIONAL"] | None = None
    preferred_break_duration_minutes: int | None = None
    source: str | None = None
    planned_start_at: datetime
    planned_end_at: datetime
    position: int
    status: str
    is_locked: bool
    draft_task_id: str | None = None


class UnscheduledReason(BaseModel):
    code: str
    task_id: UUID
    dependency_id: UUID | None = None


class UnscheduledTaskInfo(BaseModel):
    draft_task_id: str | None = None
    title: str | None = None
    reason: str | None = None

class TodayResponse(BaseModel):
    plan_date: date
    status: str
    timezone: str = "UTC"
    unscheduled_tasks: list[UUID] | list[UnscheduledTaskInfo] = Field(default_factory=list)
    reasons: list[UnscheduledReason] = Field(default_factory=list)
    reality_check: str | None = None
    blocks: list[TodayBlock] = Field(default_factory=list)


class TodayNoPlanResponse(BaseModel):
    timezone: str = "UTC"
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

class TodayPreviewRequest(BaseModel):
    draft: TodayDraft



class TodayPreviewResponse(BaseModel):
    plan_date: date
    status: Literal["PREVIEW"] = "PREVIEW"
    timezone: str
    preview_token: str
    reality_check: str | None = None
    blocks: list[TodayBlock] = Field(default_factory=list)
    unscheduled_tasks: list[UnscheduledTaskInfo] = Field(default_factory=list)
    reasons: list[dict[str, Any]] = Field(default_factory=list)

class TodaySaveRequest(BaseModel):
    preview_token: str
    draft: TodayDraft
    session_id: UUID | None = None
    replace_existing: bool = False
