"""Pure, validated edits for uncommitted assistant drafts."""

from datetime import date
from typing import Annotated, Literal, Union

from app.schemas.drafts import (
    AvailabilityWindowDraft,
    RoadmapDraft,
    TaskDraft,
    TodayDraft,
)
from pydantic import BaseModel, Field, model_validator


class RemoveTaskOp(BaseModel):
    op: Literal["remove_task"]
    task_id: str


class MoveTaskToDateOp(BaseModel):
    op: Literal["move_task_to_date"]
    task_id: str
    target_date: str
    timezone: str | None = None


class RemoveDeferredTaskOp(BaseModel):
    """Drop a task the draft would save for a later day."""

    op: Literal["remove_deferred_task"]
    task_id: str


class UpdateWindowOp(BaseModel):
    op: Literal["update_window"]
    window_index: int = Field(ge=0)
    start: str | None = Field(default=None, pattern=r"^([01]\d|2[0-3]):[0-5]\d$")
    end: str | None = Field(default=None, pattern=r"^([01]\d|2[0-3]):[0-5]\d$")


class UpdateTaskOp(BaseModel):
    op: Literal["update_task"]
    task_id: str
    duration_min: int | None = Field(default=None, ge=5, le=480)
    title: str | None = Field(default=None, min_length=1, max_length=200)
    importance: Literal["CORE", "OPTIONAL"] | None = None
    priority: Literal["LOW", "MEDIUM", "HIGH", "URGENT"] | None = None
    category: Literal["Learning", "Work", "Personal"] | None = None
    break_after_min: int | None = Field(default=None, ge=0, le=60)
    splittable: bool | None = None
    fixed_start: str | None = Field(default=None, pattern=r"^([01]\d|2[0-3]):[0-5]\d$")
    fixed_end: str | None = Field(default=None, pattern=r"^([01]\d|2[0-3]):[0-5]\d$")
    deadline: str | None = Field(default=None, pattern=r"^([01]\d|2[0-3]):[0-5]\d$")
    scheduling_type: Literal["FLEXIBLE", "FIXED"] | None = None

    @model_validator(mode="after")
    def validate_update(self) -> "UpdateTaskOp":
        if (
            self.title is None
            and self.duration_min is None
            and self.priority is None
            and self.importance is None
            and self.category is None
            and self.splittable is None
            and self.break_after_min is None
            and self.fixed_start is None
            and self.fixed_end is None
            and self.deadline is None
            and self.scheduling_type is None
        ):
            raise ValueError("UpdateTaskOp must contain at least one changed field.")
        return self


class SplitTaskOp(BaseModel):
    op: Literal["split_task"]
    task_id: str
    split_minutes: int = Field(ge=5, le=475)


class AddTaskOp(BaseModel):
    op: Literal["add_task"]
    task: TaskDraft


class ScaleDurationsOp(BaseModel):
    op: Literal["scale_durations"]
    factor: float = Field(ge=0.1, le=4)
    task_id: str | None = None


class SetWindowsOp(BaseModel):
    op: Literal["set_windows"]
    windows: list[AvailabilityWindowDraft] = Field(max_length=8)


class SetPlanDateOp(BaseModel):
    op: Literal["set_plan_date"]
    plan_date: date


PatchOp = Annotated[
    Union[
        RemoveTaskOp,
        RemoveDeferredTaskOp,
        MoveTaskToDateOp,
        UpdateWindowOp,
        UpdateTaskOp,
        SplitTaskOp,
        AddTaskOp,
        ScaleDurationsOp,
        SetWindowsOp,
        SetPlanDateOp,
    ],
    Field(discriminator="op"),
]


class ApplyPatchRequest(BaseModel):
    draft: TodayDraft | RoadmapDraft
    ops: list[PatchOp] = Field(min_length=1, max_length=10)


class ApplyPatchResponse(BaseModel):
    draft: TodayDraft | RoadmapDraft
    preview: dict | None = None
