"""
Scope: Statistics aggregation for FocusRuns and DailyPlans.
Domain mappings:
- Focus session statuses qualifying for focus totals: 'ENDED'
- Plan outcomes:
  - Completed: 'COMPLETED'
  - Unfinished: 'CONFIRMED', 'ACTIVE'
  - Excluded: 'DRAFT', 'ARCHIVED'
- Timezone fallback logic: Use UserSettings.timezone if requested timezone is not provided or invalid.
"""

import uuid
import zoneinfo
from datetime import date, timedelta
from typing import Optional, List

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import func, select, case, Date

from app.db.models.users import UserSettings
from app.db.models.focus import FocusRun
from app.db.models.daily_plans import DailyPlan, PlanBlock
from app.schemas.statistics import (
    SummaryMetrics,
    DailyStudyEntry,
    PlanHistoryResponse,
    PlanHistoryItem,
)

COMPLETED_PLAN_STATUSES = ["COMPLETED"]
UNFINISHED_PLAN_STATUSES = ["CONFIRMED", "ACTIVE"]
EXCLUDED_PLAN_STATUSES = ["DRAFT", "ARCHIVED"]


async def _get_user_timezone(
    db: AsyncSession, user_id: uuid.UUID, requested_tz: Optional[str] = None
) -> str:
    if requested_tz:
        try:
            zoneinfo.ZoneInfo(requested_tz)
            return requested_tz
        except zoneinfo.ZoneInfoNotFoundError:
            pass

    result = await db.execute(
        select(UserSettings).where(UserSettings.user_id == user_id)
    )
    settings = result.scalar_one_or_none()
    return settings.timezone if settings else "UTC"


async def get_statistics_summary(
    db: AsyncSession,
    user_id: uuid.UUID,
    start_date: date,
    end_date: date,
    requested_tz: Optional[str] = None,
) -> SummaryMetrics:
    tz_str = await _get_user_timezone(db, user_id, requested_tz)
    local_started_at = func.timezone(tz_str, FocusRun.started_at).cast(Date)

    focus_stmt = select(
        func.coalesce(func.sum(FocusRun.actual_duration_seconds), 0).label(
            "total_seconds"
        ),
        func.count(func.distinct(local_started_at)).label("study_days"),
    ).where(
        FocusRun.user_id == user_id,
        FocusRun.status == "ENDED",
        FocusRun.actual_duration_seconds > 0,
        local_started_at >= start_date,
        local_started_at <= end_date,
    )

    result = await db.execute(focus_stmt)
    focus_stats = result.first()

    total_seconds = focus_stats.total_seconds if focus_stats else 0
    study_days = focus_stats.study_days if focus_stats else 0

    hours = total_seconds // 3600
    minutes = (total_seconds % 3600) // 60

    plan_stmt = select(
        func.coalesce(
            func.sum(case((DailyPlan.status.in_(COMPLETED_PLAN_STATUSES), 1), else_=0)),
            0,
        ).label("completed_count"),
        func.coalesce(
            func.sum(
                case((DailyPlan.status.in_(UNFINISHED_PLAN_STATUSES), 1), else_=0)
            ),
            0,
        ).label("unfinished_count"),
    ).where(
        DailyPlan.user_id == user_id,
        DailyPlan.plan_date >= start_date,
        DailyPlan.plan_date <= end_date,
    )

    result = await db.execute(plan_stmt)
    plan_stats = result.first()

    completed_plans = plan_stats.completed_count if plan_stats else 0
    unfinished_plans = plan_stats.unfinished_count if plan_stats else 0

    return SummaryMetrics(
        study_time_hours=int(hours),
        study_time_minutes=int(minutes),
        study_day_count=int(study_days),
        completed_plan_count=int(completed_plans),
        unfinished_plan_count=int(unfinished_plans),
    )


