from datetime import date, datetime, timedelta, timezone
from uuid import uuid4
import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.daily_plans import DailyPlan, PlanBlock, AvailabilityWindow
from app.db.models.tasks import Task, TaskDependency
from app.schemas.drafts import TodayDraft
from app.services.today_service import today_service

pytestmark = pytest.mark.asyncio

async def test_today_draft_round_trip(async_client: AsyncClient, auth_headers: dict[str, str], test_user: dict, db_session: AsyncSession):
    today = date.today()
    
    # Create a task with complex scheduling constraints
    task1 = Task(
        user_id=test_user["id"],
        title="Complex Task",
        estimated_duration_minutes=60,
        category="Deep Work",
        priority="HIGH",
        importance="CORE",
        source="USER",
        preferred_break_duration_minutes=15,
        deadline_at=datetime.now(timezone.utc) + timedelta(days=2),
        scheduling_type="FIXED",
        fixed_start_at=datetime.now(timezone.utc).replace(hour=10, minute=0, second=0, microsecond=0),
        fixed_end_at=datetime.now(timezone.utc).replace(hour=11, minute=0, second=0, microsecond=0),
        is_splittable=True,
    )
    db_session.add(task1)
    
    task2 = Task(
        user_id=test_user["id"],
        title="Dependent Task",
        estimated_duration_minutes=30,
        category="Admin",
        priority="LOW",
        importance="OPTIONAL",
        source="USER",
        scheduling_type="FLEXIBLE",
        is_splittable=False,
    )
    db_session.add(task2)
    await db_session.flush()
    
    # Add dependency
    dep = TaskDependency(task_id=task2.id, depends_on_task_id=task1.id)
    db_session.add(dep)
    
    # Create the daily plan
    plan = DailyPlan(
        user_id=test_user["id"],
        plan_date=today,
        status="ACTIVE",
        timezone_snapshot="America/New_York",
    )
    db_session.add(plan)
    await db_session.flush()
    
    # Add blocks
    block1 = PlanBlock(
        daily_plan_id=plan.id,
        block_type="TASK",
        task_id=task1.id,
        position=0,
        status="PLANNED",
        planned_start_at=task1.fixed_start_at,
        planned_end_at=task1.fixed_end_at
    )
    block2 = PlanBlock(
        daily_plan_id=plan.id,
        block_type="TASK",
        task_id=task2.id,
        position=1,
        status="PLANNED",
        planned_start_at=task1.fixed_end_at,
        planned_end_at=task1.fixed_end_at + timedelta(minutes=30)
    )
    db_session.add_all([block1, block2])
    
    # Add availability window
    w_start = datetime.now(timezone.utc).replace(hour=9, minute=0, second=0, microsecond=0)
    w_end = datetime.now(timezone.utc).replace(hour=17, minute=0, second=0, microsecond=0)
    window = AvailabilityWindow(
        daily_plan_id=plan.id,
        available_start_at=w_start,
        available_end_at=w_end,
    )
    db_session.add(window)
    await db_session.commit()

    # Request the draft via API
    resp = await async_client.get(
        f"/api/v1/today/draft?date={today.isoformat()}",
        headers=auth_headers
    )
    assert resp.status_code == 200, resp.text
    
    data = resp.json()
    assert data["type"] == "today"
    assert data["planDate"] == today.isoformat()
    assert data["timezone"] == "America/New_York"
    
    windows = data["windows"]
    assert len(windows) == 1
    assert windows[0]["start"] == w_start.isoformat().replace('+00:00', 'Z')
    assert windows[0]["end"] == w_end.isoformat().replace('+00:00', 'Z')

    tasks = data["tasks"]
    assert len(tasks) == 2
    
    t1_draft = next(t for t in tasks if t["sourceTaskId"] == str(task1.id))
    assert t1_draft["title"] == "Complex Task"
    assert t1_draft["durationMin"] == 60
    assert t1_draft["priority"] == "HIGH"
    assert t1_draft["importance"] == "CORE"
    assert t1_draft["category"] == "Deep Work"
    assert t1_draft["schedulingType"] == "FIXED"
    assert t1_draft["splittable"] is True
    assert t1_draft["fixedStart"] == task1.fixed_start_at.isoformat().replace('+00:00', 'Z')
    assert t1_draft["fixedEnd"] == task1.fixed_end_at.isoformat().replace('+00:00', 'Z')
    assert t1_draft["deadline"] == task1.deadline_at.isoformat().replace('+00:00', 'Z')
    assert t1_draft["dependencies"] == []
    
    t2_draft = next(t for t in tasks if t["sourceTaskId"] == str(task2.id))
    assert t2_draft["title"] == "Dependent Task"
    assert t2_draft["durationMin"] == 30
    assert t2_draft["priority"] == "LOW"
    assert t2_draft["importance"] == "OPTIONAL"
    assert t2_draft["category"] == "Admin"
    assert t2_draft["schedulingType"] == "FLEXIBLE"
    assert t2_draft["splittable"] is False
    assert t2_draft["dependencies"] == [str(task1.id)]

async def test_today_draft_no_plan(async_client: AsyncClient, auth_headers: dict[str, str]):
    resp = await async_client.get(
        "/api/v1/today/draft?date=2099-01-01",
        headers=auth_headers
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["type"] == "today"
    assert data["tasks"] == []
    assert data["windows"] == []

async def test_today_draft_other_user_plan(async_client: AsyncClient, auth_headers: dict[str, str], db_session: AsyncSession):
    today = date.today()
    other_user_id = uuid4()
    
    # Create plan for another user
    plan = DailyPlan(
        user_id=other_user_id,
        plan_date=today,
        status="ACTIVE",
        timezone_snapshot="UTC"
    )
    db_session.add(plan)
    await db_session.commit()
    
    resp = await async_client.get(
        f"/api/v1/today/draft?date={today.isoformat()}",
        headers=auth_headers
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["type"] == "today"
    assert data["tasks"] == []
    assert data["windows"] == []
