"""Pure, validated edits for uncommitted assistant drafts."""

from copy import deepcopy
from datetime import date, datetime
from typing import Literal
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from app.schemas.drafts import AvailabilityWindowDraft, RoadmapDraft, TaskDraft, TodayDraft
from pydantic import BaseModel, Field, model_validator


class PatchOp(BaseModel):
    op: Literal["add_task", "update_task", "remove_task", "scale_durations", "split_task", "update_window", "set_windows", "set_plan_date"]
    task_id: str | None = None
    task: TaskDraft | None = None
    duration_min: int | None = Field(default=None, ge=5, le=480)
    factor: float | None = Field(default=None, ge=0.1, le=4)
    split_minutes: int | None = Field(default=None, ge=5, le=475)
    windows: list[AvailabilityWindowDraft] | None = Field(default=None, max_length=8)
    plan_date: date | None = None
    title: str | None = Field(default=None, min_length=1, max_length=200)
    importance: Literal["CORE", "OPTIONAL"] | None = None
    priority: Literal["LOW", "MEDIUM", "HIGH", "URGENT"] | None = None
    category: Literal["Learning", "Work", "Personal"] | None = None
    break_after_min: int | None = Field(default=None, ge=0, le=60)
    window_index: int | None = Field(default=None, ge=0)
    start: str | None = Field(default=None, pattern=r"^([01]\d|2[0-3]):[0-5]\d$")
    end: str | None = Field(default=None, pattern=r"^([01]\d|2[0-3]):[0-5]\d$")
    fixed_start: str | None = Field(default=None, pattern=r"^([01]\d|2[0-3]):[0-5]\d$")
    fixed_end: str | None = Field(default=None, pattern=r"^([01]\d|2[0-3]):[0-5]\d$")
    deadline: str | None = Field(default=None, pattern=r"^([01]\d|2[0-3]):[0-5]\d$")
    scheduling_type: Literal["FLEXIBLE", "FIXED"] | None = None

    @model_validator(mode="after")
    def validate_target(self) -> "PatchOp":
        if self.op in {"update_task", "remove_task", "split_task"} and not self.task_id:
            raise ValueError("task_id is required")
        if self.op == "add_task" and self.task is None:
            raise ValueError("add_task requires task")
        if self.op == "scale_durations" and self.factor is None:
            raise ValueError("scale_durations requires factor")
        if self.op == "split_task" and self.split_minutes is None:
            raise ValueError("split_task requires split_minutes")
        if self.op == "set_windows" and self.windows is None:
            raise ValueError("set_windows requires windows")
        if self.op == "set_plan_date" and self.plan_date is None:
            raise ValueError("set_plan_date requires plan_date")
        if self.op == "update_task" and not self.model_fields_set.intersection({
            "duration_min", "title", "importance", "priority", "category", "break_after_min",
            "fixed_start", "fixed_end", "deadline", "scheduling_type"
        }):
            raise ValueError("update_task requires a changed field")
        if self.op == "update_window" and (
            self.window_index is None
            or self.start is None
            or self.end is None
            or self.start >= self.end
        ):
            raise ValueError("update_window requires a valid window")
        return self


class ApplyPatchRequest(BaseModel):
    draft: TodayDraft | RoadmapDraft
    ops: list[PatchOp] = Field(min_length=1, max_length=10)


class ApplyPatchResponse(BaseModel):
    draft: TodayDraft | RoadmapDraft
    preview: dict | None = None