async def get_daily_statistics(
    db: AsyncSession,
    user_id: uuid.UUID,
    start_date: date,
    end_date: date,
    requested_tz: Optional[str] = None,
) -> List[DailyStudyEntry]:
    tz_str = await _get_user_timezone(db, user_id, requested_tz)
    local_started_at = func.timezone(tz_str, FocusRun.started_at).cast(Date)

    stmt = (
        select(
            local_started_at.label("study_date"),
            func.coalesce(func.sum(FocusRun.actual_duration_seconds), 0).label(
                "total_seconds"
            ),
        )
        .where(
            FocusRun.user_id == user_id,
            FocusRun.status == "ENDED",
            FocusRun.actual_duration_seconds > 0,
            local_started_at >= start_date,
            local_started_at <= end_date,
        )
        .group_by(local_started_at)
    )

    result = await db.execute(stmt)
    daily_stats = result.all()

    stats_dict = {stat.study_date: stat.total_seconds for stat in daily_stats}

    entries = []
    current_date = start_date
    while current_date <= end_date:
        seconds = stats_dict.get(current_date, 0)
        hours = seconds / 3600.0
        day_label = current_date.strftime("%a")

        entries.append(
            DailyStudyEntry(
                day_label=day_label, hours=round(hours, 1), date=current_date
            )
        )
        current_date += timedelta(days=1)

    return entries


async def get_plan_history(
    db: AsyncSession,
    user_id: uuid.UUID,
    start_date: date,
    end_date: date,
    status_filter: str = "All",
    page: int = 1,
    page_size: int = 4,
) -> PlanHistoryResponse:
    stmt = select(DailyPlan).where(
        DailyPlan.user_id == user_id,
        DailyPlan.plan_date >= start_date,
        DailyPlan.plan_date <= end_date,
        DailyPlan.status.notin_(EXCLUDED_PLAN_STATUSES),
    )

    if status_filter == "Completed":
        stmt = stmt.where(DailyPlan.status.in_(COMPLETED_PLAN_STATUSES))
    elif status_filter == "Unfinished":
        stmt = stmt.where(DailyPlan.status.in_(UNFINISHED_PLAN_STATUSES))

    count_stmt = select(func.count()).select_from(stmt.subquery())
    total_items = (await db.execute(count_stmt)).scalar() or 0

    paginated_stmt = (
        stmt.order_by(
            DailyPlan.plan_date.desc(), DailyPlan.created_at.desc(), DailyPlan.id.desc()
        )
        .offset((page - 1) * page_size)
        .limit(page_size)
    )

    result = await db.execute(paginated_stmt)
    plans = result.scalars().all()

    if not plans:
        return PlanHistoryResponse(
            items=[],
            total_items=total_items,
            total_pages=0,
            current_page=page,
            items_per_page=page_size,
        )

    plan_ids = [p.id for p in plans]

    tc_stmt = (
        select(
            PlanBlock.daily_plan_id,
            func.count().label("total_tasks"),
            func.sum(case((PlanBlock.status == "COMPLETED", 1), else_=0)).label(
                "completed_tasks"
            ),
        )
        .where(PlanBlock.daily_plan_id.in_(plan_ids), PlanBlock.block_type == "TASK")
        .group_by(PlanBlock.daily_plan_id)
    )

    tc_result = await db.execute(tc_stmt)
    task_counts = tc_result.all()

    counts_dict = {
        tc.daily_plan_id: (tc.total_tasks, tc.completed_tasks or 0)
        for tc in task_counts
    }

    items = []
    for plan in plans:
        total_tasks, completed_tasks = counts_dict.get(plan.id, (0, 0))
        plan_status = (
            "Completed" if plan.status in COMPLETED_PLAN_STATUSES else "Unfinished"
        )

        d_day = plan.plan_date.strftime("%d").lstrip("0")
        date_lbl = plan.plan_date.strftime(f"%b {d_day}, %Y")

        items.append(
            PlanHistoryItem(
                id=plan.id,
                date_label=date_lbl,
                plan_name="Daily Plan",
                completed_tasks=completed_tasks,
                total_tasks=total_tasks,
                status=plan_status,
            )
        )

    total_pages = (total_items + page_size - 1) // page_size

    return PlanHistoryResponse(
        items=items,
        total_items=total_items,
        total_pages=total_pages,
        current_page=page,
        items_per_page=page_size,
    )
