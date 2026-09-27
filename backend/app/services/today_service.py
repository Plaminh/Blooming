import hashlib
import hmac
import logging
from datetime import date, datetime, timezone
from typing import cast
from uuid import UUID, uuid4

from fastapi.encoders import jsonable_encoder
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.config import settings
from app.core.errors import ResourceNotFoundError, UnauthorizedOwnershipError
from app.core.scheduler import DeterministicScheduler, ScheduleTask, ScheduleWindow
from app.core.time_utils import safe_timezone
from app.crud.crud_daily_plan import daily_plan as crud_daily_plan
from app.crud.crud_task import task as crud_task
from app.db.models.daily_plans import PlanBlock, PlanRevision
from app.db.models.planning import PlanningSession
from app.db.models.tasks import Task
from app.db.models.users import UserSettings
from app.schemas.today import (
    TodayBlock,
    TodayPreviewRequest,
    TodayPreviewResponse,
    TodaySaveRequest,
    TodayTaskEdit,
    TodayTaskStatusUpdate,
)
from app.schemas.planning import TaskCategory

logger = logging.getLogger(__name__)
USABLE_PLAN_STATUSES = {"CONFIRMED", "ACTIVE", "COMPLETED"}


def _snapshot_task_ids(snapshot: dict, key: str = "unscheduled_tasks") -> set[UUID]:
    """Task ids named by a revision's unscheduled list.

    Replan revisions store bare UUID strings, save revisions store objects
    keyed by draft task id; both shapes must be readable by the next replan.
    """
    draft_to_task = {
        draft_id: task_id
        for task_id, draft_id in (snapshot.get("task_draft_map") or {}).items()
    }
    ids: set[UUID] = set()
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


