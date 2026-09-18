import uuid
from datetime import date, datetime, timezone

import pytest_asyncio
from app.db.models.daily_plans import AvailabilityWindow, DailyPlan, PlanBlock
from app.db.models.tasks import Task
from app.db.models.users import User
from sqlalchemy.ext.asyncio import AsyncSession


@pytest_asyncio.fixture
async def test_daily_plan(db_session: AsyncSession, test_user: User) -> DailyPlan:
    """Creates a basic active Daily Plan with a deterministic date."""
    plan = DailyPlan(
        id=uuid.uuid4(),
        user_id=test_user.id,
        plan_date=date(2026, 1, 1),
        status="ACTIVE",
        confirmed_at=datetime(2026, 1, 1, 8, tzinfo=timezone.utc),
        timezone_snapshot="UTC",
    )
    db_session.add(plan)
    await db_session.commit()
    await db_session.refresh(plan)
    return plan


@pytest_asyncio.fixture
async def test_availability_window(
    db_session: AsyncSession, test_daily_plan: DailyPlan
) -> AvailabilityWindow:
    """Creates an availability window for the test plan."""
    window = AvailabilityWindow(
        id=uuid.uuid4(),
        daily_plan_id=test_daily_plan.id,
        available_start_at=datetime(2026, 1, 1, 9, 0, tzinfo=timezone.utc),
        available_end_at=datetime(2026, 1, 1, 17, 0, tzinfo=timezone.utc),
    )
    db_session.add(window)
    await db_session.commit()
    await db_session.refresh(window)
    return window


@pytest_asyncio.fixture
async def test_plan_block(
    db_session: AsyncSession, test_daily_plan: DailyPlan, test_task: Task
) -> PlanBlock:
    """Creates a TASK plan block."""
    block = PlanBlock(
        id=uuid.uuid4(),
        daily_plan_id=test_daily_plan.id,
        task_id=test_task.id,
        block_type="TASK",
        planned_start_at=datetime(2026, 1, 1, 9, 0, tzinfo=timezone.utc),
        planned_end_at=datetime(2026, 1, 1, 10, 0, tzinfo=timezone.utc),
        position=0,
        status="PLANNED",
        created_by="SCHEDULER",
    )
    db_session.add(block)
    await db_session.commit()
    await db_session.refresh(block)
    return block
