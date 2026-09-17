from datetime import datetime, timedelta, timezone
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.economy import WATER_PER_POMODORO
from app.core.errors import ResourceNotFoundError, ValidationError
from app.crud.crud_focus import focus_run as crud_focus
from app.crud.crud_task import task as crud_task
from app.db.models.focus import FocusRun
from app.db.models.users import User
from app.schemas.focus import FocusSessionFinish, FocusSessionStart
from app.schemas.today import TodayTaskStatusUpdate
from app.services.garden_service import award_resources
from app.services.today_service import today_service


class FocusService:
    async def get_active_session(self, db: AsyncSession, user_id: UUID) -> FocusRun | None:
        return await crud_focus.get_active_session(db, user_id)

    async def start_session(
        self, db: AsyncSession, user_id: UUID, obj_in: FocusSessionStart
    ) -> FocusRun:
        active = await crud_focus.get_active_session(db, user_id)
        if active:
            raise ValidationError("An active focus session already exists")

        # Validate task ownership
        if obj_in.task_id:
            task = await crud_task.get(db, id=obj_in.task_id)
            if not task or task.user_id != user_id:
                raise ValidationError("Task not found or unauthorized")

        now = datetime.now(timezone.utc)
        run = FocusRun(
            user_id=user_id,
            task_id=obj_in.task_id,
            plan_block_id=obj_in.plan_block_id,
            quick_task_title=obj_in.quick_task_title,
            planned_focus_seconds=obj_in.planned_focus_seconds,
            planned_break_seconds=obj_in.planned_break_seconds,
            status="FOCUSING",
            started_at=now,
            expected_end_at=now + timedelta(seconds=obj_in.planned_focus_seconds),
        )
        db.add(run)
        await db.flush()
        await crud_focus.add_event(db, run.id, "STARTED", {})
        await db.commit()
        await db.refresh(run)
        return run

    async def pause_session(self, db: AsyncSession, user_id: UUID) -> FocusRun:
        run = await crud_focus.get_active_session(db, user_id)
        if not run:
            raise ResourceNotFoundError("No active focus session to pause")
        if run.status != "FOCUSING":
            raise ValidationError(f"Cannot pause session in {run.status} state")

        run.status = "PAUSED"
        run.paused_at = datetime.now(timezone.utc)
        db.add(run)
        await crud_focus.add_event(db, run.id, "PAUSED", {})
        await db.commit()
        await db.refresh(run)
        return run

    async def resume_session(self, db: AsyncSession, user_id: UUID) -> FocusRun:
        run = await crud_focus.get_active_session(db, user_id)
        if not run:
            raise ResourceNotFoundError("No active focus session to resume")
        if run.status != "PAUSED":
            raise ValidationError(f"Cannot resume session in {run.status} state")

        now = datetime.now(timezone.utc)
        if run.paused_at:
            paused_duration = (now - run.paused_at).total_seconds()
            run.total_paused_seconds += int(paused_duration)
            if run.expected_end_at:
                run.expected_end_at += timedelta(seconds=int(paused_duration))
        run.paused_at = None
        run.status = "FOCUSING"
        db.add(run)
        await crud_focus.add_event(db, run.id, "RESUMED", {})
        await db.commit()
        await db.refresh(run)
        return run

    async def finish_session(
        self, db: AsyncSession, user_id: UUID, obj_in: FocusSessionFinish
    ) -> FocusRun:
        await db.execute(select(User.id).where(User.id == user_id).with_for_update())
        run = await crud_focus.get_active_session(db, user_id)
        if not run:
            raise ResourceNotFoundError("No active focus session to finish")

        now = datetime.now(timezone.utc)
        if run.status == "PAUSED" and run.paused_at:
            paused_duration = (now - run.paused_at).total_seconds()
            run.total_paused_seconds += int(paused_duration)

        run.status = "ENDED"
        run.ended_at = now
        run.outcome = obj_in.outcome

        # Calculate actual duration from server timestamps
        total_elapsed = int((now - run.started_at).total_seconds())
        run.actual_duration_seconds = max(0, total_elapsed - run.total_paused_seconds)

        db.add(run)
        await crud_focus.add_event(db, run.id, "ENDED", {"outcome": obj_in.outcome})

        if obj_in.outcome in ("DONE", "FINISHED_EARLY", "NEED_MORE_TIME"):
            await award_resources(
                db,
                user_id,
                "WATER",
                WATER_PER_POMODORO,
                "FOCUS_COMPLETED",
                f"focus_completed_{run.id}",
                run.id,
            )
        if run.task_id and obj_in.outcome in ("DONE", "FINISHED_EARLY", "SKIP"):
            task_status = "SKIPPED" if obj_in.outcome == "SKIP" else "COMPLETED"
            await today_service.update_task_status_from_today(
                db,
                user_id,
                run.task_id,
                TodayTaskStatusUpdate(status=task_status),
                commit=False,
            )

        # Do not commit here if replanning to ensure one transaction boundary
        if obj_in.should_replan:
            await db.flush()
            await today_service.replan_today(db, user_id, commit=False)
            await db.commit()
            await db.refresh(run)
        else:
            await db.commit()
            await db.refresh(run)

        return run


focus_service = FocusService()
