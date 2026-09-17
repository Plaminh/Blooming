from datetime import date, datetime
from typing import List, Optional, Literal
from uuid import UUID
from pydantic import BaseModel, Field

class TodayBlock(BaseModel):
    id: UUID
    block_type: Literal["TASK", "BREAK", "BUFFER", "FIXED_EVENT"]
    task_id: Optional[UUID] = None
    title: Optional[str] = None
    planned_start_at: datetime
    planned_end_at: datetime
    position: int
    status: str
    is_locked: bool

class TodayResponse(BaseModel):
    plan_date: date
    status: str
    reality_check: Optional[str] = None
    blocks: List[TodayBlock] = Field(default_factory=list)

class TodayNoPlanResponse(BaseModel):
    plan_date: date
    status: Literal["NO_PLAN"] = "NO_PLAN"

class TodayTaskEdit(BaseModel):
    title: Optional[str] = Field(None, min_length=1)
    estimated_duration_minutes: Optional[int] = Field(None, gt=0)

class TodayTaskStatusUpdate(BaseModel):
    status: Literal["PENDING", "IN_PROGRESS", "COMPLETED", "SKIPPED", "CANCELLED"]
