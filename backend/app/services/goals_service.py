from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import datetime, timezone
from app.db.models.goals import Milestone
from app.db.models.garden import GardenState, RewardEvent
from app.core.economy import LEAVES_PER_MILESTONE
from fastapi import HTTPException

async def complete_milestone(db: AsyncSession, user_id: UUID, milestone_id: UUID):
    from app.db.models.goals import Goal
    milestone = await db.scalar(select(Milestone).join(Goal).where(Milestone.id == milestone_id, Goal.user_id == user_id))
    if not milestone:
        raise HTTPException(status_code=404, detail="Milestone not found")
        
    if milestone.status == "COMPLETED":
        return milestone
        
    milestone.status = "COMPLETED"
    milestone.completed_at = datetime.now(timezone.utc)
    
    garden = await db.scalar(select(GardenState).where(GardenState.user_id == user_id))
    if not garden:
        garden = GardenState(user_id=user_id, water_balance=0, leaves_balance=0)
        db.add(garden)
        
    idempotency_key = f"milestone_completed_{milestone_id}"
    existing = await db.scalar(select(RewardEvent).where(RewardEvent.idempotency_key == idempotency_key))
    if not existing:
        garden.leaves_balance += LEAVES_PER_MILESTONE
        event = RewardEvent(
            user_id=user_id,
            event_type="MILESTONE_COMPLETED",
            resource_type="LEAVES",
            amount=LEAVES_PER_MILESTONE,
            idempotency_key=idempotency_key,
            source_milestone_id=milestone_id
        )
        db.add(event)
        
    await db.commit()
    return milestone
