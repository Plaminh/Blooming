from datetime import date, datetime, timedelta, timezone
import pytest
from sqlalchemy import select
from app.services.goals_service import goals_service
from app.db.models.goals import Milestone
from app.db.models.reminders import Reminder
from app.schemas.goals import RoadmapSave, MilestoneCreate, MilestoneUpdate
from app.db.models.users import UserSettings
from app.schemas.drafts import RoadmapDraft, MilestoneDraft

pytestmark = pytest.mark.integration


async def test_update_from_roadmap(db_session, test_user, test_goal):
    # Setup goal with 1 completed and 1 pending milestone
    m1 = Milestone(
        goal_id=test_goal.id,
        title="M1",
        position=0,
        status="COMPLETED",
        completed_at=datetime.now(timezone.utc),
        due_at=datetime.now(timezone.utc),
    )
    m2 = Milestone(
        goal_id=test_goal.id,
        title="M2",
        position=1,
        status="PENDING",
        due_at=datetime.now(timezone.utc),
    )
    db_session.add_all([m1, m2])
    await db_session.flush()

    # Draft only includes M2 (renamed) and a new M3
    draft = RoadmapDraft(
        type="roadmap",
        goalId=str(test_goal.id),
        goalTitle="Updated Title",
        targetDate=datetime.now(timezone.utc).date() + timedelta(days=10),
        milestones=[
            MilestoneDraft(
                id=str(m2.id),
                title="M2 Updated",
                targetDate=datetime.now(timezone.utc).date(),
                expectedOutcome="Outcome M2",
            ),
            MilestoneDraft(
                id="",
                title="M3 New",
                targetDate=datetime.now(timezone.utc).date(),
                expectedOutcome="Outcome M3",
            ),
        ],
    )

    save_payload = RoadmapSave(draft=draft, idempotency_key="roadmap_key_1")

    updated_goal = await goals_service.update_from_roadmap(
        db_session, test_goal.id, save_payload, test_user.id
    )
    await db_session.commit()
    await db_session.refresh(updated_goal)

    milestones = sorted(updated_goal.milestones, key=lambda m: m.position)
    assert len(milestones) == 3
    assert milestones[0].id == m1.id
    assert milestones[0].status == "COMPLETED"

    assert milestones[1].id == m2.id
    assert milestones[1].title == "M2 Updated"
    assert milestones[1].expected_outcome == "Outcome M2"

    assert milestones[2].title == "M3 New"
    assert milestones[2].expected_outcome == "Outcome M3"

    # Idempotency
    save_payload2 = RoadmapSave(draft=draft, idempotency_key="roadmap_key_1")
    updated_goal2 = await goals_service.update_from_roadmap(
        db_session, test_goal.id, save_payload2, test_user.id
    )
    assert len(updated_goal2.milestones) == 3


async def test_update_from_roadmap_removes_pending(db_session, test_user, test_goal):
    m_pending = Milestone(
        goal_id=test_goal.id,
        title="To Delete",
        position=0,
        status="PENDING",
        due_at=datetime.now(timezone.utc),
    )
    m_retain = Milestone(
        goal_id=test_goal.id,
        title="To Keep",
        position=1,
        status="PENDING",
        due_at=datetime.now(timezone.utc),
    )
    db_session.add_all([m_pending, m_retain])
    await db_session.commit()
    await db_session.refresh(m_pending)
    await db_session.refresh(m_retain)

    draft = RoadmapDraft(
        type="roadmap",
        goalId=str(test_goal.id),
        goalTitle="Title",
        targetDate=datetime.now(timezone.utc).date() + timedelta(days=10),
        milestones=[
            MilestoneDraft(
                id=str(m_retain.id),
                title="To Keep",
                targetDate=datetime.now(timezone.utc).date(),
                expectedOutcome="Outcome",
            )
        ],
    )

    save_payload = RoadmapSave(draft=draft, idempotency_key="roadmap_key_rem")
    updated_goal = await goals_service.update_from_roadmap(
        db_session, test_goal.id, save_payload, test_user.id
    )
    await db_session.commit()

    # Check reminder cleanup
    reminders = (
        await db_session.scalars(
            select(Reminder).where(Reminder.milestone_id == m_pending.id)
        )
    ).all()
    # It cascades delete because of SQLAlchemy relationship, or explicitly cancels.
    assert len(reminders) == 0

    m_check = await db_session.scalar(
        select(Milestone).where(Milestone.id == m_pending.id)
    )
    assert m_check is None

    m_retain_check = await db_session.scalar(
        select(Milestone).where(Milestone.id == m_retain.id)
    )
    assert m_retain_check is not None

    assert len(updated_goal.milestones) >= 1


