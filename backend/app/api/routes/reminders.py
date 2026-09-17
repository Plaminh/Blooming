from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, get_db
from app.db.models.users import User
from app.schemas.reminders import ReminderResponse, ReminderActionRequest
from app.services.reminders_service import reminders_service

router = APIRouter(prefix="/reminders", tags=["reminders"])

@router.get("/due", response_model=List[ReminderResponse])
async def get_due_reminders(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return await reminders_service.get_due_reminders(db, current_user.id)

@router.post("/{reminder_id}/actions", response_model=ReminderResponse)
async def execute_reminder_action(
    reminder_id: UUID,
    action_in: ReminderActionRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    reminder = await reminders_service.execute_action(db, reminder_id, action_in, current_user.id)
    await db.commit()
    return reminder
