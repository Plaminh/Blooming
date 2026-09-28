from datetime import datetime
from typing import Any, Optional
from uuid import UUID
from pydantic import BaseModel, ConfigDict

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

    model_config = ConfigDict(from_attributes=True)

from enum import Enum
from pydantic import model_validator

class ReminderActionType(str, Enum):
    REMIND_LATER = "REMIND_LATER"
    CREATE_PLAN = "CREATE_PLAN"
    MARK_COMPLETED = "MARK_COMPLETED"
    MOVE_MILESTONE = "MOVE_MILESTONE"

class ReminderActionRequest(BaseModel):
    action_type: ReminderActionType
    new_due_at: Optional[datetime] = None
    payload: Optional[dict[str, Any]] = None

    @model_validator(mode='after')
    def validate_new_due_at(self):
        if self.action_type in (ReminderActionType.REMIND_LATER, ReminderActionType.MOVE_MILESTONE):
            if not self.new_due_at:
                raise ValueError(f"{self.action_type.value} requires new_due_at")
        return self
