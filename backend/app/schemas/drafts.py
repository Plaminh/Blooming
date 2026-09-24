from datetime import date, datetime
from typing import Literal

from pydantic import BaseModel, Field, model_validator


class MilestoneDraft(BaseModel):
    id: str | None = None
    title: str = Field(min_length=1)
    targetDate: date
    expectedOutcome: str | None = None


class RoadmapDraft(BaseModel):
    type: Literal["roadmap"]
    goalTitle: str = Field(min_length=1)
    goalDescription: str = ""
    targetDate: date
    milestones: list[MilestoneDraft] = Field(default_factory=list)

    @model_validator(mode="after")
    def validate_roadmap(self) -> "RoadmapDraft":
        if len(self.milestones) == 0:
            raise ValueError("Roadmap must have at least 1 milestone")
        if len(self.milestones) > 12:
            raise ValueError("Roadmap must have at most 12 milestones")

        if self.milestones[-1].targetDate > self.targetDate:
            raise ValueError(
                "Milestone target date cannot be after roadmap target date"
            )

        if any(
            current.targetDate > following.targetDate
            for current, following in zip(self.milestones, self.milestones[1:])
        ):
            raise ValueError("Milestone target dates must be ordered")

        return self


class AvailabilityWindowDraft(BaseModel):
    start: str = Field(pattern=r"^([01][0-9]|2[0-3]):[0-5][0-9]$")
    end: str = Field(pattern=r"^([01][0-9]|2[0-3]):[0-5][0-9]$")

    @model_validator(mode="after")
    def validate_window(self) -> "AvailabilityWindowDraft":
        if self.start >= self.end:
            raise ValueError("Window start time must be before end time")
        return self


class TaskDraft(BaseModel):
    id: str = Field(min_length=1)
    title: str = Field(min_length=1)
    durationMin: int = Field(ge=5, le=480)
    priority: Literal["URGENT", "HIGH", "MEDIUM", "LOW"] = "MEDIUM"
    importance: Literal["CORE", "OPTIONAL"] = "CORE"
    category: str | None = None
    estimateSource: Literal["USER", "RULE", "AI", "HISTORY"] = "USER"
    breakAfterMin: int | None = Field(None, ge=0, le=60)
    deadline: datetime | None = None
    schedulingType: Literal["FLEXIBLE", "FIXED"] = "FLEXIBLE"
    fixedStart: datetime | None = None
    fixedEnd: datetime | None = None
    dependencies: list[str] = Field(default_factory=list)
    splittable: bool = False


class DeferredTaskDraft(BaseModel):
    task: TaskDraft
    targetDate: date


class TodayDraft(BaseModel):
    @model_validator(mode="after")
    def validate_deferred_tasks(self) -> "TodayDraft":
        if self.deferred_tasks:
            seen_ids = {t.id for t in self.tasks}
            def_ids = set()
            for dt in self.deferred_tasks:
                if dt.targetDate < self.planDate:
                    raise ValueError(
                        f"Deferred task '{dt.task.title}' cannot target a date before the plan date."
                    )
                if dt.task.id in seen_ids or dt.task.id in def_ids:
                    raise ValueError(
                        f"Deferred task ID '{dt.task.id}' is duplicated or overlaps with today tasks."
                    )
                def_ids.add(dt.task.id)

            allowed_ids = seen_ids | def_ids
            for dt in self.deferred_tasks:
                for dep in dt.task.dependencies:
                    if dep not in allowed_ids:
                        raise ValueError(
                            f"Dangling dependency '{dep}' in deferred task '{dt.task.id}'."
                        )
                    if dep == dt.task.id:
                        raise ValueError(
                            f"Self-dependency '{dep}' in deferred task '{dt.task.id}'."
                        )
        return self

    type: Literal["today"] = "today"
    planDate: date
    timezone: str = "UTC"
    windows: list[AvailabilityWindowDraft] = Field(default_factory=list)
    tasks: list[TaskDraft] = Field(default_factory=list)
    deferred_tasks: list[DeferredTaskDraft] = Field(default_factory=list)


def clean_availability_windows(
    windows: list[AvailabilityWindowDraft], current_time: datetime
) -> list[AvailabilityWindowDraft]:
    current_hm = current_time.strftime("%H:%M")
    cleaned = []
    for w in windows:
        if w.end <= current_hm:
            continue
        start = w.start if w.start >= current_hm else current_hm
        cleaned.append(AvailabilityWindowDraft(start=start, end=w.end))
    return cleaned
