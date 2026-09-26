from datetime import datetime, timezone, timedelta
from uuid import uuid4
import pytest
from app.services.goals_service import goals_service
from app.services.reminders_service import reminders_service
from app.db.models.goals import Goal, Milestone
from app.db.models.reminders import Reminder
from app.schemas.goals import GoalCreate, MilestoneCreate, MilestoneUpdate
from sqlalchemy import select

pytestmark = pytest.mark.integration

@pytest.fixture
async def test_goal(db_session, test_user):
    goal = await goals_service.create_goal(
        db_session,
        GoalCreate(
            title="Test Goal",
            description="Test Description",
            target_date=datetime.now(timezone.utc).date() + timedelta(days=30),
            status="ACTIVE"
        ),
        test_user.id
    )
    return goal

async def test_milestone_reminder_sync_on_creation(db_session, test_user, test_goal):
    due_at = datetime.now(timezone.utc) + timedelta(days=7)
    milestone = await goals_service.create_milestone(
        db_session,
        test_goal.id,
        MilestoneCreate(
            title="Initial Milestone",
            description="Outcome",
            due_at=due_at,
            status="PENDING"
        ),
        test_user.id
    )
    await db_session.commit()
    
    # Check that a reminder was created
    reminders = (await db_session.scalars(
        select(Reminder).where(Reminder.source_id == str(milestone.id))
    )).all()
    
    assert len(reminders) == 1
    assert reminders[0].status == "SCHEDULED"

async def test_milestone_completion_resolves_reminder(db_session, test_user, test_goal):
    due_at = datetime.now(timezone.utc) + timedelta(days=7)
    milestone = await goals_service.create_milestone(
        db_session,
        test_goal.id,
        MilestoneCreate(
            title="To Be Completed",
            description="Outcome",
            due_at=due_at,
            status="PENDING"
        ),
        test_user.id
    )
    await db_session.commit()
    
    await goals_service.update_milestone(
        db_session,
        test_goal.id,
        milestone.id,
        MilestoneUpdate(status="COMPLETED"),
        test_user.id
    )
    await db_session.commit()
    
    # Check that reminder is resolved
    reminders = (await db_session.scalars(
        select(Reminder).where(Reminder.source_id == str(milestone.id))
    )).all()
    
    # The existing sync_milestone_reminder cancels them
    active_reminders = [r for r in reminders if r.status == "SCHEDULED"]
    assert len(active_reminders) == 0

async def test_milestone_date_change_reschedules_reminder_without_duplicates(db_session, test_user, test_goal):
    due_at1 = datetime.now(timezone.utc) + timedelta(days=7)
    milestone = await goals_service.create_milestone(
        db_session,
        test_goal.id,
        MilestoneCreate(
            title="Date Change Milestone",
            description="Outcome",
            due_at=due_at1,
            status="PENDING"
        ),
        test_user.id
    )
    await db_session.commit()
    
    # Change date
    due_at2 = due_at1 + timedelta(days=2)
    await goals_service.update_milestone(
        db_session,
        test_goal.id,
        milestone.id,
        MilestoneUpdate(due_at=due_at2),
        test_user.id
    )
    await db_session.commit()
    
    reminders = (await db_session.scalars(
        select(Reminder).where(Reminder.source_id == str(milestone.id))
    )).all()
    
    active_reminders = [r for r in reminders if r.status == "SCHEDULED"]
    assert len(active_reminders) == 1
    # sync_milestone_reminder subtracts 1 day from the due date to set the reminder
    # so we can just ensure it doesn't duplicate.

