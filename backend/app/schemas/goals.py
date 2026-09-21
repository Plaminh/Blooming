from datetime import date, datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field

from app.schemas.drafts import RoadmapDraft


# Milestone Schemas
class MilestoneBase(BaseModel):
    title: str = Field(..., min_length=1)
    description: Optional[str] = None
    expected_outcome: Optional[str] = None
    due_at: Optional[datetime] = None
    status: str = Field(default="PENDING")


class MilestoneCreate(MilestoneBase):
    pass


class MilestoneUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1)
    description: Optional[str] = None
    expected_outcome: Optional[str] = None
    due_at: Optional[datetime] = None
    status: Optional[str] = None
    position: Optional[int] = None


class MilestoneResponse(MilestoneBase):
    id: UUID
    goal_id: UUID
    position: int
    completed_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# Goal Schemas
class GoalBase(BaseModel):
    title: str = Field(..., min_length=1)
    description: Optional[str] = None
    roadmap_summary: Optional[str] = None
    target_date: Optional[date] = None
    status: str = Field(default="DRAFT")


class GoalCreate(GoalBase):
    pass


class GoalUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1)
    description: Optional[str] = None
    roadmap_summary: Optional[str] = None
    target_date: Optional[date] = None
    status: Optional[str] = None


class GoalResponse(GoalBase):
    id: UUID
    user_id: UUID
    completed_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime
    milestones: list[MilestoneResponse] = []

    class Config:
        from_attributes = True


class RoadmapSave(BaseModel):
    session_id: UUID | None = None
    draft: RoadmapDraft
