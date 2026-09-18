import uuid
from datetime import datetime, timezone

import pytest_asyncio
from app.db.models.reminders import Reminder, ReminderAction
from app.db.models.users import User
from sqlalchemy.ext.asyncio import AsyncSession


@pytest_asyncio.fixture
async def test_reminder(db_session: AsyncSession, test_user: User) -> Reminder:
    """Creates a basic SCHEDULED custom reminder."""
    reminder = Reminder(
        id=uuid.uuid4(),
        user_id=test_user.id,
        reminder_type="CUSTOM",
        message="It is time to plan your day.",
        due_at=datetime(2026, 1, 1, 9, 0, tzinfo=timezone.utc),
        original_due_at=datetime(2026, 1, 1, 9, 0, tzinfo=timezone.utc),
        status="SCHEDULED",
    )
    db_session.add(reminder)
    await db_session.commit()
    await db_session.refresh(reminder)
    return reminder


@pytest_asyncio.fixture
async def test_reminder_action(
    db_session: AsyncSession, test_reminder: Reminder
) -> ReminderAction:
    """Creates an action for the test reminder."""
    action = ReminderAction(
        id=uuid.uuid4(),
        reminder_id=test_reminder.id,
        action_type="CREATE_PLAN",
    )
    db_session.add(action)
    await db_session.commit()
    await db_session.refresh(action)
    return action
