from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import datetime, timezone
from fastapi import HTTPException
from app.db.models.focus import FocusRun
from app.db.models.garden import GardenState, RewardEvent
from app.core.economy import WATER_PER_POMODORO

async def finish_focus_run(db: AsyncSession, user_id: UUID, focus_run_id: UUID, outcome: str):
    focus_run = await db.scalar(select(FocusRun).where(FocusRun.id == focus_run_id, FocusRun.user_id == user_id))
    if not focus_run:
        raise HTTPException(status_code=404, detail="Focus run not found")
        
    if focus_run.status == 'ENDED':
        return focus_run # idempotent
        
    focus_run.status = 'ENDED'
    focus_run.outcome = outcome
    
    if outcome in ('DONE', 'NEED_MORE_TIME', 'FINISHED_EARLY'):
        garden = await db.scalar(select(GardenState).where(GardenState.user_id == user_id))
        if not garden:
            garden = GardenState(user_id=user_id, water_balance=0, leaves_balance=0)
            db.add(garden)
            await db.flush()
            
        idempotency_key = f"focus_completed_{focus_run_id}"
        existing = await db.scalar(select(RewardEvent).where(RewardEvent.idempotency_key == idempotency_key))
        if not existing:
            garden.water_balance += WATER_PER_POMODORO
            event = RewardEvent(
                user_id=user_id,
                event_type="FOCUS_COMPLETED",
                resource_type="WATER",
                amount=WATER_PER_POMODORO,
                idempotency_key=idempotency_key,
                source_focus_run_id=focus_run_id
            )
            db.add(event)
            
    await db.commit()
    return focus_run
from uuid import UUID
from datetime import datetime, timezone, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.errors import ValidationError, ResourceNotFoundError
from app.db.models.focus import FocusRun
from app.db.models.tasks import Task
from app.schemas.focus import FocusSessionStart, FocusSessionFinish
from app.crud.crud_focus import focus_run as crud_focus
from app.crud.crud_task import task as crud_task
from app.services.today_service import today_service

class FocusService:
    async def get_active_session(self, db: AsyncSession, user_id: UUID) -> FocusRun | None:
        return await crud_focus.get_active_session(db, user_id)

    async def start_session(self, db: AsyncSession, user_id: UUID, obj_in: FocusSessionStart) -> FocusRun:
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
        await crud_focus.add_event(db, run.id, "STARTED")
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
        await crud_focus.add_event(db, run.id, "PAUSED")
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
        await crud_focus.add_event(db, run.id, "RESUMED")
        await db.commit()
        await db.refresh(run)
        return run

    async def finish_session(self, db: AsyncSession, user_id: UUID, obj_in: FocusSessionFinish) -> FocusRun:
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

        if run.task_id:
            task = await crud_task.get(db, id=run.task_id)
            if task:
                if obj_in.outcome in ("DONE", "FINISHED_EARLY"):
                    task.status = "COMPLETED"
                    task.completed_at = now
                elif obj_in.outcome == "SKIP":
                    task.status = "SKIPPED"
                db.add(task)

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
