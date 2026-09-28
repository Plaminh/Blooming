import logging
from datetime import date, datetime
from typing import cast
from uuid import UUID, uuid4

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.scheduler import DeterministicScheduler, ScheduleTask, ScheduleWindow
from app.core.time_utils import safe_timezone
from app.crud.crud_daily_plan import daily_plan as crud_daily_plan
from app.db.models.users import UserSettings
from app.schemas.today import (
    TodayBlock,
    TodayPreviewRequest,
    TodayPreviewResponse,
)
from app.schemas.planning import TaskCategory

logger = logging.getLogger(__name__)
USABLE_PLAN_STATUSES = {"CONFIRMED", "ACTIVE", "COMPLETED"}


from app.core.preview_token import generate_hmac_token, plan_version


def _normalize_dt(dt, tz):
    from datetime import datetime, time

    if not isinstance(dt, date) and not isinstance(dt, datetime):
        return dt
    if not isinstance(dt, datetime):
        # date-only, end-of-day rule
        dt = datetime.combine(dt, time(23, 59, 59))
    if dt.tzinfo is None:
        return dt.replace(tzinfo=tz)
    return dt.astimezone(tz)


def _normalize_and_schedule(draft, tz, local_date, user_id):
    import uuid
    from datetime import datetime, timedelta

    windows = []
    for w in draft.windows:
        start_dt = datetime.strptime(w.start, "%H:%M").replace(
            year=local_date.year,
            month=local_date.month,
            day=local_date.day,
            tzinfo=tz,
        )
        end_dt = datetime.strptime(w.end, "%H:%M").replace(
            year=local_date.year,
            month=local_date.month,
            day=local_date.day,
            tzinfo=tz,
        )
        windows.append(ScheduleWindow(start_at=start_dt, end_at=end_dt))

    tasks = []
    # Generate deterministic UUIDs from user_id and draft task ID
    draft_to_uuid = {t.id: uuid.uuid5(user_id, t.id) for t in draft.tasks}

    base_time = datetime(2000, 1, 1, tzinfo=tz)
    for i, t in enumerate(draft.tasks):
        sched_priority = t.priority
        if sched_priority not in ("URGENT", "HIGH", "MEDIUM", "LOW"):
            sched_priority = "MEDIUM"

        tasks.append(
            ScheduleTask(
                id=draft_to_uuid[t.id],
                title=t.title,
                estimated_duration_minutes=t.durationMin,
                priority=sched_priority,
                scheduling_type=t.schedulingType,
                created_at=base_time + timedelta(seconds=i),
                is_splittable=t.splittable,
                preferred_break_duration_minutes=t.breakAfterMin,
                fixed_start_at=_normalize_dt(t.fixedStart, tz)
                if t.fixedStart
                else None,
                fixed_end_at=_normalize_dt(t.fixedEnd, tz) if t.fixedEnd else None,
                dependencies=[
                    draft_to_uuid[d] for d in t.dependencies if d in draft_to_uuid
                ],
            )
        )

    result = DeterministicScheduler().schedule(tasks, windows)
    if any(reason["code"] == "FIXED_TASK_OVERLAP" for reason in result.reasons):
        from fastapi import HTTPException

        raise HTTPException(status_code=422, detail="Fixed tasks overlap.")
    from app.services.plans.timeline import compute_reality_check

    reality_check = compute_reality_check(result)

    return result, reality_check, draft_to_uuid


async def preview_today_draft(
    db: AsyncSession, user_id: UUID, request: TodayPreviewRequest
) -> TodayPreviewResponse:
    from fastapi import HTTPException

    user_settings = await db.scalar(
        select(UserSettings).where(UserSettings.user_id == user_id)
    )
    from app.ai.drafting.validators import check_today

    issues = check_today(request.draft)
    if issues:
        raise HTTPException(
            status_code=422,
            detail=[
                {
                    "loc": ["body", "draft"],
                    "msg": issue,
                    "type": "value_error",
                    "code": issue,
                }
                for issue in issues
            ],
        )
    user_tz = safe_timezone(user_settings.timezone if user_settings else "UTC")

    if request.draft.timezone != str(user_tz):
        raise HTTPException(
            status_code=422,
            detail="Draft timezone must match user timezone exactly.",
        )

    tz = user_tz
    current_local_date = datetime.now(tz).date()
    local_date = request.draft.planDate

    if local_date < current_local_date:
        raise HTTPException(status_code=422, detail="Cannot plan for a past date.")

    result, reality_check, draft_to_uuid = _normalize_and_schedule(
        request.draft, tz, local_date, user_id
    )
    uuid_to_draft = {v: k for k, v in draft_to_uuid.items()}

    blocks = []
    draft_tasks = {task.id: task for task in request.draft.tasks}
    for i, b in enumerate(result.blocks):
        draft_task_id = uuid_to_draft.get(b.task_id) if b.task_id else None
        draft_task = draft_tasks.get(draft_task_id) if draft_task_id else None
        blocks.append(
            TodayBlock(
                id=uuid4(),
                block_type="TASK"
                if b.task_id and b.block_type == "FIXED_EVENT"
                else b.block_type,
                task_id=b.task_id,
                title=b.title,
                planned_start_at=b.start_at,
                planned_end_at=b.end_at,
                position=i,
                status="PLANNED",
                is_locked=False,
                draft_task_id=draft_task_id,
                category=cast(
                    TaskCategory | None, draft_task.category if draft_task else None
                ),
                estimated_duration_minutes=(
                    draft_task.durationMin if draft_task else None
                ),
                importance=draft_task.importance if draft_task else None,
                preferred_break_duration_minutes=(
                    draft_task.breakAfterMin if draft_task else None
                ),
                source=(
                    "MANUAL"
                    if draft_task and draft_task.estimateSource == "USER"
                    else "AI"
                    if draft_task
                    else None
                ),
            )
        )

    unscheduled = []
    for ut_id in result.unscheduled_tasks:
        draft_tid = uuid_to_draft.get(ut_id) if ut_id else None
        title = None
        if draft_tid:
            for t in request.draft.tasks:
                if t.id == draft_tid:
                    title = t.title
                    break

        reason_code = None
        for r in result.reasons:
            if r.get("task_id") == ut_id:
                reason_code = r.get("code")
                break

        from app.schemas.today import UnscheduledTaskInfo

        unscheduled.append(
            UnscheduledTaskInfo(
                draft_task_id=draft_tid, reason=reason_code, title=title
            )
        )

    draft_json = request.draft.model_dump_json()
    existing_plan = await crud_daily_plan.get_by_date(db, user_id, local_date)
    version_str = await plan_version(
        db, existing_plan.id if existing_plan is not None else None
    )
    token = generate_hmac_token(user_id, draft_json, version_str)

    suggestions = []
    if reality_check == "OVERLOADED":
        from app.ai.context import build_context
        from app.ai.coach.coach import generate_overloaded_suggestions
        from datetime import datetime as dt, timezone as dt_timezone

        ctx = await build_context(db, user_id, dt.now(dt_timezone.utc))
        unsched_ids = [u.draft_task_id for u in unscheduled if u.draft_task_id]
        suggestions = generate_overloaded_suggestions(request.draft, ctx, unsched_ids)

    return TodayPreviewResponse(
        plan_date=local_date,
        timezone=str(tz),
        preview_token=token,
        reality_check=reality_check,
        blocks=blocks,
        unscheduled_tasks=unscheduled,
        reasons=result.reasons,
        suggestions=suggestions,
    )
