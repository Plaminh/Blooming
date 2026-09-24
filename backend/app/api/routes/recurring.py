from uuid import UUID

from fastapi import APIRouter

from app.api.deps import CurrentUser, SessionDep
from app.schemas.recurring import RecurringTaskResponse, RecurringTaskUpdate
from app.services import recurring_service

router = APIRouter(prefix="/recurring-tasks", tags=["recurring-tasks"])


@router.get("", response_model=list[RecurringTaskResponse])
async def list_recurring_tasks(db: SessionDep, current_user: CurrentUser):
    templates = await recurring_service.list_active(db, current_user.id)
    return [recurring_service.to_response(item) for item in templates]


@router.patch("/{template_id}", response_model=RecurringTaskResponse)
async def update_recurring_task(
    template_id: UUID,
    obj_in: RecurringTaskUpdate,
    db: SessionDep,
    current_user: CurrentUser,
):
    template = await recurring_service.set_active(
        db, current_user.id, template_id, obj_in.is_active
    )
    await db.commit()
    return recurring_service.to_response(template)
