from datetime import date, datetime
from typing import Literal

from pydantic import BaseModel, Field, model_validator


class MilestoneDraft(BaseModel):
    title: str = Field(min_length=1)
    targetDate: date


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
        
        self.milestones.sort(key=lambda m: m.targetDate)

        if self.milestones[-1].targetDate > self.targetDate:
            raise ValueError("Milestone target date cannot be after roadmap target date")
            
        if self.targetDate < date.today():
            raise ValueError("Roadmap target date cannot be in the past")

        return self


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

    @model_validator(mode="after")
    def validate_window(self) -> "AvailabilityWindowDraft":
        if self.start >= self.end:
            raise ValueError("Window start time must be before end time")
        return self

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

def clean_availability_windows(windows: list[AvailabilityWindowDraft], current_time: datetime) -> list[AvailabilityWindowDraft]:
    current_hm = current_time.strftime("%H:%M")
    cleaned = []
    for w in windows:
        if w.end <= current_hm:
            continue
        start = w.start if w.start >= current_hm else current_hm
        cleaned.append(AvailabilityWindowDraft(start=start, end=w.end))
    return cleaned
