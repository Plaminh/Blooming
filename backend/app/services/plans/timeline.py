from typing import Any
from uuid import UUID
from datetime import datetime, timezone

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.core.errors import (
    ResourceNotFoundError,
    UnauthorizedOwnershipError,
    ValidationError,
    PlanAlreadyExistsError,
)
from app.core.scheduler import DeterministicScheduler, ScheduleTask, ScheduleWindow
from app.crud.crud_daily_plan import daily_plan as crud_daily_plan
from app.db.models.tasks import Task
from app.db.models.daily_plans import (
    PlanBlock,
    AvailabilityWindow as DbAvailabilityWindow,
    DailyPlan,
)


def compute_reality_check(schedule_result) -> str:
    if schedule_result.unscheduled_tasks or any(
        r["code"] == "FIXED_TASK_OVERLAP" for r in schedule_result.reasons
    ):
        return "OVERLOADED"
    buffer_ratio = 1.0
    if schedule_result.available_minutes > 0:
        buffer_ratio = (
            schedule_result.available_minutes - schedule_result.workload_minutes
        ) / schedule_result.available_minutes
    if buffer_ratio >= 0.2:
        return "COMFORTABLE"
    return "TIGHT"


async def generate_timeline(db: AsyncSession, request: Any, user_id: UUID) -> Any:
    if len(set(request.task_ids)) != len(request.task_ids):
        raise ValidationError("Duplicate task IDs are not allowed")

    result = await db.execute(
        select(Task)
        .options(selectinload(Task.dependencies))
        .where(Task.user_id == user_id, Task.id.in_(request.task_ids))
    )
    db_tasks = list(result.scalars().all())

    if len(db_tasks) != len(set(request.task_ids)):
        raise ValidationError(
            "One or more requested tasks were not found or are not owned by the user"
        )

    schedule_tasks = []
    for t in db_tasks:
        schedule_tasks.append(
            ScheduleTask(
                id=t.id,
                title=t.title,
                estimated_duration_minutes=t.estimated_duration_minutes,
                priority=t.priority,
                scheduling_type=t.scheduling_type,
                is_splittable=t.is_splittable,
                min_split_duration_minutes=t.min_split_duration_minutes,
                preferred_break_duration_minutes=t.preferred_break_duration_minutes,
                fixed_start_at=t.fixed_start_at,
                fixed_end_at=t.fixed_end_at,
                dependencies=[d.depends_on_task_id for d in t.dependencies],
                created_at=t.created_at,
            )
        )

    windows = [
        ScheduleWindow(start_at=w.start_at, end_at=w.end_at)
        for w in request.availability_windows
    ]

    scheduler = DeterministicScheduler()
    schedule_result = scheduler.schedule(schedule_tasks, windows)

    reality_check = compute_reality_check(schedule_result)

    draft_plan = await crud_daily_plan.create_draft(
        db,
        user_id=user_id,
        plan_date=request.plan_date,
        timezone_snapshot=request.timezone_snapshot,
        reality_check=reality_check,
    )

    for w in request.availability_windows:
        db_w = DbAvailabilityWindow(
            daily_plan_id=draft_plan.id,
            available_start_at=w.start_at,
            available_end_at=w.end_at,
        )
        db.add(db_w)

    draft_blocks = []
    for i, b in enumerate(schedule_result.blocks):
        db_b = PlanBlock(
            daily_plan_id=draft_plan.id,
            task_id=b.task_id,
            block_type=b.block_type,
            title=b.title,
            planned_start_at=b.start_at,
            planned_end_at=b.end_at,
            position=i,
            status="PLANNED",
            created_by="SCHEDULER",
        )
        db.add(db_b)
        draft_blocks.append(db_b)

    await db.flush()
    await db.commit()

    return {
        "draft_id": draft_plan.id,
        "blocks": [
            {
                "block_type": b.block_type,
                "planned_start_at": b.planned_start_at,
                "planned_end_at": b.planned_end_at,
                "task_id": b.task_id,
                "title": b.title,
                "position": b.position,
            }
            for b in draft_blocks
        ],
        "reality_check": reality_check,
        "reality_check_reasons": schedule_result.reasons,
        "unscheduled_tasks": schedule_result.unscheduled_tasks,
    }


async def save_daily_plan(db: AsyncSession, request: Any, user_id: UUID) -> Any:
    draft = await crud_daily_plan.get(db, request.draft_id, user_id)
    if not draft:
        raise ResourceNotFoundError("Timeline Draft not found")
    if draft.user_id != user_id:
        raise UnauthorizedOwnershipError("Unauthorized ownership")

    if draft.status in ("CONFIRMED", "ACTIVE"):
        return draft

    existing_plan = await crud_daily_plan.get_by_date(db, user_id, draft.plan_date)
    if existing_plan and existing_plan.id != draft.id:
        if existing_plan.status in ("CONFIRMED", "ACTIVE"):
            if not getattr(request, "replace_existing", False):
                raise PlanAlreadyExistsError(
                    "An active plan already exists for this date. Provide replace_existing=True to replace it."
                )
            existing_plan.status = "ARCHIVED"
            db.add(existing_plan)
            await db.flush()

    draft.status = "CONFIRMED"
    draft.confirmed_at = datetime.now(timezone.utc)
    db.add(draft)

    await db.commit()

    result = await db.execute(
        select(DailyPlan)
        .options(selectinload(DailyPlan.plan_blocks))
        .where(DailyPlan.id == draft.id, DailyPlan.user_id == user_id)
    )
    return result.scalars().first()
