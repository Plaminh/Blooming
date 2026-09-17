from datetime import datetime
from typing import Any, Optional
from uuid import UUID
from pydantic import BaseModel

class ReminderResponse(BaseModel):
    id: UUID
    user_id: UUID
    milestone_id: Optional[UUID] = None
    plan_block_id: Optional[UUID] = None
    reminder_type: str
    message: str
    due_at: datetime
    original_due_at: datetime
    status: str
    viewed_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    dismissed_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class ReminderActionRequest(BaseModel):
    action_type: str
    new_due_at: Optional[datetime] = None
    payload: Optional[dict[str, Any]] = None
