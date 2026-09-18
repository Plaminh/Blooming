import pytest
from app.db.models.users import User


@pytest.mark.integration
async def test_shared_factories_persist_valid_relationships(
    db_session,
    test_milestone,
    test_goal,
    test_task_dependency,
    test_task,
    test_splittable_task,
    test_focus_run_event,
    test_focus_session,
    test_reward_event,
    test_reminder_action,
    test_reminder,
    test_plant_ownership,
    test_plant,
    test_user_settings,
    test_user,
):
    assert test_milestone.goal_id == test_goal.id
    assert test_task_dependency.task_id == test_splittable_task.id
    assert test_task_dependency.depends_on_task_id == test_task.id
    assert test_focus_run_event.focus_run_id == test_focus_session.id
    assert test_reward_event.user_id == test_user.id
    assert test_reminder_action.reminder_id == test_reminder.id
    assert test_plant_ownership.plant_id == test_plant.id
    assert test_user_settings.user_id == test_user.id


from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession


@pytest.mark.integration
async def test_user_fixture_creation(db_session: AsyncSession, test_user: User):
    """Verify that test_user is created successfully."""
    result = await db_session.execute(select(User).where(User.id == test_user.id))
    db_user = result.scalar_one_or_none()
    assert db_user is not None
    assert db_user.email == test_user.email


@pytest.mark.integration
async def test_user_fixture_isolation_1(db_session: AsyncSession, test_user: User):
    """Count users. Should be exactly 1 in this isolated DB."""
    result = await db_session.execute(select(User))
    users = result.scalars().all()
    assert len(users) == 1


@pytest.mark.integration
async def test_user_fixture_isolation_2(db_session: AsyncSession, test_user: User):
    """Count users again in a separate test. Should STILL be exactly 1."""
    result = await db_session.execute(select(User))
    users = result.scalars().all()
    assert len(users) == 1
