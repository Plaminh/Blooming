from datetime import date, datetime, time
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class RecurringTaskResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    title: str
    estimated_duration_minutes: int
    priority: str
    importance: str
    category: str | None = None
    frequency: Literal["DAILY", "WEEKLY"]
    weekdays: list[int] = Field(default_factory=list)
    fixed_start_time: time | None = None
    start_date: date
    until_date: date | None = None
    is_active: bool
    created_at: datetime


class RecurringTaskUpdate(BaseModel):
    is_active: bool
