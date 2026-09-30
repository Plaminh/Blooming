import logging
from datetime import date, datetime
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.time_utils import safe_timezone
from app.crud.crud_daily_plan import daily_plan as crud_daily_plan
from app.db.models.daily_plans import PlanRevision
from app.db.models.tasks import Task
from app.db.models.users import UserSettings

logger = logging.getLogger(__name__)
USABLE_PLAN_STATUSES = {"CONFIRMED", "ACTIVE", "COMPLETED"}


async def _pending_task_infos(db: AsyncSession, user_id: UUID, day: date) -> list[dict]:
    """Deferred and recurring work waiting for a day that has no plan yet."""
    from app.ai.carryover import due_recurring_tasks, pending_tasks_for_day

    infos = [
        {"task_id": str(task.id), "title": task.title, "reason": "DEFERRED"}
        for task in await pending_tasks_for_day(db, user_id, day)
    ]
    infos.extend(
        {"task_id": None, "title": template.title, "reason": "RECURRING"}
        for template in await due_recurring_tasks(db, user_id, day)
    )
    return infos


async def _get_plan_for_preview_validation(
    db: AsyncSession, user_id: UUID, plan_date: date
):
    """Ownership-scoped lookup used when restoring a persisted preview."""
    return await crud_daily_plan.get_by_date(db, user_id, plan_date)


async def get_today_draft(
    db: AsyncSession, user_id: UUID, local_date: date | None = None
) -> dict:
    from app.schemas.drafts import (
        TodayDraft,
        TaskDraft,
        AvailabilityWindowDraft,
    )

    settings = await db.scalar(
        select(UserSettings).where(UserSettings.user_id == user_id)
    )
    tz = safe_timezone(settings.timezone if settings else "UTC")
    if local_date is None:
        local_date = datetime.now(tz).date()

    plan = await crud_daily_plan.get_by_date(db, user_id, local_date)
    if not plan or plan.status not in USABLE_PLAN_STATUSES:
        return TodayDraft(
            planDate=local_date,
            timezone=str(tz),
            windows=[],
            tasks=[],
            deferred_tasks=[],
        ).model_dump(mode="json")

    await db.refresh(plan, ["plan_blocks", "availability_windows"])

    # Load tasks from blocks
    task_ids = {b.task_id for b in plan.plan_blocks if b.task_id}
    tasks = {}
    if task_ids:
        tasks_list = (
            await db.scalars(
                select(Task)
                .options(selectinload(Task.dependencies))
                .where(Task.id.in_(task_ids))
            )
        ).all()
        tasks = {t.id: t for t in tasks_list}

    # Only open work is re-planned: a finished task stays in today's history,
    # and putting it back in the draft would schedule it again on save.
    open_tasks = {
        task_id: task
        for task_id, task in tasks.items()
        if task.status not in ("COMPLETED", "SKIPPED", "CANCELLED")
    }
    draft_tasks = []
    seen: set = set()
    for b in sorted(plan.plan_blocks, key=lambda x: x.position):
        if b.block_type == "TASK" and b.task_id in open_tasks and b.task_id not in seen:
            seen.add(b.task_id)  # A split task has several blocks.
            t = open_tasks[b.task_id]
            draft_tasks.append(
                TaskDraft(
                    id=str(t.id),
                    title=t.title,
                    durationMin=t.estimated_duration_minutes,
                    priority=t.priority,
                    importance=t.importance,
                    category=t.category,
                    estimateSource="USER" if t.source == "MANUAL" else "AI",
                    breakAfterMin=t.preferred_break_duration_minutes,
                    deadline=t.deadline_at,
                    schedulingType=t.scheduling_type,
                    fixedStart=t.fixed_start_at,
                    fixedEnd=t.fixed_end_at,
                    dependencies=[
                        str(d.depends_on_task_id)
                        for d in t.dependencies
                        if d.depends_on_task_id in open_tasks
                    ],
                    splittable=t.is_splittable,
                    sourceTaskId=str(t.id),
                    recurringTaskId=str(t.recurring_task_id)
                    if t.recurring_task_id
                    else None,
                )
            )

    # Windows are wall-clock times in the draft's own timezone.
    plan_tz = safe_timezone(plan.timezone_snapshot)
    windows = []
    for w in plan.availability_windows:
        windows.append(
            AvailabilityWindowDraft(
                start=w.available_start_at.astimezone(plan_tz).strftime("%H:%M"),
                end=w.available_end_at.astimezone(plan_tz).strftime("%H:%M"),
            )
        )

    draft = TodayDraft(
        planDate=plan.plan_date,
        timezone=plan.timezone_snapshot,
        windows=windows,
        tasks=draft_tasks,
        deferred_tasks=[],
    )
    return draft.model_dump(mode="json")


async def get_today(
    db: AsyncSession, user_id: UUID, local_date: date | None = None
) -> dict:
    settings = await db.scalar(
        select(UserSettings).where(UserSettings.user_id == user_id)
    )
    tz = safe_timezone(settings.timezone if settings else "UTC")
    if local_date is None:
        local_date = datetime.now(tz).date()

    plan = await crud_daily_plan.get_by_date(db, user_id, local_date)
    if not plan or plan.status not in USABLE_PLAN_STATUSES:
        return {
            "plan_date": local_date,
            "status": "NO_PLAN",
            "timezone": str(tz),
            "pending_tasks": await _pending_task_infos(db, user_id, local_date),
        }

    revision = await db.scalar(
        select(PlanRevision)
        .where(PlanRevision.daily_plan_id == plan.id)
        .order_by(PlanRevision.revision_number.desc())
        .limit(1)
    )
    scheduling = revision.after_snapshot if revision else {}
    task_draft_map = scheduling.get("task_draft_map", {})
    blocks = sorted(plan.plan_blocks, key=lambda b: b.planned_start_at)

    block_dicts = []
    for b in blocks:
        b_dict = {
            "id": b.id,
            "block_type": b.block_type,
            "task_id": b.task_id,
            "draft_task_id": task_draft_map.get(str(b.task_id)) if b.task_id else None,
            "title": b.title,
            "planned_start_at": b.planned_start_at,
            "planned_end_at": b.planned_end_at,
            "position": b.position,
            "status": b.status,
            "is_locked": b.is_locked,
            "description": b.task.description if b.task else None,
            "category": b.task.category if b.task else None,
            "estimated_duration_minutes": b.task.estimated_duration_minutes
            if b.task
            else None,
            "importance": b.task.importance if b.task else None,
            "preferred_break_duration_minutes": (
                b.task.preferred_break_duration_minutes if b.task else None
            ),
            "source": b.task.source if b.task else None,
        }
        block_dicts.append(b_dict)

    return {
        "plan_date": plan.plan_date,
        "status": plan.status,
        "reality_check": plan.reality_check,
        "blocks": block_dicts,
        "timezone": str(tz),
        "unscheduled_tasks": scheduling.get("unscheduled_tasks", []),
        "reasons": scheduling.get("reasons", []),
    }
