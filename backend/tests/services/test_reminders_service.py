from datetime import date, datetime, timedelta
from unittest.mock import AsyncMock
from uuid import uuid4

import pytest
from app.core.errors import ResourceNotFoundError
from app.crud.crud_daily_plan import daily_plan as crud_daily_plan
from app.db.models.daily_plans import DailyPlan, PlanBlock
from app.db.models.reminders import Reminder, ReminderAction
from app.db.models.tasks import Task
from app.db.models.users import UserSettings
from app.schemas.reminders import ReminderActionRequest
from app.services.reminders_service import reminders_service
from sqlalchemy import event, select
from sqlalchemy.orm import Session

pytestmark = pytest.mark.integration


@pytest.mark.parametrize(
    "tz,instant,expected_date",
    [
        ("Asia/Ho_Chi_Minh", "2026-01-01T09:00:00+00:00", date(2026, 1, 1)),
        ("Pacific/Kiritimati", "2026-01-01T10:30:00+00:00", date(2026, 1, 2)),
        ("America/Los_Angeles", "2026-01-01T00:30:00+00:00", date(2025, 12, 31)),
        (None, "2026-01-01T00:30:00+00:00", date(2026, 1, 1)),
        ("Invalid/Timezone", "2026-01-01T00:30:00+00:00", date(2026, 1, 1)),
    ],
)
async def test_reminders_local_date_and_offsets(
    db_session, test_user, test_reminder, clock, tz, instant, expected_date
):
    clock.instant = datetime.fromisoformat(instant)
    if tz is not None:
        db_session.add(UserSettings(user_id=test_user.id, timezone=tz))
        await db_session.commit()
    await reminders_service.execute_action(
        db_session,
        test_reminder.id,
        ReminderActionRequest(action_type="CREATE_PLAN"),
        test_user.id,
    )
    await db_session.commit()
    plan = (await db_session.scalars(select(DailyPlan))).one()
    assert plan.plan_date == expected_date
    # Snapshot retains the configured value; invalid zones use UTC for calculation.
    assert plan.timezone_snapshot == (tz or "UTC")


async def test_create_draft_uses_crud_and_creates_expected_task_block(
    db_session, test_user, test_reminder, clock, monkeypatch
):
    spy = AsyncMock(wraps=crud_daily_plan.create_draft)
    monkeypatch.setattr(crud_daily_plan, "create_draft", spy)
    await reminders_service.execute_action(
        db_session,
        test_reminder.id,
        ReminderActionRequest(action_type="CREATE_PLAN"),
        test_user.id,
    )
    await db_session.commit()
    spy.assert_awaited_once_with(
        db_session,
        user_id=test_user.id,
        plan_date=clock.instant.date(),
        timezone_snapshot="UTC",
        reality_check="COMFORTABLE",
    )
    plan = (await db_session.scalars(select(DailyPlan))).one()
    task = (await db_session.scalars(select(Task))).one()
    block = (await db_session.scalars(select(PlanBlock))).one()
    assert plan.status == "DRAFT"
    assert (
        task.title,
        task.estimated_duration_minutes,
        task.priority,
        task.status,
    ) == (f"Work on {test_reminder.message}", 30, "HIGH", "DRAFT")
    assert (block.daily_plan_id, block.task_id) == (plan.id, task.id)
    assert block.planned_start_at == clock.instant
    assert block.planned_end_at == clock.instant + timedelta(minutes=30)
    assert test_reminder.status == "COMPLETED"
    assert test_reminder.completed_at == clock.instant


@pytest.mark.parametrize("status", ["DRAFT", "CONFIRMED", "ACTIVE"])
async def test_existing_plan_and_repeated_action_do_not_duplicate(
    db_session, test_user, test_reminder, clock, status
):
    plan = DailyPlan(
        user_id=test_user.id,
        plan_date=clock.instant.date(),
        status=status,
        timezone_snapshot="UTC",
        confirmed_at=None if status == "DRAFT" else clock.instant,
    )
    db_session.add(plan)
    await db_session.commit()
    plan_id = plan.id
    request = ReminderActionRequest(action_type="CREATE_PLAN")
    for _ in range(2):
        await reminders_service.execute_action(
            db_session, test_reminder.id, request, test_user.id
        )
        await db_session.commit()
    plans = (await db_session.scalars(select(DailyPlan))).all()
    assert [p.id for p in plans] == [plan_id]
    assert plans[0].status == status
    # Existing drafts are reused through CRUD; confirmed/active plans are untouched.
    expected = 1 if status == "DRAFT" else 0
    assert len((await db_session.scalars(select(Task))).all()) == expected
    assert len((await db_session.scalars(select(PlanBlock))).all()) == expected
    assert len((await db_session.scalars(select(ReminderAction))).all()) == 1
    assert test_reminder.status == "COMPLETED"


async def test_create_plan_transaction_atomicity(
    db_session, test_user, test_reminder, clock
):
    user_id, reminder_id = test_user.id, test_reminder.id
    observed = []

    def fail_block_flush(session, flush_context, instances):
        if session is db_session.sync_session and any(
            isinstance(obj, PlanBlock) for obj in session.new
        ):
            observed.append(True)
            raise RuntimeError("injected block persistence failure")

    event.listen(Session, "before_flush", fail_block_flush)
    try:
        with pytest.raises(RuntimeError, match="injected block persistence failure"):
            await reminders_service.execute_action(
                db_session,
                reminder_id,
                ReminderActionRequest(action_type="CREATE_PLAN"),
                user_id,
            )
    finally:
        event.remove(Session, "before_flush", fail_block_flush)
    await db_session.rollback()
    assert observed == [True]
    for model in (DailyPlan, Task, PlanBlock, ReminderAction):
        assert (await db_session.scalars(select(model))).all() == []
    reminder = await db_session.get(Reminder, reminder_id)
    assert reminder.status == "SCHEDULED"
    assert reminder.completed_at is None


async def test_cross_user_rejected(db_session, test_user_two, test_reminder):
    with pytest.raises(ResourceNotFoundError):
        await reminders_service.execute_action(
            db_session,
            test_reminder.id,
            ReminderActionRequest(action_type="CREATE_PLAN"),
            test_user_two.id,
        )
    await db_session.refresh(test_reminder)
    assert test_reminder.status == "SCHEDULED"
    assert (await db_session.scalars(select(ReminderAction))).all() == []


async def test_missing_reminder(db_session, test_user):
    with pytest.raises(ResourceNotFoundError):
        await reminders_service.execute_action(
            db_session,
            uuid4(),
            ReminderActionRequest(action_type="CREATE_PLAN"),
            test_user.id,
        )
