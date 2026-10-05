from datetime import timezone
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


from pydantic import ValidationError as PydanticValidationError


async def test_invalid_action_rejected():
    with pytest.raises(PydanticValidationError):
        ReminderActionRequest(action_type="INVALID_ACTION")


async def test_remind_later_missing_due_at(db_session, test_user, test_reminder, clock):
    with pytest.raises(PydanticValidationError):
        ReminderActionRequest(action_type="REMIND_LATER")


async def test_move_milestone_missing_due_at(
    db_session, test_user, test_reminder, clock
):
    with pytest.raises(PydanticValidationError):
        ReminderActionRequest(action_type="MOVE_MILESTONE")


async def test_remind_later_action(db_session, test_user, test_reminder, clock):
    new_due = clock.instant + timedelta(days=1)
    await reminders_service.execute_action(
        db_session,
        test_reminder.id,
        ReminderActionRequest(action_type="REMIND_LATER", new_due_at=new_due),
        test_user.id,
    )
    await db_session.commit()
    await db_session.refresh(test_reminder)
    assert test_reminder.due_at == new_due

    # Repeated REMIND_LATER with same time deduplicates
    await reminders_service.execute_action(
        db_session,
        test_reminder.id,
        ReminderActionRequest(action_type="REMIND_LATER", new_due_at=new_due),
        test_user.id,
    )
    await db_session.commit()
    actions = (
        await db_session.scalars(
            select(ReminderAction).where(ReminderAction.reminder_id == test_reminder.id)
        )
    ).all()
    assert len(actions) == 1


from app.db.models.garden import RewardEvent


async def test_mark_completed_action(db_session, test_user, test_goal, clock):
    # Need a milestone reminder
    from app.db.models.goals import Milestone

    milestone = Milestone(
        goal_id=test_goal.id,
        title="Test",
        position=0,
        due_at=clock.instant,
        status="PENDING",
    )
    db_session.add(milestone)
    await db_session.flush()
    reminder = Reminder(
        user_id=test_user.id,
        milestone_id=milestone.id,
        reminder_type="MILESTONE_DUE",
        message="M",
        due_at=clock.instant,
        original_due_at=clock.instant,
        status="DUE",
    )
    db_session.add(reminder)
    await db_session.commit()

    await reminders_service.execute_action(
        db_session,
        reminder.id,
        ReminderActionRequest(action_type="MARK_COMPLETED"),
        test_user.id,
    )
    await db_session.commit()
    await db_session.refresh(reminder)
    await db_session.refresh(milestone)

    assert reminder.status == "COMPLETED"
    assert milestone.status == "COMPLETED"
    assert milestone.completed_at is not None

    rewards = (
        await db_session.scalars(
            select(RewardEvent).where(RewardEvent.source_milestone_id == milestone.id)
        )
    ).all()
    assert len(rewards) == 1
    assert rewards[0].amount == 1

    # Repeated action
    await reminders_service.execute_action(
        db_session,
        reminder.id,
        ReminderActionRequest(action_type="MARK_COMPLETED"),
        test_user.id,
    )
    await db_session.commit()
    rewards_after = (
        await db_session.scalars(
            select(RewardEvent).where(RewardEvent.source_milestone_id == milestone.id)
        )
    ).all()
    assert len(rewards_after) == 1


