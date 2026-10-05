import hashlib
import logging
from datetime import date, datetime, timezone
from uuid import UUID

from fastapi.encoders import jsonable_encoder
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.time_utils import safe_timezone
from app.crud.crud_daily_plan import daily_plan as crud_daily_plan
from app.db.models.daily_plans import PlanBlock, PlanRevision, DailyPlan
from app.db.models.planning import PlanningSession
from app.db.models.tasks import Task
from app.db.models.users import UserSettings
from app.schemas.today import (
    TodaySaveRequest,
)

logger = logging.getLogger(__name__)
USABLE_PLAN_STATUSES = {"CONFIRMED", "ACTIVE", "COMPLETED"}


from app.core.preview_token import preview_token_claims
from app.services.plans.draft_preview import _normalize_and_schedule, _normalize_dt
from app.services.plans.today_query import get_today


async def _reusable_task(
    db: AsyncSession, user_id: UUID, raw_id: str | None
) -> Task | None:
    """An unfinished, unscheduled task of this user the draft carried in."""
    if not raw_id:
        return None
    try:
        task_id = UUID(raw_id)
    except ValueError:
        return None
    task = await db.scalar(
        select(Task).where(
            Task.id == task_id,
            Task.user_id == user_id,
            Task.status.in_(("DRAFT", "PENDING")),
        )
    )
    if task is None:
        return None
    still_scheduled = await db.scalar(
        select(func.count(PlanBlock.id)).where(PlanBlock.task_id == task.id)
    )
    return None if still_scheduled else task


async def _owned_template_id(
    db: AsyncSession, user_id: UUID, raw_id: str | None
) -> UUID | None:
    from app.db.models.tasks import RecurringTask

    if not raw_id:
        return None
    try:
        template_id = UUID(raw_id)
    except ValueError:
        return None
    return await db.scalar(
        select(RecurringTask.id).where(
            RecurringTask.id == template_id, RecurringTask.user_id == user_id
        )
    )


async def _materialize_task(
    db: AsyncSession,
    user_id: UUID,
    t_draft,
    day: date,
    tz,
    *,
    status: str | None = None,
) -> tuple[Task, bool]:
    """Create (or reuse the carried-in) task row for one draft task.

    Returns the task and whether an existing row was reused. A draft task
    with a recurrence also creates or reuses its repeating template.
    """
    from app.services import recurring_service

    template_id = await _owned_template_id(db, user_id, t_draft.recurringTaskId)
    if t_draft.recurrence is not None:
        template = await recurring_service.upsert_from_draft(
            db, user_id, t_draft, day, tz
        )
        template_id = template.id
    values = dict(
        title=t_draft.title,
        estimated_duration_minutes=t_draft.durationMin,
        priority=t_draft.priority,
        scheduling_type=t_draft.schedulingType,
        importance=t_draft.importance,
        category=t_draft.category,
        deadline_at=_normalize_dt(t_draft.deadline, tz) if t_draft.deadline else None,
        fixed_start_at=_normalize_dt(t_draft.fixedStart, tz)
        if t_draft.fixedStart
        else None,
        fixed_end_at=_normalize_dt(t_draft.fixedEnd, tz) if t_draft.fixedEnd else None,
        is_splittable=t_draft.splittable,
        preferred_break_duration_minutes=t_draft.breakAfterMin,
        planned_date=day,
        recurring_task_id=template_id,
    )
    existing = await _reusable_task(db, user_id, t_draft.sourceTaskId)
    if existing is not None:
        for key, value in values.items():
            setattr(existing, key, value)
        if status:
            existing.status = status
        return existing, True
    task = Task(
        user_id=user_id,
        source="MANUAL" if t_draft.estimateSource == "USER" else "AI",
        **values,
    )
    if status:
        task.status = status
    db.add(task)
    return task, False


