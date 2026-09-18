import uuid

import pytest_asyncio
from app.db.models.tasks import Task, TaskDependency
from app.db.models.users import User
from sqlalchemy.ext.asyncio import AsyncSession


@pytest_asyncio.fixture
async def test_task(db_session: AsyncSession, test_user: User) -> Task:
    """Creates a simple task for the test user."""
    task = Task(
        id=uuid.uuid4(),
        user_id=test_user.id,
        title="Test Task",
        scheduling_type="FLEXIBLE",
        estimated_duration_minutes=30,
        is_splittable=False,
        status="PENDING",
    )
    db_session.add(task)
    await db_session.commit()
    await db_session.refresh(task)
    return task


@pytest_asyncio.fixture
async def test_splittable_task(db_session: AsyncSession, test_user: User) -> Task:
    """Creates a splittable task."""
    task = Task(
        id=uuid.uuid4(),
        user_id=test_user.id,
        title="Splittable Task",
        scheduling_type="FLEXIBLE",
        estimated_duration_minutes=120,
        is_splittable=True,
        min_split_duration_minutes=30,
        status="PENDING",
    )
    db_session.add(task)
    await db_session.commit()
    await db_session.refresh(task)
    return task


@pytest_asyncio.fixture
async def test_task_dependency(
    db_session: AsyncSession, test_task: Task, test_splittable_task: Task
) -> TaskDependency:
    """Creates a dependency where test_splittable_task depends on test_task."""
    dep = TaskDependency(
        task_id=test_splittable_task.id, depends_on_task_id=test_task.id
    )
    db_session.add(dep)
    await db_session.commit()
    await db_session.refresh(dep)
    return dep