def apply_patch(
    draft: TodayDraft | RoadmapDraft, ops: list[PatchOp]
) -> TodayDraft | RoadmapDraft:
    if not isinstance(draft, TodayDraft):
        raise ValueError("Roadmap patch operations are not supported")
    result = deepcopy(draft)
    try:
        draft_timezone = ZoneInfo(result.timezone)
    except ZoneInfoNotFoundError as exc:
        raise ValueError(f"Unknown draft timezone: {result.timezone}") from exc
    for op in ops:
        if op.op == "set_plan_date":
            if op.plan_date is None or op.plan_date < date.today():
                raise ValueError("Plan date cannot be in the past")
            for item in result.tasks:
                for field_name in ("deadline", "fixedStart", "fixedEnd"):
                    old_value = getattr(item, field_name)
                    if old_value is not None:
                        setattr(item, field_name, old_value.replace(year=op.plan_date.year,
                            month=op.plan_date.month, day=op.plan_date.day))
            result.planDate = op.plan_date
            continue
        if op.op == "set_windows":
            result.windows = op.windows or []
            continue
        if op.op == "add_task":
            if op.task is None or any(item.id == op.task.id for item in result.tasks):
                raise ValueError("Task ID already exists")
            result.tasks.append(deepcopy(op.task))
            continue
        if op.op == "scale_durations":
            if op.task_id is not None and not any(item.id == op.task_id for item in result.tasks):
                raise ValueError("Task not found")
            for item in result.tasks:
                if op.task_id is None or item.id == op.task_id:
                    item.durationMin = min(480, max(5, round(item.durationMin * (op.factor or 1) / 5) * 5))
                    item.estimateSource = "USER"
            continue
        if op.op == "update_window":
            if op.window_index is None or op.window_index >= len(result.windows):
                raise ValueError("Window not found")
            result.windows[op.window_index].start = op.start  # type: ignore[assignment]
            result.windows[op.window_index].end = op.end  # type: ignore[assignment]
            continue
        task = next((item for item in result.tasks if item.id == op.task_id), None)
        if task is None:
            raise ValueError("Task not found")
        if op.op == "remove_task":
            if any(task.id in item.dependencies for item in result.tasks):
                raise ValueError("Cannot remove a task required by another task")
            result.tasks = [item for item in result.tasks if item.id != task.id]
        elif op.op == "split_task":
            first = op.split_minutes or 0
            if not 5 <= first <= task.durationMin - 5:
                raise ValueError("Split must leave at least five minutes per part")
            second_id = f"{task.id}-2"
            if any(item.id == second_id for item in result.tasks):
                raise ValueError("Split task ID already exists")
            remainder = deepcopy(task)
            remainder.id = second_id
            original_title = task.title
            task.title = f"{original_title} (part 1)"[:200]
            remainder.title = f"{original_title} (part 2)"[:200]
            remainder.durationMin = task.durationMin - first
            remainder.dependencies = [task.id]
            task.durationMin = first
            task.estimateSource = "USER"
            remainder.estimateSource = "USER"
            result.tasks.insert(result.tasks.index(task) + 1, remainder)
        else:
            if "duration_min" in op.model_fields_set:
                task.durationMin = op.duration_min
                task.estimateSource = "USER"
            if "title" in op.model_fields_set and op.title is not None:
                task.title = op.title.strip()
            if "importance" in op.model_fields_set:
                task.importance = op.importance
            if "priority" in op.model_fields_set:
                task.priority = op.priority
            if "category" in op.model_fields_set:
                task.category = op.category
            if "break_after_min" in op.model_fields_set:
                task.breakAfterMin = op.break_after_min
            if "scheduling_type" in op.model_fields_set:
                task.schedulingType = op.scheduling_type
            
            for attr, field in [("fixedStart", "fixed_start"), ("fixedEnd", "fixed_end"), ("deadline", "deadline")]:
                if field in op.model_fields_set:
                    val = getattr(op, field)
                    if val is None:
                        setattr(task, attr, None)
                    else:
                        parsed_time = datetime.strptime(val, "%H:%M").time()
                        setattr(task, attr, datetime.combine(result.planDate, parsed_time, draft_timezone))
    validated = TodayDraft.model_validate(result.model_dump())
    from app.ai.validators import check_today
    issues = check_today(validated)
    if issues:
        raise ValueError(", ".join(issues))
    return validated