async def test_move_milestone_action(db_session, test_user, test_goal, clock):
    from app.db.models.goals import Milestone

    milestone = Milestone(
        goal_id=test_goal.id,
        title="Test",
        position=0,
        due_at=clock.instant,
        status="PENDING",
    )
    db_session.add(milestone)
    await db_session.flush()
    reminder = Reminder(
        user_id=test_user.id,
        milestone_id=milestone.id,
        reminder_type="MILESTONE_DUE",
        message="M",
        due_at=clock.instant,
        original_due_at=clock.instant,
        status="DUE",
    )
    db_session.add(reminder)
    await db_session.commit()

    new_due = clock.instant + timedelta(days=5)
    await reminders_service.execute_action(
        db_session,
        reminder.id,
        ReminderActionRequest(action_type="MOVE_MILESTONE", new_due_at=new_due),
        test_user.id,
    )
    await db_session.commit()
    await db_session.refresh(reminder)
    await db_session.refresh(milestone)

    assert milestone.due_at == new_due
    assert reminder.due_at == new_due - timedelta(days=1)

    # Repeated action
    await reminders_service.execute_action(
        db_session,
        reminder.id,
        ReminderActionRequest(action_type="MOVE_MILESTONE", new_due_at=new_due),
        test_user.id,
    )
    await db_session.commit()
    actions = (
        await db_session.scalars(
            select(ReminderAction).where(ReminderAction.reminder_id == reminder.id)
        )
    ).all()
    assert len(actions) == 1

    # Stale reminder repair regression
    reminder.due_at = clock.instant + timedelta(days=10)
    db_session.add(reminder)
    await db_session.commit()

    await reminders_service.execute_action(
        db_session,
        reminder.id,
        ReminderActionRequest(action_type="MOVE_MILESTONE", new_due_at=new_due),
        test_user.id,
    )
    await db_session.commit()
    await db_session.refresh(reminder)

    assert reminder.due_at == new_due - timedelta(days=1)
    actions = (
        await db_session.scalars(
            select(ReminderAction).where(ReminderAction.reminder_id == reminder.id)
        )
    ).all()
    assert len(actions) == 2

async def test_reminder_action_whitelist_enforcement(db_session, test_user):
    """Unsupported action -> rejected at the schema level."""
    from pydantic import ValidationError as PydanticValidationError

    with pytest.raises(PydanticValidationError):
        ReminderActionRequest(action_type="INVALID_HACK_ACTION")


async def test_remind_later_requires_new_due_at(db_session, test_user):
    """REMIND_LATER without new_due_at -> rejected at the schema level."""
    from pydantic import ValidationError as PydanticValidationError

    with pytest.raises(PydanticValidationError, match="REMIND_LATER requires new_due_at"):
        ReminderActionRequest(action_type="REMIND_LATER", new_due_at=None)


async def test_remind_later_rejects_past_time(db_session, test_user):
    """REMIND_LATER with new_due_at < current due_at -> rejected."""
    from datetime import timezone
    now = datetime.now(timezone.utc)
    reminder = Reminder(
        id=uuid4(),
        user_id=test_user.id,
        reminder_type="CUSTOM", original_due_at=datetime.now(timezone.utc),
        message="Test reminder",
        status="DUE",
        due_at=now
    )
    db_session.add(reminder)
    await db_session.flush()

    request = ReminderActionRequest(
        action_type="REMIND_LATER",
        new_due_at=now - timedelta(hours=1)
    )
    from app.core.errors import ValidationError
    with pytest.raises(ValidationError, match="new_due_at must be after previous due_at"):
        await reminders_service.execute_action(db_session, reminder.id, request, test_user.id)


async def test_remind_later_updates_time(db_session, test_user):
    """Valid REMIND_LATER updates due time correctly."""
    from datetime import timezone
    now = datetime.now(timezone.utc)
    reminder = Reminder(
        id=uuid4(),
        user_id=test_user.id,
        reminder_type="CUSTOM", original_due_at=datetime.now(timezone.utc),
        message="Test reminder",
        status="DUE",
        due_at=now
    )
    db_session.add(reminder)
    await db_session.flush()

    future = now + timedelta(hours=1)
    request = ReminderActionRequest(
        action_type="REMIND_LATER",
        new_due_at=future
    )
    updated = await reminders_service.execute_action(db_session, reminder.id, request, test_user.id)

    assert updated.due_at == future
    assert updated.status == "SCHEDULED"


