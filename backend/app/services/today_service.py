from datetime import date, datetime, timezone
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.errors import ResourceNotFoundError, UnauthorizedOwnershipError
from app.core.scheduler import DeterministicScheduler, ScheduleTask, ScheduleWindow
from app.core.time_utils import safe_timezone
from app.crud.crud_daily_plan import daily_plan as crud_daily_plan
from app.crud.crud_task import task as crud_task
from app.db.models.daily_plans import PlanBlock
from app.db.models.tasks import Task
from app.db.models.users import UserSettings
from app.schemas.today import TodayTaskEdit, TodayTaskStatusUpdate


class TodayService:
    async def get_today(
        self, db: AsyncSession, user_id: UUID, local_date: date | None = None
    ) -> dict:
        if local_date is None:
            settings = await db.scalar(
                select(UserSettings).where(UserSettings.user_id == user_id)
            )
            tz = safe_timezone(settings.timezone if settings else "UTC")
            local_date = datetime.now(tz).date()

        plan = await crud_daily_plan.get_by_date(db, user_id, local_date)
        if not plan or plan.status == "DRAFT":
            return {"plan_date": local_date, "status": "NO_PLAN"}

        blocks = sorted(plan.plan_blocks, key=lambda b: b.planned_start_at)

        block_dicts = []
        for b in blocks:
            b_dict = {
                "id": b.id,
                "block_type": b.block_type,
                "task_id": b.task_id,
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
            }
            block_dicts.append(b_dict)

        return {
            "plan_date": plan.plan_date,
            "status": plan.status,
            "reality_check": plan.reality_check,
            "blocks": block_dicts,
        }

    async def update_task_from_today(
        self, db: AsyncSession, user_id: UUID, task_id: UUID, obj_in: TodayTaskEdit
    ) -> Task:
        task_db = await crud_task.get_with_plan_blocks(db, id=task_id)
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
        task_db = await crud_task.get_with_plan_blocks(db, id=task_id)
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
        self, db: AsyncSession, user_id: UUID, commit: bool = True
    ) -> dict:
        from app.core.errors import ValidationError
        from app.db.models.users import User

        await db.execute(select(User.id).where(User.id == user_id).with_for_update())
        settings = await db.scalar(
            select(UserSettings).where(UserSettings.user_id == user_id)
        )
        now = datetime.now(timezone.utc)
        local_date = now.astimezone(
            safe_timezone(settings.timezone if settings else "UTC")
        ).date()
        plan = await crud_daily_plan.get_by_date(db, user_id, local_date)
        if not plan or plan.status == "DRAFT":
            return {"plan_date": local_date, "status": "NO_PLAN"}
        await db.refresh(plan, ["plan_blocks", "availability_windows"])
        blocks = list(plan.plan_blocks)
        task_ids = {b.task_id for b in blocks if b.task_id}
        tasks = {
            t.id: t
            for t in (
                await db.scalars(
                    select(Task)
                    .options(selectinload(Task.dependencies))
                    .where(Task.id.in_(task_ids))
                )
            ).all()
        }
        preserved, eligible = [], []
        for block in blocks:
            task = tasks.get(block.task_id)
            if (
                block.status != "PLANNED"
                or block.is_locked
                or block.block_type == "FIXED_EVENT"
                or (
                    task
                    and (
                        task.scheduling_type == "FIXED"
                        or task.status not in ("DRAFT", "PENDING")
                    )
                )
            ):
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
        for task_id in {b.task_id for b in eligible if b.task_id}:
            task = tasks[task_id]
            reserved_minutes = sum(
                int((b.planned_end_at - b.planned_start_at).total_seconds() // 60)
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
        result = DeterministicScheduler().schedule(schedule_tasks, windows)
        if result.unscheduled_tasks:
            raise ValidationError(
                "Unable to fit unfinished work and dependencies in the remaining availability. Adjust the plan and try again."
            )
        for block in eligible:
            await db.delete(block)
        await db.flush()
        # Preserve historical rows, including their positions; new rows receive unused positions.
        position = max((b.position for b in preserved), default=-1) + 1
        for offset, block in enumerate(result.blocks):
            db.add(
                PlanBlock(
                    daily_plan_id=plan.id,
                    task_id=block.task_id,
                    block_type=block.block_type,
                    title=block.title,
                    planned_start_at=block.start_at,
                    planned_end_at=block.end_at,
                    position=position + offset,
                    status="PLANNED",
                    created_by="SCHEDULER",
                )
            )
        await db.flush()
        await db.refresh(plan, ["plan_blocks"])
        if commit:
            await db.commit()
        return await self.get_today(db, user_id, local_date)


today_service = TodayService()
