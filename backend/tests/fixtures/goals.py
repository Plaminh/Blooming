import uuid
from datetime import date, datetime, timezone

import pytest_asyncio
from app.db.models.goals import Goal, Milestone
from app.db.models.users import User
from sqlalchemy.ext.asyncio import AsyncSession


@pytest_asyncio.fixture
async def test_goal(db_session: AsyncSession, test_user: User) -> Goal:
    """Creates a basic active goal for the test user."""
    goal = Goal(
        id=uuid.uuid4(),
        user_id=test_user.id,
        title="Test Goal",
        status="ACTIVE",
        target_date=date(2026, 12, 31),
    )
    db_session.add(goal)
    await db_session.commit()
    await db_session.refresh(goal)
    return goal


@pytest_asyncio.fixture
async def test_milestone(db_session: AsyncSession, test_goal: Goal) -> Milestone:
    """Creates a milestone for the test goal."""
    milestone = Milestone(
        id=uuid.uuid4(),
        goal_id=test_goal.id,
        title="Test Milestone",
        position=0,
        status="PENDING",
        due_at=datetime(2026, 6, 1, tzinfo=timezone.utc),
    )
    db_session.add(milestone)
    await db_session.commit()
    await db_session.refresh(milestone)
    return milestone
