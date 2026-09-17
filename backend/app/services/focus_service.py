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
