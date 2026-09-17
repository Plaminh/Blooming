from uuid import UUID

from fastapi import APIRouter

from app.api.deps import CurrentUser, SessionDep
from app.schemas.reminders import ReminderActionRequest, ReminderResponse
from app.services.reminders_service import reminders_service

router = APIRouter(prefix="/reminders", tags=["reminders"])


@router.get("/due", response_model=list[ReminderResponse])
async def get_due_reminders(
    db: SessionDep,
    current_user: CurrentUser,
):
    return await reminders_service.get_due_reminders(db, current_user.id)


@router.post("/{reminder_id}/actions", response_model=ReminderResponse)
async def execute_reminder_action(
    reminder_id: UUID,
    action_in: ReminderActionRequest,
    db: SessionDep,
    current_user: CurrentUser,
):
    reminder = await reminders_service.execute_action(
        db, reminder_id, action_in, current_user.id
    )
    await db.commit()
    return reminder
