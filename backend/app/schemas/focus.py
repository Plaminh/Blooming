from typing import Literal
from uuid import UUID
from datetime import datetime
from pydantic import BaseModel, Field
from app.schemas.today import TodayResponse


class FocusSessionStart(BaseModel):
    task_id: UUID | None = None
    plan_block_id: UUID | None = None
    quick_task_title: str | None = None
    planned_focus_seconds: int = Field(ge=1, le=86400)
    planned_break_seconds: int = Field(default=0, ge=0, le=21600)


class FocusSessionFinish(BaseModel):
    run_id: UUID | None = None
    outcome: Literal["DONE", "NEED_MORE_TIME", "SKIP", "FINISHED_EARLY"]
    actual_duration_seconds: int | None = Field(default=None, ge=0)
    should_replan: bool = False


class FocusRunResponse(BaseModel):
    replan: TodayResponse | None = None
    id: UUID
    user_id: UUID
    task_id: UUID | None = None
    plan_block_id: UUID | None = None
    quick_task_title: str | None = None
    status: str
    outcome: str | None = None
    planned_focus_seconds: int
    planned_break_seconds: int
    started_at: datetime | None = None
    expected_end_at: datetime | None = None
    paused_at: datetime | None = None
    total_paused_seconds: int
    ended_at: datetime | None = None
    actual_duration_seconds: int | None = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