async def test_get_goal_draft_timezone(db_session, test_user, test_goal):

    settings = UserSettings(user_id=test_user.id, timezone="Asia/Ho_Chi_Minh")
    db_session.add(settings)
    await db_session.flush()

    m = Milestone(
        goal_id=test_goal.id,
        title="TZ Test",
        position=0,
        status="PENDING",
        # 10 PM UTC is 5 AM next day in Asia/Ho_Chi_Minh
        due_at=datetime(2026, 1, 1, 22, 0, tzinfo=timezone.utc),
    )
    db_session.add(m)
    await db_session.commit()

    draft = await goals_service.get_goal_draft(db_session, test_goal.id, test_user.id)
    # The date should be Jan 2nd in Ho Chi Minh City
    assert draft.milestones[0].targetDate.day == 2


async def test_update_from_roadmap_completed_milestones_are_immutable(
    db_session, test_user, test_goal
):
    # Setup goal with a COMPLETED milestone
    m1 = Milestone(
        goal_id=test_goal.id,
        title="Original Title",
        expected_outcome="Original Outcome",
        position=0,
        status="COMPLETED",
        completed_at=datetime(2026, 5, 5, tzinfo=timezone.utc),
        due_at=datetime(2026, 6, 1, tzinfo=timezone.utc),
    )
    db_session.add(m1)
    await db_session.commit()
    await db_session.refresh(m1)

    # Draft attempts to change the COMPLETED milestone's historical data
    draft = RoadmapDraft(
        type="roadmap",
        goalId=str(test_goal.id),
        goalTitle="Title",
        targetDate=datetime.now(timezone.utc).date() + timedelta(days=10),
        milestones=[
            MilestoneDraft(
                id=str(m1.id),
                title="Hacked Title",
                targetDate=datetime(2026, 10, 1, tzinfo=timezone.utc).date(),
                expectedOutcome="Hacked Outcome",
            )
        ],
    )

    save_payload = RoadmapSave(draft=draft, idempotency_key="roadmap_key_immutable")
    updated_goal = await goals_service.update_from_roadmap(
        db_session, test_goal.id, save_payload, test_user.id
    )
    await db_session.commit()
    await db_session.refresh(updated_goal)

    milestones = sorted(updated_goal.milestones, key=lambda m: m.position)
    assert len(milestones) == 1

    m_check = milestones[0]
    assert m_check.id == m1.id
    assert m_check.status == "COMPLETED"
    assert m_check.title == "Original Title"
    assert m_check.expected_outcome == "Original Outcome"
    assert m_check.due_at == datetime(2026, 6, 1, tzinfo=timezone.utc)
    assert m_check.completed_at == datetime(2026, 5, 5, tzinfo=timezone.utc)


async def test_milestone_date_timezone_round_trip(db_session, test_user, test_goal):
    # Set user timezone to Asia/Ho_Chi_Minh
    user_settings = await db_session.scalar(
        select(UserSettings).where(UserSettings.user_id == test_user.id)
    )
    if not user_settings:
        user_settings = UserSettings(user_id=test_user.id, timezone="Asia/Ho_Chi_Minh")
        db_session.add(user_settings)
    else:
        user_settings.timezone = "Asia/Ho_Chi_Minh"
    await db_session.commit()

    # Create milestone using target_date
    m_create = MilestoneCreate(
        title="TZ Test", target_date=date(2026, 10, 1), status="PENDING"
    )
    m = await goals_service.create_milestone(
        db_session, test_goal.id, m_create, test_user.id
    )
    await db_session.commit()
    await db_session.refresh(m)

    # Check persistence and retrieval
    goal = await goals_service.get_goal(db_session, test_goal.id, test_user.id)
    retrieved_m = next(mil for mil in goal.milestones if mil.id == m.id)

    assert retrieved_m.target_date == date(2026, 10, 1)

    # Change timezone to America/New_York and test update
    user_settings.timezone = "America/New_York"
    await db_session.commit()

    m_update = MilestoneUpdate(target_date=date(2026, 11, 5))
    await goals_service.update_milestone(
        db_session, test_goal.id, m.id, m_update, test_user.id
    )
    await db_session.commit()

    goal2 = await goals_service.get_goal(db_session, test_goal.id, test_user.id)
    retrieved_m2 = next(mil for mil in goal2.milestones if mil.id == m.id)

    assert retrieved_m2.target_date == date(2026, 11, 5)
