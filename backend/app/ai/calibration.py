"""Personal duration calibration derived from completed focus history."""

from collections import defaultdict
from datetime import datetime, timedelta, timezone
from statistics import median
from time import monotonic
from uuid import UUID

from app.db.models.focus import FocusRun
from app.db.models.tasks import Task
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

_cache: dict[UUID, tuple[float, dict[str, float]]] = {}
_CACHE_SECONDS = 300


async def calibration_multipliers(
    db: AsyncSession, user_id: UUID, *, minimum_samples: int = 5,
    now: datetime | None = None,
) -> dict[str, float]:
    if now is None:
        now = datetime.now(timezone.utc)
    cached = _cache.get(user_id)
    if cached and monotonic() < cached[0]:
        return cached[1].copy()
    rows = (
        await db.execute(
            select(
                Task.id,
                Task.category,
                Task.estimated_duration_minutes,
                FocusRun.actual_duration_seconds,
            )
            .join(FocusRun, FocusRun.task_id == Task.id)
            .where(
                Task.user_id == user_id,
                Task.source == "AI",
                Task.status == "COMPLETED",
                Task.completed_at >= now - timedelta(days=60),
                Task.completed_at <= now,
                FocusRun.user_id == user_id,
                FocusRun.status == "ENDED",
                FocusRun.outcome.in_(("DONE", "FINISHED_EARLY")),
                FocusRun.actual_duration_seconds.is_not(None),
            )
        )
    ).all()
    actual_by_task: dict[object, int] = defaultdict(int)
    task_info: dict[object, tuple[str, int]] = {}
    for task_id, category, estimate, actual in rows:
        if category and estimate and actual is not None:
            actual_by_task[task_id] += int(actual)
            task_info[task_id] = (category, int(estimate))
    ratios: dict[str, list[float]] = defaultdict(list)
    for task_id, actual_seconds in actual_by_task.items():
        category, estimate_minutes = task_info[task_id]
        ratios[category].append(actual_seconds / 60 / estimate_minutes)
    values = {
        category: round(min(2.0, max(0.6, 1 + (median(samples) - 1) * len(samples) / (len(samples) + 2))), 2)
        for category, samples in ratios.items()
        if len(samples) >= minimum_samples
    }
    _cache[user_id] = (monotonic() + _CACHE_SECONDS, values)
    return values.copy()


def apply_multiplier(
    minutes: int, category: str | None, multipliers: dict[str, float]
) -> int:
    factor = multipliers.get(category or "", 1.0)
    return min(480, max(5, round(minutes * factor / 5) * 5))
