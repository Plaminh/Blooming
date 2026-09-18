from uuid import UUID
from datetime import datetime, timezone
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.models.focus import FocusRun, FocusRunEvent

class CRUDFocus:
    async def get_active_session(self, db: AsyncSession, user_id: UUID) -> FocusRun | None:
        result = await db.execute(
            select(FocusRun).where(
                FocusRun.user_id == user_id,
                FocusRun.status.in_(['READY', 'FOCUSING', 'PAUSED'])
            ).execution_options(populate_existing=True)
        )
        return result.scalars().first()

    async def add_event(self, db: AsyncSession, focus_run_id: UUID, event_type: str, payload: dict | None = None) -> FocusRunEvent:
        event = FocusRunEvent(
            focus_run_id=focus_run_id,
            event_type=event_type,
            occurred_at=datetime.now(timezone.utc),
            payload=payload
        )
        db.add(event)
        return event

focus_run = CRUDFocus()
