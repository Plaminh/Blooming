import logging
from datetime import date, datetime, timezone
from uuid import UUID

from fastapi.encoders import jsonable_encoder
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.scheduler import DeterministicScheduler, ScheduleTask, ScheduleWindow
from app.core.time_utils import safe_timezone
from app.crud.crud_daily_plan import daily_plan as crud_daily_plan
from app.db.models.daily_plans import PlanBlock, PlanRevision
from app.db.models.tasks import Task
from app.db.models.users import UserSettings

logger = logging.getLogger(__name__)
USABLE_PLAN_STATUSES = {"CONFIRMED", "ACTIVE", "COMPLETED"}


from app.services.plans.task_status import sync_daily_plan_completion
from app.services.plans.today_query import get_today


async def replan_today(
    db: AsyncSession, user_id: UUID, local_date: date | None = None, commit: bool = True
) -> dict:
    from app.db.models.users import User

    await db.execute(select(User.id).where(User.id == user_id).with_for_update())
    settings = await db.scalar(
        select(UserSettings).where(UserSettings.user_id == user_id)
    )
    now = datetime.now(timezone.utc)
    if local_date is None:
        local_date = now.astimezone(
            safe_timezone(settings.timezone if settings else "UTC")
        ).date()

    plan = await crud_daily_plan.get_by_date(db, user_id, local_date)
    if not plan or plan.status not in USABLE_PLAN_STATUSES:
        return {"plan_date": local_date, "status": "NO_PLAN"}
    await db.refresh(plan, ["plan_blocks", "availability_windows"])
    blocks = list(plan.plan_blocks)
    previous = await db.scalar(
        select(PlanRevision)
        .where(PlanRevision.daily_plan_id == plan.id)
        .order_by(PlanRevision.revision_number.desc())
        .limit(1)
    )
    pending_ids = _snapshot_task_ids(previous.after_snapshot) if previous else set()
    # Work moved to today from an earlier day joins the replan too.
    from app.ai.carryover import pending_tasks_for_day

    carried_ids = {
        task.id for task in await pending_tasks_for_day(db, user_id, local_date)
    }
    pending_ids |= carried_ids

    task_ids = {b.task_id for b in blocks if b.task_id} | pending_ids
    tasks = {
        t.id: t
        for t in (
            await db.scalars(
                select(Task)
                .options(selectinload(Task.dependencies))
                .where(Task.id.in_(task_ids), Task.user_id == user_id)
            )
        ).all()
    }
    from app.db.models.focus import FocusRun

    active_task_ids = set(
        (
            await db.scalars(
                select(FocusRun.task_id).where(
                    FocusRun.user_id == user_id,
                    FocusRun.status.in_(("READY", "FOCUSING", "PAUSED")),
                )
            )
        ).all()
    )
    preserved, eligible = [], []
    for block in blocks:
        task = tasks.get(block.task_id) if block.task_id is not None else None
        terminal = block.status in ("COMPLETED", "SKIPPED", "CANCELLED") or (
            task and task.status in ("COMPLETED", "SKIPPED", "CANCELLED")
        )
        historical = block.planned_start_at < now
        fixed_remaining = block.planned_end_at > now and (
            block.is_locked
            or block.status == "ACTIVE"
            or block.task_id in active_task_ids
            or block.block_type == "FIXED_EVENT"
            or (task and task.scheduling_type == "FIXED")
        )
        if terminal or historical or fixed_remaining:
            preserved.append(block)
        else:
            eligible.append(block)

    # Subtract reservations even when they straddle now or an availability boundary.
    windows = [
        ScheduleWindow(max(w.available_start_at, now), w.available_end_at)
        for w in plan.availability_windows
        if w.available_end_at > now
    ]
    for block in preserved:
        task = tasks.get(block.task_id) if block.task_id is not None else None
        if block.status in ("COMPLETED", "SKIPPED", "CANCELLED") or (
            task is not None and task.status in ("COMPLETED", "SKIPPED", "CANCELLED")
        ):
            continue
        gaps = []
        for window in windows:
            if (
                block.planned_end_at <= window.start_at
                or block.planned_start_at >= window.end_at
            ):
                gaps.append(window)
            else:
                if window.start_at < block.planned_start_at:
                    gaps.append(ScheduleWindow(window.start_at, block.planned_start_at))
                if block.planned_end_at < window.end_at:
                    gaps.append(ScheduleWindow(block.planned_end_at, window.end_at))
        windows = gaps

    completed_ids = set(
        (
            await db.scalars(
                select(Task.id).where(
                    Task.user_id == user_id, Task.status == "COMPLETED"
                )
            )
        ).all()
    )
    schedule_tasks = []
    candidate_ids = {b.task_id for b in eligible if b.task_id} | pending_ids
    for task_id in sorted(candidate_ids, key=str):
        task = tasks.get(task_id)
        if not task or task.status not in ("DRAFT", "PENDING", "IN_PROGRESS"):
            continue
        reserved_minutes = sum(
            max(
                0,
                int(
                    (
                        b.planned_end_at
                        - (
                            b.planned_start_at
                            if b.status == "COMPLETED"
                            else max(b.planned_start_at, now)
                        )
                    ).total_seconds()
                    // 60
                ),
            )
            for b in preserved
            if b.task_id == task_id
        )
        remaining_minutes = max(0, task.estimated_duration_minutes - reserved_minutes)
        if remaining_minutes == 0:
            continue
        schedule_tasks.append(
            ScheduleTask(
                id=task.id,
                title=task.title,
                estimated_duration_minutes=remaining_minutes,
                priority=task.priority,
                scheduling_type="FLEXIBLE",
                created_at=task.created_at,
                is_splittable=task.is_splittable,
                min_split_duration_minutes=task.min_split_duration_minutes,
                preferred_break_duration_minutes=task.preferred_break_duration_minutes,
                dependencies=[
                    d.depends_on_task_id
                    for d in task.dependencies
                    if d.depends_on_task_id not in completed_ids
                ],
            )
        )
    reserved_ends: dict[UUID, datetime] = {}
    for block in preserved:
        if (
            block.task_id
            and block.task_id not in completed_ids
            and block.planned_end_at > now
            and block.status not in ("SKIPPED", "CANCELLED")
        ):
            reserved_ends[block.task_id] = max(
                reserved_ends.get(block.task_id, now), block.planned_end_at
            )
    result = DeterministicScheduler().schedule(
        schedule_tasks, windows, satisfied_dependencies=reserved_ends
    )
    for block in eligible:
        await db.delete(block)
    await db.flush()
    # Preserve historical rows, including their positions; new rows receive unused positions.
    position = max((b.position for b in preserved), default=-1) + 1
    for offset, scheduled_block in enumerate(result.blocks):
        db.add(
            PlanBlock(
                daily_plan_id=plan.id,
                task_id=scheduled_block.task_id,
                block_type=scheduled_block.block_type,
                title=scheduled_block.title,
                planned_start_at=scheduled_block.start_at,
                planned_end_at=scheduled_block.end_at,
                position=position + offset,
                status="PLANNED",
                created_by="SCHEDULER",
            )
        )
    plan.reality_check = (
        "OVERLOADED"
        if result.unscheduled_tasks
        else (
            "COMFORTABLE"
            if result.workload_minutes <= result.available_minutes * 0.8
            else "TIGHT"
        )
    )
    db.add(
        PlanRevision(
            daily_plan_id=plan.id,
            revision_number=(previous.revision_number if previous else 0) + 1,
            reason="Replan unfinished work",
            trigger_type="RECOVERY",
            generated_by="SYSTEM",
            before_snapshot={"block_ids": [str(b.id) for b in blocks]},
            after_snapshot=jsonable_encoder(
                {
                    "unscheduled_tasks": result.unscheduled_tasks,
                    "reasons": result.reasons,
                    # Carry the save-time bookkeeping forward: a later
                    # replace needs it to remove only this plan's tasks,
                    # and Today needs it to map blocks to draft tasks.
                    **{
                        key: previous.after_snapshot[key]
                        for key in (
                            "created_task_ids",
                            "reused_task_ids",
                            "task_draft_map",
                        )
                        if previous is not None and key in previous.after_snapshot
                    },
                }
            ),
        )
    )
    await db.flush()
    await db.refresh(plan, ["plan_blocks"])
    await sync_daily_plan_completion(db, plan.id)
    if commit:
        await db.commit()
    logger.info(
        "replan_result",
        extra={
            "unscheduled_count": len(result.unscheduled_tasks),
            "scheduled_count": len(result.blocks),
            "committed": commit,
        },
    )
    return await get_today(db, user_id, local_date)


def _snapshot_task_ids(snapshot: dict, key: str = "unscheduled_tasks") -> set:
    from uuid import UUID

    draft_to_task = {
        draft_id: task_id
        for task_id, draft_id in (snapshot.get("task_draft_map") or {}).items()
    }
    ids = set()
    for entry in snapshot.get(key) or []:
        raw = None
        if isinstance(entry, str):
            raw = entry
        elif isinstance(entry, dict):
            raw = entry.get("task_id") or draft_to_task.get(entry.get("draft_task_id"))
        if raw:
            try:
                ids.add(UUID(str(raw)))
            except ValueError:
                continue
    return ids