async def test_complete_and_dismiss_actions_idempotency(db_session, test_user, test_milestone):
    """COMPLETE/DISMISS idempotency and isolation from milestones."""
    from datetime import timezone

    ms = test_milestone

    r_complete = Reminder(
        id=uuid4(), user_id=test_user.id, reminder_type="MILESTONE_DUE", milestone_id=ms.id,
        original_due_at=datetime.now(timezone.utc), message="Complete me", status="DUE", due_at=datetime.now(timezone.utc)
    )
    r_dismiss = Reminder(
        id=uuid4(), user_id=test_user.id, reminder_type="MILESTONE_DUE", milestone_id=ms.id,
        original_due_at=datetime.now(timezone.utc), message="Dismiss me", status="DUE", due_at=datetime.now(timezone.utc)
    )
    db_session.add_all([r_complete, r_dismiss])
    await db_session.flush()

    # Action 1: COMPLETE
    await reminders_service.execute_action(
        db_session, r_complete.id, ReminderActionRequest(action_type="COMPLETE"), test_user.id
    )
    # Action 2: DISMISS
    await reminders_service.execute_action(
        db_session, r_dismiss.id, ReminderActionRequest(action_type="DISMISS"), test_user.id
    )
    await db_session.commit()
    await db_session.refresh(r_complete)
    await db_session.refresh(r_dismiss)
    await db_session.refresh(ms)

    assert r_complete.status == "COMPLETED"
    assert r_complete.completed_at is not None
    assert r_dismiss.status == "DISMISSED"
    assert r_dismiss.dismissed_at is not None

    # DISMISS/COMPLETE do not complete the milestone!
    assert ms.status == "PENDING"

    # Idempotency: repeated execution does not corrupt state
    original_complete_time = r_complete.completed_at
    original_dismiss_time = r_dismiss.dismissed_at

    await reminders_service.execute_action(
        db_session, r_complete.id, ReminderActionRequest(action_type="COMPLETE"), test_user.id
    )
    await reminders_service.execute_action(
        db_session, r_dismiss.id, ReminderActionRequest(action_type="DISMISS"), test_user.id
    )

    assert r_complete.status == "COMPLETED"
    assert r_complete.completed_at == original_complete_time
    assert r_dismiss.status == "DISMISSED"
    assert r_dismiss.dismissed_at == original_dismiss_time

async def test_terminal_state_cross_mutation_blocked(db_session, test_user):
    """A terminal reminder must not be changed into another state."""
    from datetime import timezone, timedelta
    
    now = datetime.now(timezone.utc)
    new_due = now + timedelta(days=1)
    
    r_comp = Reminder(
        id=uuid4(), user_id=test_user.id, reminder_type="CUSTOM", original_due_at=now,
        message="comp", status="COMPLETED", due_at=now, completed_at=now
    )
    r_diss = Reminder(
        id=uuid4(), user_id=test_user.id, reminder_type="CUSTOM", original_due_at=now,
        message="diss", status="DISMISSED", due_at=now, dismissed_at=now
    )
    db_session.add_all([r_comp, r_diss])
    await db_session.flush()
    
    # COMPLETED -> DISMISS blocked
    await reminders_service.execute_action(db_session, r_comp.id, ReminderActionRequest(action_type="DISMISS"), test_user.id)
    # COMPLETED -> REMIND_LATER blocked
    await reminders_service.execute_action(db_session, r_comp.id, ReminderActionRequest(action_type="REMIND_LATER", new_due_at=new_due), test_user.id)
    
    # DISMISSED -> COMPLETE blocked
    await reminders_service.execute_action(db_session, r_diss.id, ReminderActionRequest(action_type="COMPLETE"), test_user.id)
    # DISMISSED -> REMIND_LATER blocked
    await reminders_service.execute_action(db_session, r_diss.id, ReminderActionRequest(action_type="REMIND_LATER", new_due_at=new_due), test_user.id)
    
    await db_session.commit()
    await db_session.refresh(r_comp)
    await db_session.refresh(r_diss)
    
    assert r_comp.status == "COMPLETED"
    assert r_diss.status == "DISMISSED"