class TodayService:
    @staticmethod
    async def _pending_task_infos(
        db: AsyncSession, user_id: UUID, day: date
    ) -> list[dict]:
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

    async def _reusable_task(
        self, db: AsyncSession, user_id: UUID, raw_id: str | None, day: date
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
        from app.ai.carryover import scheduled_on

        still_scheduled = await db.scalar(
            select(func.count()).select_from(Task).where(Task.id == task.id, scheduled_on(day))
        )
        return None if still_scheduled else task

    async def _owned_template_id(
        self, db: AsyncSession, user_id: UUID, raw_id: str | None
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
        self,
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

        template_id = await self._owned_template_id(db, user_id, t_draft.recurringTaskId)
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
            deadline_at=self._normalize_dt(t_draft.deadline, tz)
            if t_draft.deadline
            else None,
            fixed_start_at=self._normalize_dt(t_draft.fixedStart, tz)
            if t_draft.fixedStart
            else None,
            fixed_end_at=self._normalize_dt(t_draft.fixedEnd, tz)
            if t_draft.fixedEnd
            else None,
            is_splittable=t_draft.splittable,
            preferred_break_duration_minutes=t_draft.breakAfterMin,
            planned_date=day,
            recurring_task_id=template_id,
        )
        existing = await self._reusable_task(db, user_id, t_draft.sourceTaskId, day)
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

    async def carry_over_unfinished(
        self, db: AsyncSession, user_id: UUID, *, commit: bool = True
    ) -> dict:
        """Move today's unfinished work to tomorrow's waiting list.

        Tasks keep their identity (history, focus runs, rewards) and become
        PENDING for tomorrow; tomorrow's draft then carries them in. Only
        future blocks are removed from today, so today's history stays intact.
        Tasks with a running focus session are left alone.
        """
        from datetime import timedelta

        from app.db.models.focus import FocusRun
        from app.db.models.users import User

        await db.execute(select(User.id).where(User.id == user_id).with_for_update())
        user_settings = await db.scalar(
            select(UserSettings).where(UserSettings.user_id == user_id)
        )
        tz = safe_timezone(user_settings.timezone if user_settings else "UTC")
        now = datetime.now(timezone.utc)
        local_date = now.astimezone(tz).date()
        target_date = local_date + timedelta(days=1)
        plan = await crud_daily_plan.get_by_date(db, user_id, local_date)
        if not plan or plan.status not in USABLE_PLAN_STATUSES:
            return {"target_date": target_date, "moved": []}

        revision = await db.scalar(
            select(PlanRevision)
            .where(PlanRevision.daily_plan_id == plan.id)
            .order_by(PlanRevision.revision_number.desc())
            .limit(1)
        )
        candidate_ids = {b.task_id for b in plan.plan_blocks if b.task_id}
        if revision is not None:
            candidate_ids |= _snapshot_task_ids(revision.after_snapshot)
        if not candidate_ids:
            return {"target_date": target_date, "moved": []}
        focusing = set(
            (
                await db.scalars(
                    select(FocusRun.task_id).where(
                        FocusRun.user_id == user_id,
                        FocusRun.status.in_(("READY", "FOCUSING", "PAUSED")),
                    )
                )
            ).all()
        )
        tasks = (
            await db.scalars(
                select(Task)
                .where(Task.id.in_(candidate_ids), Task.user_id == user_id)
                .order_by(Task.created_at, Task.id)
            )
        ).all()
        moved = []
        for task in tasks:
            if task.status not in ("DRAFT", "PENDING", "IN_PROGRESS") or task.id in focusing:
                continue
            if task.planned_date is not None and task.planned_date != local_date:
                continue  # Already moved to another day; past blocks remain here.
            task.status = "PENDING"
            task.planned_date = target_date
            # Yesterday's clock times rarely hold tomorrow; the new draft
            # schedules the task flexibly unless the user fixes it again.
            task.scheduling_type = "FLEXIBLE"
            task.fixed_start_at = None
            task.fixed_end_at = None
            task.deadline_at = None
            for block in list(plan.plan_blocks):
                if (
                    block.task_id == task.id
                    and block.planned_start_at >= now
                    and block.status not in ("COMPLETED", "ACTIVE")
                ):
                    await db.delete(block)
            moved.append({"task_id": str(task.id), "title": task.title})
        await db.flush()
        if commit:
            await db.commit()
        logger.info("carry_over_result", extra={"moved_count": len(moved)})
        return {"target_date": target_date, "moved": moved}

    async def _get_plan_for_preview_validation(
        self, db: AsyncSession, user_id: UUID, plan_date: date
    ):
        """Ownership-scoped lookup used when restoring a persisted preview."""
        return await crud_daily_plan.get_by_date(db, user_id, plan_date)

    async def get_today_draft(
        self, db: AsyncSession, user_id: UUID, local_date: date | None = None
    ) -> dict:
        from app.schemas.drafts import (
            TodayDraft, TaskDraft, AvailabilityWindowDraft,
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
                deferred_tasks=[]
            ).model_dump(mode="json")
            
        await db.refresh(plan, ["plan_blocks", "availability_windows"])
        
        # Load tasks from blocks
        task_ids = {b.task_id for b in plan.plan_blocks if b.task_id}
        tasks = {}
        if task_ids:
            tasks_list = (await db.scalars(
                select(Task)
                .options(selectinload(Task.dependencies))
                .where(Task.id.in_(task_ids))
            )).all()
            tasks = {t.id: t for t in tasks_list}
            
        draft_tasks = []
        for b in sorted(plan.plan_blocks, key=lambda x: x.position):
            if b.block_type == "TASK" and b.task_id and b.task_id in tasks:
                t = tasks[b.task_id]
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
                        dependencies=[str(d.depends_on_task_id) for d in t.dependencies],
                        splittable=t.is_splittable,
                        sourceTaskId=str(t.id),
                        recurringTaskId=str(t.recurring_task_id) if t.recurring_task_id else None,
                    )
                )

        windows = []
        for w in plan.availability_windows:
            windows.append(
                AvailabilityWindowDraft(
                    start=w.available_start_at.astimezone(tz).strftime("%H:%M"),
                    end=w.available_end_at.astimezone(tz).strftime("%H:%M")
                )
            )

        draft = TodayDraft(
            planDate=plan.plan_date,
            timezone=plan.timezone_snapshot,
            windows=windows,
            tasks=draft_tasks,
            deferred_tasks=[]
        )
        return draft.model_dump(mode="json")

    async def get_today(
        self, db: AsyncSession, user_id: UUID, local_date: date | None = None
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
                "pending_tasks": await self._pending_task_infos(db, user_id, local_date),
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
                "draft_task_id": task_draft_map.get(str(b.task_id))
                if b.task_id
                else None,
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

    async def update_task_from_today(
        self, db: AsyncSession, user_id: UUID, task_id: UUID, obj_in: TodayTaskEdit
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
        self,
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
        if commit:
            await db.commit()
        return task_db

    async def replan_today(
        self, db: AsyncSession, user_id: UUID, local_date: date | None = None, commit: bool = True
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
                task is not None
                and task.status in ("COMPLETED", "SKIPPED", "CANCELLED")
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
                        gaps.append(
                            ScheduleWindow(window.start_at, block.planned_start_at)
                        )
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
            remaining_minutes = max(
                0, task.estimated_duration_minutes - reserved_minutes
            )
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
        return await self.get_today(db, user_id, local_date)

    def _generate_hmac_token(
        self, user_id: UUID, draft_json: str, plan_version: str | None = None
    ) -> str:
        import base64
        import json
        import time

        secret = settings.SECRET_KEY.get_secret_value().encode()
        expiry = int(time.time()) + 3600 * 24  # 24 hours
        purpose = "today_preview"

        # A preview is a capability for one user, one canonical draft and the
        # plan revision that existed when scheduling ran.  Binding the revision
        # prevents a confirmation dialog left open in one tab from silently
        # replacing a newer plan saved in another tab.
        version = plan_version or "none"
        msg = f"{user_id}:{purpose}:{expiry}:{version}:{draft_json}".encode()
        signature = hmac.new(secret, msg, hashlib.sha256).hexdigest()

        token_data = {"exp": expiry, "sig": signature, "plan_version": version}
        return base64.urlsafe_b64encode(json.dumps(token_data).encode()).decode()

    def _preview_token_claims(
        self, user_id: UUID, draft_json: str, token: str
    ) -> dict[str, str | int] | None:
        import base64
        import json
        import time

        try:
            token_data = json.loads(base64.urlsafe_b64decode(token.encode()).decode())
            expiry = token_data["exp"]
            signature = token_data["sig"]
            version = str(token_data.get("plan_version", "none"))
        except Exception:
            return None

        if time.time() > expiry:
            return None

        secret = settings.SECRET_KEY.get_secret_value().encode()
        purpose = "today_preview"
        msg = f"{user_id}:{purpose}:{expiry}:{version}:{draft_json}".encode()
        expected = hmac.new(secret, msg, hashlib.sha256).hexdigest()
        if not hmac.compare_digest(expected, signature):
            return None
        return {"exp": int(expiry), "plan_version": version}

    def _verify_hmac_token(self, user_id: UUID, draft_json: str, token: str) -> bool:
        return self._preview_token_claims(user_id, draft_json, token) is not None

    @staticmethod
    async def _plan_version(db: AsyncSession, plan_id: UUID | None) -> str:
        if plan_id is None:
            return "none"
        revision = await db.scalar(
            select(PlanRevision)
            .where(PlanRevision.daily_plan_id == plan_id)
            .order_by(PlanRevision.revision_number.desc())
            .limit(1)
        )
        return f"{plan_id}:{revision.revision_number if revision else 0}"

    def _normalize_dt(self, dt, tz):
        from datetime import date, datetime, time

        if not isinstance(dt, date) and not isinstance(dt, datetime):
            return dt
        if not isinstance(dt, datetime):
            # date-only, end-of-day rule
            dt = datetime.combine(dt, time(23, 59, 59))
        if dt.tzinfo is None:
            return dt.replace(tzinfo=tz)
        return dt.astimezone(tz)

    def _normalize_and_schedule(self, draft, tz, local_date, user_id):
        import uuid
        from datetime import datetime, timedelta

        from app.core.scheduler import (
            DeterministicScheduler,
            ScheduleTask,
            ScheduleWindow,
        )

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
                    fixed_start_at=self._normalize_dt(t.fixedStart, tz)
                    if t.fixedStart
                    else None,
                    fixed_end_at=self._normalize_dt(t.fixedEnd, tz)
                    if t.fixedEnd
                    else None,
                    dependencies=[
                        draft_to_uuid[d] for d in t.dependencies if d in draft_to_uuid
                    ],
                )
            )

        result = DeterministicScheduler().schedule(tasks, windows)
        if any(reason["code"] == "FIXED_TASK_OVERLAP" for reason in result.reasons):
            from fastapi import HTTPException

            raise HTTPException(status_code=422, detail="Fixed tasks overlap.")
        reality_check = (
            "OVERLOADED"
            if result.unscheduled_tasks
            else (
                "COMFORTABLE"
                if result.workload_minutes <= result.available_minutes * 0.8
                else "TIGHT"
            )
        )

        return result, reality_check, draft_to_uuid

    async def preview_today_draft(
        self, db: AsyncSession, user_id: UUID, request: TodayPreviewRequest
    ) -> TodayPreviewResponse:
        from fastapi import HTTPException

        from app.db.models.users import UserSettings

        user_settings = await db.scalar(
            select(UserSettings).where(UserSettings.user_id == user_id)
        )
        from app.ai.validators import check_today

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

        result, reality_check, draft_to_uuid = self._normalize_and_schedule(
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
        plan_version = await self._plan_version(
            db, existing_plan.id if existing_plan is not None else None
        )
        token = self._generate_hmac_token(user_id, draft_json, plan_version)

        suggestions = []
        if reality_check == "OVERLOADED":
            from app.ai.context import build_context
            from app.ai.coach import generate_overloaded_suggestions
            from datetime import datetime as dt, timezone as dt_timezone

            ctx = await build_context(db, user_id, dt.now(dt_timezone.utc))
            unsched_ids = [u.draft_task_id for u in unscheduled if u.draft_task_id]
            suggestions = generate_overloaded_suggestions(
                request.draft, ctx, unsched_ids
            )

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

    async def save_today_draft(
        self, db: AsyncSession, user_id: UUID, request: TodaySaveRequest
    ) -> dict:
        import hashlib

        from fastapi import HTTPException

        from app.db.models.daily_plans import (
            AvailabilityWindow,
            DailyPlan,
            PlanBlock,
            PlanRevision,
        )
        from app.db.models.tasks import Task, TaskDependency
        from app.db.models.users import UserSettings

        draft_json = request.draft.model_dump_json()
        token_claims = self._preview_token_claims(
            user_id, draft_json, request.preview_token
        )
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
            for task in [*request.draft.tasks, *(d.task for d in request.draft.deferred_tasks)]
            if task.sourceTaskId
        }
        idempotency_key = (
            request.idempotency_key
            or hashlib.sha256(request.preview_token.encode()).hexdigest()
        )

        user_settings = await db.scalar(
            select(UserSettings).where(UserSettings.user_id == user_id)
        )
        from app.ai.validators import check_today

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

        result, reality_check, draft_to_uuid = self._normalize_and_schedule(
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
                raise HTTPException(
                    status_code=404, detail="Planning session not found"
                )
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
                return await self.get_today(db, user_id, local_date)
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

                    prev_task_ids = [
                        UUID(pid) if isinstance(pid, str) else pid
                        for pid in prev_task_ids_str
                    ]
                    tasks_res = await db.execute(
                        select(Task).where(Task.id.in_(prev_task_ids))
                    )
                    for t in tasks_res.scalars():
                        # A task the new draft carries in again is reused below.
                        moved_elsewhere = (
                            t.planned_date is not None and t.planned_date != local_date
                        )
                        if (
                            t.status != "COMPLETED"
                            and str(t.id) not in carried_source_ids
                            and not moved_elsewhere
                        ):
                            deps_res = await db.execute(
                                select(TaskDependency).where(
                                    (TaskDependency.task_id == t.id)
                                    | (TaskDependency.depends_on_task_id == t.id)
                                )
                            )
                            for dep in deps_res.scalars():
                                await db.delete(dep)
                            await db.delete(t)

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
            new_task, reused = await self._materialize_task(
                db, user_id, t_draft, local_date, tz
            )
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
            deferred_task, reused = await self._materialize_task(
                db, user_id, deferred.task, deferred.targetDate, tz, status="PENDING"
            )
            await db.flush()
            (reused_task_ids if reused else deferred_task_ids).append(
                str(deferred_task.id)
            )

        blocks_created = []
        first_position = (
            max((block.position for block in preserved_blocks), default=-1) + 1
        )
        for idx, block_item in enumerate(result.blocks):
            t_id = None
            if block_item.task_id:
                draft_task_id = uuid_to_draft.get(block_item.task_id)
                t_id = (
                    task_id_map.get(draft_task_id)
                    if draft_task_id is not None
                    else None
                )

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

        preserved_ids = {
            str(block.task_id) for block in preserved_blocks if block.task_id
        }
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
        return await self.get_today(db, user_id, local_date)


today_service = TodayService()
