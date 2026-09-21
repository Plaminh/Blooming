import logging
from datetime import datetime, timedelta, timezone
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.economy import WATER_PER_POMODORO
from app.core.errors import ResourceNotFoundError, ValidationError, InvalidStatusTransitionError
from app.crud.crud_focus import focus_run as crud_focus
from app.crud.crud_task import task as crud_task
from app.db.models.focus import FocusRun, FocusRunEvent
from app.db.models.daily_plans import DailyPlan, PlanBlock
from app.db.models.users import User
from app.schemas.focus import FocusSessionFinish, FocusSessionStart
from app.schemas.today import TodayTaskStatusUpdate
from app.services.garden_service import award_resources
from app.services.today_service import today_service


logger = logging.getLogger(__name__)


class FocusService:
    async def get_active_session(self, db: AsyncSession, user_id: UUID) -> FocusRun | None:
        return await crud_focus.get_active_session(db, user_id)

    async def start_session(
        self, db: AsyncSession, user_id: UUID, obj_in: FocusSessionStart
    ) -> FocusRun:
        await db.execute(select(User.id).where(User.id == user_id).with_for_update())
        active = await crud_focus.get_active_session(db, user_id)
        if active:
            raise InvalidStatusTransitionError("An active focus session already exists")

        # Validate task ownership
        if obj_in.task_id:
            task = await crud_task.get(db, id=obj_in.task_id, user_id=user_id)
            if not task or task.user_id != user_id:
                raise ResourceNotFoundError("Task not found")

        task_id = obj_in.task_id
        if obj_in.plan_block_id:
            block = await db.scalar(select(PlanBlock).join(DailyPlan).where(PlanBlock.id == obj_in.plan_block_id, DailyPlan.user_id == user_id, DailyPlan.status.in_(("CONFIRMED", "ACTIVE"))))
            if not block:
                raise ResourceNotFoundError("Plan block not found")
            if block.status not in ("PLANNED", "ACTIVE"):
                raise InvalidStatusTransitionError("Plan block is no longer available")
            if task_id is not None and block.task_id != task_id:
                raise ValidationError("Task does not match plan block")
            task_id = block.task_id
        if task_id:
            task = await crud_task.get(db, id=task_id, user_id=user_id)
            if not task:
                raise ResourceNotFoundError("Task not found")
            if task.status not in ("DRAFT", "PENDING", "IN_PROGRESS"):
                raise InvalidStatusTransitionError("Task is no longer available")
        now = datetime.now(timezone.utc)
        run = FocusRun(
            user_id=user_id,
            task_id=task_id,
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
        await db.execute(select(User.id).where(User.id == user_id).with_for_update())
        run = await crud_focus.get_active_session(db, user_id)
        if not run:
            raise ResourceNotFoundError("No active focus session to pause")
        if run.status != "FOCUSING":
            raise InvalidStatusTransitionError(f"Cannot pause session in {run.status} state")

        run.status = "PAUSED"
        run.paused_at = datetime.now(timezone.utc)
        db.add(run)
        await crud_focus.add_event(db, run.id, "PAUSED", {})
        await db.commit()
        await db.refresh(run)
        return run

    async def resume_session(self, db: AsyncSession, user_id: UUID) -> FocusRun:
        await db.execute(select(User.id).where(User.id == user_id).with_for_update())
        run = await crud_focus.get_active_session(db, user_id)
        if not run:
            raise ResourceNotFoundError("No active focus session to resume")
        if run.status != "PAUSED":
            raise InvalidStatusTransitionError(f"Cannot resume session in {run.status} state")

        now = datetime.now(timezone.utc)
        if run.paused_at:
            paused_duration = max(0, int((now - run.paused_at).total_seconds()))
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
        if obj_in.run_id:
            run = await db.scalar(select(FocusRun).where(FocusRun.id == obj_in.run_id, FocusRun.user_id == user_id).execution_options(populate_existing=True))
        else:
            run = await crud_focus.get_active_session(db, user_id)
        if not run:
            logger.info("focus_finish_no_active_run")
            raise ResourceNotFoundError("No active focus session to finish")
        if run.status == "ENDED":
            logger.info("focus_completion_duplicate", extra={"run_id": str(run.id)})
            event = await db.scalar(select(FocusRunEvent).where(FocusRunEvent.focus_run_id == run.id, FocusRunEvent.event_type == "ENDED"))
            run.replan = (event.payload or {}).get("replan") if event else None
            return run
        if run.status not in ("FOCUSING", "PAUSED"):
            raise InvalidStatusTransitionError("Focus session has not started")

        now = datetime.now(timezone.utc)
        if run.status == "PAUSED" and run.paused_at:
            paused_duration = max(0, int((now - run.paused_at).total_seconds()))
            run.total_paused_seconds += int(paused_duration)

        run.paused_at = None
        run.status = "ENDED"
        run.ended_at = now
        run.outcome = obj_in.outcome

        # Calculate actual duration from server timestamps
        if run.started_at is None:
            raise InvalidStatusTransitionError("Focus session has no start time")
        total_elapsed = int((now - run.started_at).total_seconds())
        run.actual_duration_seconds = max(0, total_elapsed - run.total_paused_seconds)

        if total_elapsed < 0 or run.actual_duration_seconds > 86400:
            logger.warning("abnormal_server_focus_duration", extra={"run_id": str(run.id), "elapsed_seconds": total_elapsed})
        db.add(run)
        ended_event = await crud_focus.add_event(db, run.id, "ENDED", {"outcome": obj_in.outcome})

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
            from typing import Literal
            task_status: Literal["SKIPPED", "COMPLETED"] = "SKIPPED" if obj_in.outcome == "SKIP" else "COMPLETED"
            await today_service.update_task_status_from_today(
                db,
                user_id,
                run.task_id,
                TodayTaskStatusUpdate(status=task_status),
                commit=False,
            )

        # Completion, awards and the partial replan share exactly one commit.
        replan = None
        if obj_in.should_replan:
            from fastapi.encoders import jsonable_encoder
            await db.flush()
            replan = await today_service.replan_today(db, user_id, commit=False)
            ended_event.payload = {"outcome": obj_in.outcome, "replan": jsonable_encoder(replan)}
        await db.commit()
        await db.refresh(run)
        run.replan = replan
        logger.info("focus_completed", extra={"run_id": str(run.id), "duration_seconds": run.actual_duration_seconds, "outcome": run.outcome})

        return run


focus_service = FocusService()
