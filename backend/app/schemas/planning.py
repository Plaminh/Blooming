import zoneinfo
from datetime import date, datetime
from typing import Any, Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

TaskCategory = Literal["Learning", "Work", "Personal"]


class TaskBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    description: str | None = None
    category: TaskCategory | None = None
    estimated_duration_minutes: int = Field(..., gt=0, le=10080)
    priority: Literal["LOW", "MEDIUM", "HIGH", "URGENT"] = Field(default="MEDIUM")
    scheduling_type: Literal["FLEXIBLE", "FIXED"] = Field(default="FLEXIBLE")
    is_splittable: bool = Field(default=False)
    min_split_duration_minutes: int | None = Field(default=None, gt=0)
    preferred_break_duration_minutes: int | None = Field(default=None, gt=0)
    fixed_start_at: datetime | None = None
    fixed_end_at: datetime | None = None
    deadline_at: datetime | None = None

    @field_validator('title')
    def validate_title(cls, v):
        if not v.strip():
            raise ValueError("Title must not be empty or whitespace only")
        return v.strip()

    @field_validator('fixed_start_at', 'fixed_end_at', 'deadline_at')
    def validate_timezone_aware(cls, v):
        if v is not None and v.tzinfo is None:
            raise ValueError("Datetime must be timezone-aware")
        return v

    @model_validator(mode="after")
    def validate_split_duration(self) -> "TaskBase":
        if (
            self.min_split_duration_minutes is not None
            and self.min_split_duration_minutes > self.estimated_duration_minutes
        ):
            raise ValueError(
                "min_split_duration_minutes cannot exceed estimated_duration_minutes"
            )
        return self


class TaskCreate(TaskBase):
    dependencies: list[UUID] = Field(default_factory=list)

    @model_validator(mode='after')
    def validate_fixed_window(self) -> 'TaskCreate':
        if self.scheduling_type == 'FIXED':
            if not self.fixed_start_at or not self.fixed_end_at:
                raise ValueError("FIXED tasks require fixed_start_at and fixed_end_at")
            if self.fixed_end_at <= self.fixed_start_at:
                raise ValueError("fixed_end_at must be strictly greater than fixed_start_at")
        else:
            if self.fixed_start_at or self.fixed_end_at:
                raise ValueError("FLEXIBLE tasks cannot have fixed start/end times")
        return self


class TaskUpdate(BaseModel):
    title: str | None = Field(None, min_length=1, max_length=200)
    description: str | None = None
    category: TaskCategory | None = None
    estimated_duration_minutes: int | None = Field(None, gt=0, le=10080)
    priority: Literal["LOW", "MEDIUM", "HIGH", "URGENT"] | None = None
    scheduling_type: Literal["FLEXIBLE", "FIXED"] | None = None
    is_splittable: bool | None = None
    min_split_duration_minutes: int | None = Field(None, gt=0)
    preferred_break_duration_minutes: int | None = Field(None, gt=0)
    fixed_start_at: datetime | None = None
    fixed_end_at: datetime | None = None
    deadline_at: datetime | None = None
    dependencies: list[UUID] | None = None

    @field_validator('title')
    def validate_title(cls, v):
        if v is not None and not v.strip():
            raise ValueError("Title must not be empty or whitespace only")
        return v.strip() if v is not None else v

    @field_validator('fixed_start_at', 'fixed_end_at', 'deadline_at')
    def validate_timezone_aware(cls, v):
        if v is not None and v.tzinfo is None:
            raise ValueError("Datetime must be timezone-aware")
        return v


class TaskDependencyResponse(BaseModel):
    task_id: UUID
    depends_on_task_id: UUID

    model_config = ConfigDict(from_attributes=True)


class TaskResponse(TaskBase):
    id: UUID
    user_id: UUID
    status: Literal[
        "DRAFT", "PENDING", "IN_PROGRESS", "COMPLETED", "SKIPPED", "CANCELLED"
    ]
    created_at: datetime
    updated_at: datetime
    dependencies: list[TaskDependencyResponse] = Field(default_factory=list)

    model_config = ConfigDict(from_attributes=True)


class AvailabilityWindowInput(BaseModel):
    start_at: datetime
    end_at: datetime


class TimelineGenerateRequest(BaseModel):
    plan_date: date
    timezone_snapshot: str
    task_ids: list[UUID]
    availability_windows: list[AvailabilityWindowInput] = Field(..., min_length=1)

    @field_validator("timezone_snapshot")
    def validate_timezone(cls, v):
        try:
            zoneinfo.ZoneInfo(v)
        except (zoneinfo.ZoneInfoNotFoundError, ValueError):
            raise ValueError("Invalid timezone name")
        return v

    @field_validator('availability_windows')
    def validate_windows(cls, windows):
        for w in windows:
            if w.end_at <= w.start_at:
                raise ValueError("Availability window start_at must be before end_at")
            if w.start_at.tzinfo is None or w.end_at.tzinfo is None:
                raise ValueError("Availability window datetimes must be timezone-aware")
        return windows


class PlanBlockSchema(BaseModel):
    block_type: Literal["TASK", "BREAK", "BUFFER", "FIXED_EVENT"]
    task_id: UUID | None = None
    title: str | None = None
    planned_start_at: datetime
    planned_end_at: datetime
    position: int
    status: str = "PLANNED"


class TimelineDraftResponse(BaseModel):
    draft_id: UUID
    reality_check: Literal["COMFORTABLE", "TIGHT", "OVERLOADED"]
    reality_check_reasons: list[Any]
    blocks: list[PlanBlockSchema]
    unscheduled_tasks: list[UUID]


class SaveDailyPlanRequest(BaseModel):
    draft_id: UUID
    replace_existing: bool = False


class DailyPlanResponse(BaseModel):
    id: UUID
    user_id: UUID
    plan_date: date
    status: str
    reality_check: str | None = None
    timezone_snapshot: str
    blocks: list[PlanBlockSchema] = Field(default_factory=list)
