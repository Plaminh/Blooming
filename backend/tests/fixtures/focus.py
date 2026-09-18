import uuid
from datetime import datetime, timezone

import pytest_asyncio
from app.db.models.focus import FocusRun, FocusRunEvent
from app.db.models.tasks import Task
from app.db.models.users import User
from sqlalchemy.ext.asyncio import AsyncSession


@pytest_asyncio.fixture
async def test_focus_session(
    db_session: AsyncSession, test_user: User, test_task: Task
) -> FocusRun:
    """Creates a basic active focus run."""
    focus_run = FocusRun(
        id=uuid.uuid4(),
        user_id=test_user.id,
        task_id=test_task.id,
        status="FOCUSING",
        started_at=datetime(2026, 1, 1, 10, 0, tzinfo=timezone.utc),
        planned_focus_seconds=1500,
        total_paused_seconds=0,
    )
    db_session.add(focus_run)
    await db_session.commit()
    await db_session.refresh(focus_run)
    return focus_run


@pytest_asyncio.fixture
async def test_focus_run_event(
    db_session: AsyncSession, test_focus_session: FocusRun
) -> FocusRunEvent:
    """Creates a basic focus run event."""
    event = FocusRunEvent(
        id=uuid.uuid4(),
        focus_run_id=test_focus_session.id,
        event_type="STARTED",
        occurred_at=datetime(2026, 1, 1, 10, 0, tzinfo=timezone.utc),
    )
    db_session.add(event)
    await db_session.commit()
    await db_session.refresh(event)
    return event
