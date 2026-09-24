"""Recurring task templates: creation from saved drafts, listing and stopping."""

from datetime import date
from uuid import UUID
from zoneinfo import ZoneInfo

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.ai.router import normalize
from app.core.errors import ResourceNotFoundError
from app.db.models.tasks import WEEKDAY_COUNT, RecurringTask
from app.schemas.drafts import TaskDraft
from app.schemas.recurring import RecurringTaskResponse


def weekday_mask(weekdays: list[int]) -> int:
    mask = 0
    for day in weekdays:
        if 0 <= day < WEEKDAY_COUNT:
            mask |= 1 << day
    return mask


def weekdays_of(mask: int) -> list[int]:
    return [day for day in range(WEEKDAY_COUNT) if mask & (1 << day)]


def to_response(template: RecurringTask) -> RecurringTaskResponse:
    return RecurringTaskResponse(
        id=template.id,
        title=template.title,
        estimated_duration_minutes=template.estimated_duration_minutes,
        priority=template.priority,
        importance=template.importance,
        category=template.category,
        frequency=template.frequency,  # type: ignore[arg-type]
        weekdays=weekdays_of(template.weekday_mask) if template.frequency == "WEEKLY" else [],
        fixed_start_time=template.fixed_start_time,
        start_date=template.start_date,
        until_date=template.until_date,
        is_active=template.is_active,
        created_at=template.created_at,
    )


async def list_active(db: AsyncSession, user_id: UUID) -> list[RecurringTask]:
    return list(
        (
            await db.scalars(
                select(RecurringTask)
                .where(RecurringTask.user_id == user_id, RecurringTask.is_active.is_(True))
                .order_by(RecurringTask.created_at, RecurringTask.id)
            )
        ).all()
    )


async def upsert_from_draft(
    db: AsyncSession,
    user_id: UUID,
    task: TaskDraft,
    first_day: date,
    tz: ZoneInfo,
) -> RecurringTask:
    """Create the template a saved task repeats from, reusing an identical one.

    Saving the same repeating draft twice (for example after replacing a plan)
    must not make the task appear twice on every future day.
    """
    recurrence = task.recurrence
    assert recurrence is not None
    weekdays = recurrence.weekdays or [first_day.weekday()]
    frequency = recurrence.freq
    mask = weekday_mask(weekdays) if frequency == "WEEKLY" else 0
    fixed_start_time = (
        task.fixedStart.astimezone(tz).time().replace(tzinfo=None)
        if task.fixedStart is not None
        else None
    )
    for existing in await list_active(db, user_id):
        if (
            normalize(existing.title) == normalize(task.title)
            and existing.frequency == frequency
            and existing.weekday_mask == mask
        ):
            existing.estimated_duration_minutes = task.durationMin
            existing.fixed_start_time = fixed_start_time
            existing.until_date = recurrence.until
            return existing
    template = RecurringTask(
        user_id=user_id,
        title=task.title.strip()[:200],
        estimated_duration_minutes=min(480, max(5, task.durationMin)),
        priority=task.priority,
        importance=task.importance,
        category=task.category,
        frequency=frequency,
        weekday_mask=mask,
        fixed_start_time=fixed_start_time,
        start_date=first_day,
        until_date=recurrence.until,
    )
    db.add(template)
    await db.flush()
    return template


async def set_active(
    db: AsyncSession, user_id: UUID, template_id: UUID, is_active: bool
) -> RecurringTask:
    template = await db.scalar(
        select(RecurringTask).where(
            RecurringTask.id == template_id, RecurringTask.user_id == user_id
        )
    )
    if template is None:
        raise ResourceNotFoundError("Recurring task not found")
    template.is_active = is_active
    await db.flush()
    return template


def match_by_title(templates: list[RecurringTask], message: str) -> list[RecurringTask]:
    """Templates whose title the message names ("dừng lặp lại học tiếng Anh")."""
    text = normalize(message)
    return [item for item in templates if normalize(item.title) in text]
