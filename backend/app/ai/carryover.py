"""Work that already belongs to a day before the user plans it.

Two sources feed a new day's draft automatically:

* tasks moved to that day earlier ("dời sang thứ 6", or planned for a later
  day in a multi-day message) that are not on any timeline yet, and
* occurrences of active recurring tasks that fall on that day and have not
  been created for it yet.

Both come back as ``ParsedTask`` values carrying the ids the save step needs
to reuse the existing row or link the new occurrence to its template.
"""

from datetime import date, datetime
from uuid import UUID
from zoneinfo import ZoneInfo

from sqlalchemy import exists, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.ai.parser import ParsedTask
from app.db.models.daily_plans import DailyPlan, PlanBlock
from app.db.models.tasks import RecurringTask, Task

UNFINISHED_STATUSES = ("DRAFT", "PENDING")


def _local_hm(value: datetime | None, tz: ZoneInfo) -> str | None:
    return value.astimezone(tz).strftime("%H:%M") if value is not None else None


def _parsed_priority(priority: str) -> str:
    # Parsed tasks carry LOW/MEDIUM/HIGH; URGENT keeps its weight as HIGH.
    return "HIGH" if priority == "URGENT" else priority


def _duration(minutes: int) -> int:
    return min(480, max(5, minutes))


def scheduled_on(day: date):
    """A task already has a timeline block in that day's plan.

    Blocks on other days do not count: a task left unfinished today and moved
    to tomorrow keeps its historical blocks but still waits for tomorrow.
    """
    return (
        exists()
        .where(PlanBlock.task_id == Task.id)
        .where(PlanBlock.daily_plan_id == DailyPlan.id)
        .where(DailyPlan.plan_date == day)
    )


async def pending_tasks_for_day(
    db: AsyncSession, user_id: UUID, day: date
) -> list[Task]:
    """Unfinished tasks meant for ``day`` that no timeline block holds yet."""
    return list(
        (
            await db.scalars(
                select(Task)
                .where(
                    Task.user_id == user_id,
                    Task.planned_date == day,
                    Task.status.in_(UNFINISHED_STATUSES),
                    ~scheduled_on(day),
                )
                .order_by(Task.created_at, Task.id)
            )
        ).all()
    )


async def due_recurring_tasks(
    db: AsyncSession, user_id: UUID, day: date
) -> list[RecurringTask]:
    """Active templates that repeat on ``day`` and have no task for it yet."""
    templates = (
        await db.scalars(
            select(RecurringTask)
            .where(
                RecurringTask.user_id == user_id,
                RecurringTask.is_active.is_(True),
                RecurringTask.start_date <= day,
                or_(RecurringTask.until_date.is_(None), RecurringTask.until_date >= day),
            )
            .order_by(RecurringTask.created_at, RecurringTask.id)
        )
    ).all()
    if not templates:
        return []
    created = set(
        (
            await db.scalars(
                select(Task.recurring_task_id).where(
                    Task.user_id == user_id,
                    Task.planned_date == day,
                    Task.recurring_task_id.in_([item.id for item in templates]),
                    Task.status != "CANCELLED",
                )
            )
        ).all()
    )
    return [item for item in templates if item.id not in created and item.occurs_on(day)]


async def carried_tasks(
    db: AsyncSession, user_id: UUID, day: date, tz: ZoneInfo
) -> list[ParsedTask]:
    carried: list[ParsedTask] = []
    for task in await pending_tasks_for_day(db, user_id, day):
        carried.append(
            ParsedTask(
                title=task.title,
                duration_min=_duration(task.estimated_duration_minutes),
                source="USER",
                importance=task.importance,  # type: ignore[arg-type]
                priority=_parsed_priority(task.priority),  # type: ignore[arg-type]
                category=task.category,
                fixed_start=_local_hm(task.fixed_start_at, tz),
                fixed_end=_local_hm(task.fixed_end_at, tz),
                source_task_id=str(task.id),
                recurring_task_id=(
                    str(task.recurring_task_id) if task.recurring_task_id else None
                ),
            )
        )
    for template in await due_recurring_tasks(db, user_id, day):
        carried.append(
            ParsedTask(
                title=template.title,
                duration_min=_duration(template.estimated_duration_minutes),
                source="USER",
                importance=template.importance,  # type: ignore[arg-type]
                priority=_parsed_priority(template.priority),  # type: ignore[arg-type]
                category=template.category,
                fixed_start=(
                    template.fixed_start_time.strftime("%H:%M")
                    if template.fixed_start_time
                    else None
                ),
                recurring_task_id=str(template.id),
            )
        )
    return carried