async def save_today_draft(
    db: AsyncSession, user_id: UUID, request: TodaySaveRequest
) -> dict:

    from fastapi import HTTPException

    from app.db.models.daily_plans import (
        AvailabilityWindow,
        PlanBlock,
    )
    from app.db.models.tasks import Task, TaskDependency

    draft_json = request.draft.model_dump_json()
    token_claims = preview_token_claims(user_id, draft_json, request.preview_token)
    if token_claims is None:
        raise HTTPException(
            status_code=409,
            detail={
                "code": "PREVIEW_STALE",
                "message": "Draft has changed since last preview. Please preview again.",
            },
        )

    draft_hash = hashlib.sha256(draft_json.encode()).hexdigest()
    carried_source_ids = {
        task.sourceTaskId
        for task in [
            *request.draft.tasks,
            *(d.task for d in request.draft.deferred_tasks),
        ]
        if task.sourceTaskId
    }
    idempotency_key = (
        request.idempotency_key
        or hashlib.sha256(request.preview_token.encode()).hexdigest()
    )

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

    # Serialize all save attempts for this user.  The unique plan index is a
    # final database guard, while this lock makes duplicate requests return
    # the already-committed result instead of racing into an IntegrityError.
    from app.db.models.users import User

    await db.execute(select(User.id).where(User.id == user_id).with_for_update())

    result, reality_check, draft_to_uuid = _normalize_and_schedule(
        request.draft, tz, local_date, user_id
    )
    uuid_to_draft = {v: k for k, v in draft_to_uuid.items()}

    existing_plan = await crud_daily_plan.get_by_date(db, user_id, local_date)
    revision = None
    if existing_plan:
        revision = await db.scalar(
            select(PlanRevision)
            .where(PlanRevision.daily_plan_id == existing_plan.id)
            .order_by(PlanRevision.revision_number.desc())
            .limit(1)
        )
    current_version = (
        f"{existing_plan.id}:{revision.revision_number if revision else 0}"
        if existing_plan
        else "none"
    )
    idempotent_retry = bool(
        revision
        and revision.after_snapshot.get("draft_hash") == draft_hash
        and (
            revision.after_snapshot.get("idempotency_key", idempotency_key)
            == idempotency_key
            or token_claims["plan_version"] == current_version
        )
    )
    if (
        revision
        and revision.after_snapshot.get("idempotency_key") == idempotency_key
        and revision.after_snapshot.get("draft_hash") != draft_hash
    ):
        raise HTTPException(
            status_code=409,
            detail={
                "code": "IDEMPOTENCY_KEY_REUSED",
                "message": "This save key was already used for a different draft.",
            },
        )
    if token_claims["plan_version"] != current_version and not idempotent_retry:
        raise HTTPException(
            status_code=409,
            detail={
                "code": "PREVIEW_STALE",
                "message": "The saved plan changed after this preview. Generate a new preview before saving.",
            },
        )

    session: PlanningSession | None = None
    if request.session_id:
        session = await db.scalar(
            select(PlanningSession).where(
                PlanningSession.id == request.session_id,
                PlanningSession.user_id == user_id,
            )
        )
        if not session:
            raise HTTPException(status_code=404, detail="Planning session not found")
        if session.status not in {"OPEN", "AWAITING_CLARIFICATION"} and not (
            session.status == "COMPLETED" and idempotent_retry
        ):
            raise HTTPException(
                status_code=409, detail="Session is not open for saving"
            )

    # Idempotency Check
    if existing_plan:
        if idempotent_retry:
            if session is not None:
                session.status = "COMPLETED"
                session.closed_at = session.closed_at or datetime.now(timezone.utc)
                await db.commit()
            return await get_today(db, user_id, local_date)
        if not request.replace_existing:
            raise HTTPException(
                status_code=409,
                detail={
                    "code": "PLAN_EXISTS",
                    "message": "A plan already exists for this date. Confirm replacement before saving.",
                },
            )

        # Completed and elapsed history is immutable. Replacement only
        # removes the unfinished future schedule.
        preserved_blocks = []
        blocks_result = await db.execute(
            select(PlanBlock).where(PlanBlock.daily_plan_id == existing_plan.id)
        )
        for block in blocks_result.scalars():
            if block.status == "COMPLETED" or block.planned_end_at <= datetime.now(
                timezone.utc
            ):
                preserved_blocks.append(block)
            else:
                await db.delete(block)

        windows_result = await db.execute(
            select(AvailabilityWindow).where(
                AvailabilityWindow.daily_plan_id == existing_plan.id
            )
        )
        for window in windows_result.scalars():
            await db.delete(window)

        # Delete AI tasks from previous save if not completed
        if revision and "created_task_ids" in revision.after_snapshot:
            prev_task_ids_str = revision.after_snapshot["created_task_ids"]
            if prev_task_ids_str:
                from uuid import UUID

                from app.db.models.focus import FocusRun

                prev_task_ids = [
                    UUID(pid) if isinstance(pid, str) else pid
                    for pid in prev_task_ids_str
                ]
                tasks_res = await db.execute(
                    select(Task).where(Task.id.in_(prev_task_ids))
                )
                for t in tasks_res.scalars():
                    # A task the new draft carries in again is reused below.
                    if t.status != "COMPLETED" and str(t.id) not in carried_source_ids:
                        has_focus = await db.scalar(
                            select(func.count(FocusRun.id)).where(
                                FocusRun.task_id == t.id
                            )
                        )
                        deps_res = await db.execute(
                            select(TaskDependency).where(
                                (TaskDependency.task_id == t.id)
                                | (TaskDependency.depends_on_task_id == t.id)
                            )
                        )
                        for dep in deps_res.scalars():
                            await db.delete(dep)

                        if not has_focus:
                            await db.delete(t)
                        else:
                            t.status = "CANCELLED"
                            db.add(t)

        existing_plan.reality_check = reality_check
        existing_plan.timezone_snapshot = str(tz)
        if request.session_id:
            existing_plan.planning_session_id = request.session_id
        plan = existing_plan
    else:
        revision = None
        preserved_blocks = []
        plan = DailyPlan(
            user_id=user_id,
            plan_date=local_date,
            status="ACTIVE",
            confirmed_at=datetime.now(timezone.utc),
            planning_session_id=request.session_id,
            reality_check=reality_check,
            timezone_snapshot=str(tz),
        )
        db.add(plan)

    await db.flush()

    for window in request.draft.windows:
        start_at = datetime.strptime(window.start, "%H:%M").replace(
            year=local_date.year,
            month=local_date.month,
            day=local_date.day,
            tzinfo=tz,
        )
        end_at = datetime.strptime(window.end, "%H:%M").replace(
            year=local_date.year,
            month=local_date.month,
            day=local_date.day,
            tzinfo=tz,
        )
        db.add(
            AvailabilityWindow(
                daily_plan_id=plan.id,
                available_start_at=start_at,
                available_end_at=end_at,
            )
        )

    task_id_map = {}
    new_tasks = []
    reused_task_ids: list[str] = []
    for t_draft in request.draft.tasks:
        new_task, reused = await _materialize_task(db, user_id, t_draft, local_date, tz)
        if reused:
            reused_task_ids.append(str(new_task.id))
        new_tasks.append((t_draft, new_task))

    await db.flush()

    for t_draft, new_task in new_tasks:
        task_id_map[t_draft.id] = new_task.id

    for t_draft, new_task in new_tasks:
        for dep_draft_id in t_draft.dependencies:
            if dep_draft_id in task_id_map:
                db.add(
                    TaskDependency(
                        task_id=new_task.id,
                        depends_on_task_id=task_id_map[dep_draft_id],
                    )
                )

    await db.flush()

    unscheduled = []
    for ut_id in result.unscheduled_tasks:
        draft_tid = uuid_to_draft.get(ut_id) if ut_id else None
        title = None
        if draft_tid:
            for candidate_draft_task in request.draft.tasks:
                if candidate_draft_task.id == draft_tid:
                    title = candidate_draft_task.title
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

    # --- Work for later days ---
    # Tasks named for another day are stored as unscheduled work for that
    # day instead of an empty "active" plan: an empty plan used to block
    # planning that day (PLAN_EXISTS), and replacing it deleted the tasks.
    # They come back in the draft automatically when that day is planned.
    deferred_task_ids: list[str] = []
    for deferred in request.draft.deferred_tasks:
        deferred_task, reused = await _materialize_task(
            db, user_id, deferred.task, deferred.targetDate, tz, status="PENDING"
        )
        await db.flush()
        (reused_task_ids if reused else deferred_task_ids).append(str(deferred_task.id))

    blocks_created = []
    first_position = max((block.position for block in preserved_blocks), default=-1) + 1
    for idx, block_item in enumerate(result.blocks):
        t_id = None
        if block_item.task_id:
            draft_task_id = uuid_to_draft.get(block_item.task_id)
            t_id = task_id_map.get(draft_task_id) if draft_task_id is not None else None

        block = PlanBlock(
            daily_plan_id=plan.id,
            block_type="TASK"
            if t_id and block_item.block_type == "FIXED_EVENT"
            else block_item.block_type,
            planned_start_at=block_item.start_at,
            planned_end_at=block_item.end_at,
            task_id=t_id,
            title=block_item.title,
            position=first_position + idx,
            is_locked=False,
        )
        db.add(block)
        blocks_created.append(block)

    last_rev = await db.scalar(
        select(func.max(PlanRevision.revision_number)).where(
            PlanRevision.daily_plan_id == plan.id
        )
    )
    rev_num = (last_rev or 0) + 1

    preserved_ids = {str(block.task_id) for block in preserved_blocks if block.task_id}
    previous_created_ids = (
        revision.after_snapshot.get("created_task_ids", []) if revision else []
    )
    previous_draft_map = (
        revision.after_snapshot.get("task_draft_map", {}) if revision else {}
    )
    created_task_ids = [pid for pid in previous_created_ids if pid in preserved_ids]
    # Reused carried-in tasks are not "created" by this save: replacing the
    # plan later must return them to their day, not delete them.
    reused = set(reused_task_ids)
    created_task_ids.extend(
        str(new_task.id) for _, new_task in new_tasks if str(new_task.id) not in reused
    )
    task_draft_map = {
        task_id: draft_id
        for task_id, draft_id in previous_draft_map.items()
        if task_id in preserved_ids
    }
    task_draft_map.update(
        {str(new_task.id): t_draft.id for t_draft, new_task in new_tasks}
    )

    rev = PlanRevision(
        daily_plan_id=plan.id,
        revision_number=rev_num,
        reason="AI_DRAFT_APPLIED",
        trigger_type="MANUAL_EDIT",
        generated_by="AI",
        before_snapshot={},
        after_snapshot={
            "blocks": len(blocks_created),
            "draft_hash": draft_hash,
            "idempotency_key": idempotency_key,
            "created_task_ids": created_task_ids,
            "reused_task_ids": reused_task_ids,
            "deferred_task_ids": deferred_task_ids,
            "task_draft_map": task_draft_map,
            "unscheduled_tasks": [u.model_dump(mode="json") for u in unscheduled],
            "reasons": jsonable_encoder(result.reasons),
        },
    )
    db.add(rev)

    if session is not None:
        session.status = "COMPLETED"
        session.closed_at = datetime.now(timezone.utc)

    await db.commit()

    db.expire(plan, ["plan_blocks"])
    return await get_today(db, user_id, local_date)
