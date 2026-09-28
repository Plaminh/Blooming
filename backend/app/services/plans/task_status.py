import logging
from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.errors import ResourceNotFoundError, UnauthorizedOwnershipError
from app.crud.crud_task import task as crud_task
from app.db.models.daily_plans import DailyPlan
from app.db.models.tasks import Task
from app.schemas.today import (
    TodayTaskEdit,
    TodayTaskStatusUpdate,
)

logger = logging.getLogger(__name__)
USABLE_PLAN_STATUSES = {"CONFIRMED", "ACTIVE", "COMPLETED"}


async def sync_daily_plan_completion(db: AsyncSession, plan_id: UUID) -> None:
    """
    Does this Daily Plan still contain unfinished actionable work?
    If no, transitions its status to COMPLETED.
    """
    plan = await db.scalar(
        select(DailyPlan)
        .options(selectinload(DailyPlan.plan_blocks))
        .where(DailyPlan.id == plan_id)
    )
    if not plan or plan.status in ("DRAFT", "ARCHIVED", "COMPLETED"):
        return

    has_unfinished = any(
        b.block_type == "TASK" and b.status in ("PLANNED", "ACTIVE")
        for b in plan.plan_blocks
    )

    has_actionable_tasks = any(b.block_type == "TASK" for b in plan.plan_blocks)

    if not has_unfinished and has_actionable_tasks:
        plan.status = "COMPLETED"
        plan.completed_at = datetime.now(timezone.utc)
        db.add(plan)


async def update_task_from_today(
    db: AsyncSession, user_id: UUID, task_id: UUID, obj_in: TodayTaskEdit
) -> Task:
    task_db = await crud_task.get_with_plan_blocks(db, id=task_id, user_id=user_id)
    if not task_db:
        raise ResourceNotFoundError("Task not found")
    if task_db.user_id != user_id:
        raise UnauthorizedOwnershipError()

    if obj_in.title is not None:
        task_db.title = obj_in.title
    if obj_in.estimated_duration_minutes is not None:
        task_db.estimated_duration_minutes = obj_in.estimated_duration_minutes
    if "description" in obj_in.model_fields_set:
        task_db.description = obj_in.description
    if "category" in obj_in.model_fields_set:
        task_db.category = obj_in.category

    db.add(task_db)

    # update title in plan blocks as well
    if obj_in.title is not None:
        for b in task_db.plan_blocks:
            b.title = obj_in.title
            db.add(b)

    await db.commit()
    return task_db


async def update_task_status_from_today(
    db: AsyncSession,
    user_id: UUID,
    task_id: UUID,
    obj_in: TodayTaskStatusUpdate,
    commit: bool = True,
) -> Task:
    from app.db.models.users import User

    await db.execute(select(User.id).where(User.id == user_id).with_for_update())
    task_db = await crud_task.get_with_plan_blocks(db, id=task_id, user_id=user_id)
    if not task_db:
        raise ResourceNotFoundError("Task not found")
    if task_db.user_id != user_id:
        raise UnauthorizedOwnershipError()

    if task_db.status == obj_in.status:
        return task_db  # Idempotent

    task_db.status = obj_in.status
    if obj_in.status == "COMPLETED":
        task_db.completed_at = datetime.now(timezone.utc)

        from app.core.economy import LEAVES_PER_TASK
        from app.services.garden_service import award_resources

        # Award leaves
        await award_resources(
            db=db,
            user_id=user_id,
            resource_type="LEAVES",
            amount=LEAVES_PER_TASK,
            event_type="TASK_COMPLETED",
            idempotency_key=f"task_completed_{task_id}",
            source_id=task_id,
        )
    else:
        task_db.completed_at = None

    db.add(task_db)

    # update plan blocks
    block_status_map = {
        "DRAFT": "PLANNED",
        "PENDING": "PLANNED",
        "IN_PROGRESS": "ACTIVE",
        "COMPLETED": "COMPLETED",
        "SKIPPED": "SKIPPED",
        "CANCELLED": "CANCELLED",
    }
    b_status = block_status_map.get(obj_in.status, "PLANNED")

    for b in task_db.plan_blocks:
        b.status = b_status
        if obj_in.status == "COMPLETED":
            b.completed_at = task_db.completed_at
        else:
            b.completed_at = None
        db.add(b)

    await db.flush()

    # Synchronize plan completion for all affected plans
    plan_ids = {b.daily_plan_id for b in task_db.plan_blocks if b.daily_plan_id}
    for pid in plan_ids:
        await sync_daily_plan_completion(db, pid)

    if commit:
        await db.commit()
    return task_db
