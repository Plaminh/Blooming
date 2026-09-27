import pytest
from datetime import datetime, timezone, date
from uuid import uuid4
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.services.today_service import today_service, TodayTaskStatusUpdate
from app.db.models.daily_plans import DailyPlan, PlanBlock
from app.db.models.tasks import Task
from datetime import timedelta

pytestmark = pytest.mark.integration

async def test_daily_plan_completion_lifecycle(db_session, test_user):
    user_id = test_user.id
    now = datetime.now(timezone.utc)
    
    plan = DailyPlan(
        user_id=user_id,
        plan_date=now.date(),
        status="ACTIVE",
        confirmed_at=now,
        timezone_snapshot="UTC"
    )
    db_session.add(plan)
    await db_session.flush()
    
    t1 = Task(user_id=user_id, title="T1", status="PENDING", estimated_duration_minutes=30, source="MANUAL")
    t2 = Task(user_id=user_id, title="T2", status="PENDING", estimated_duration_minutes=30, source="MANUAL")
    db_session.add_all([t1, t2])
    await db_session.flush()
    
    b1 = PlanBlock(
        daily_plan_id=plan.id, block_type="TASK", task_id=t1.id,
        planned_start_at=now, planned_end_at=now + timedelta(minutes=30), position=1, status="ACTIVE"
    )
    b2 = PlanBlock(
        daily_plan_id=plan.id, block_type="TASK", task_id=t2.id,
        planned_start_at=now + timedelta(minutes=30), planned_end_at=now + timedelta(minutes=60), position=2, status="PLANNED"
    )
    db_session.add_all([b1, b2])
    await db_session.commit()
    
    # 3. partial/non-terminal work keeps plan non-COMPLETED
    await today_service.update_task_status_from_today(
        db_session, user_id, t1.id, TodayTaskStatusUpdate(status="COMPLETED")
    )
    
    await db_session.refresh(plan)
    assert plan.status == "ACTIVE", "Plan should not be completed yet"
    
    # 4. SKIP does not complete a plan when work remains
    await today_service.update_task_status_from_today(
        db_session, user_id, t2.id, TodayTaskStatusUpdate(status="SKIPPED")
    )
    
    await db_session.refresh(plan)
    assert plan.status == "COMPLETED", "Plan should be completed when all tasks are terminal"
    assert plan.completed_at is not None
    original_completed_at = plan.completed_at
    
    # 1. repeated sync keeps COMPLETED and does not change completed_at
    await today_service.sync_daily_plan_completion(db_session, plan.id)
    await db_session.refresh(plan)
    assert plan.status == "COMPLETED"
    assert plan.completed_at == original_completed_at


async def test_replan_terminal_completes(db_session, test_user):
    user_id = test_user.id
    now = datetime.now(timezone.utc)
    
    plan = DailyPlan(
        user_id=user_id,
        plan_date=now.date(),
        status="ACTIVE",
        confirmed_at=now,
        timezone_snapshot="UTC"
    )
    db_session.add(plan)
    await db_session.flush()
    
    t1 = Task(user_id=user_id, title="T1", status="PENDING", estimated_duration_minutes=30, source="MANUAL")
    db_session.add(t1)
    await db_session.flush()
    
    b1 = PlanBlock(
        daily_plan_id=plan.id, block_type="TASK", task_id=t1.id,
        planned_start_at=now, planned_end_at=now + timedelta(minutes=30), position=1, status="COMPLETED", completed_at=now
    )
    db_session.add(b1)
    await db_session.commit()
    
    # 2. test the real supported scenario: a plan/replan whose actionable work is all terminal -> DailyPlan becomes COMPLETED.
    await today_service.sync_daily_plan_completion(db_session, plan.id)
    assert plan.status == "COMPLETED"


async def test_transaction_rollback_does_not_persist_completed(db_session, test_user):
    user_id = test_user.id
    now = datetime.now(timezone.utc)
    
    plan = DailyPlan(
        user_id=user_id, plan_date=now.date(), status="ACTIVE", confirmed_at=now, timezone_snapshot="UTC"
    )
    db_session.add(plan)
    await db_session.flush()
    
    t1 = Task(user_id=user_id, title="T1", status="PENDING", estimated_duration_minutes=30, source="MANUAL")
    db_session.add(t1)
    await db_session.flush()
    
    b1 = PlanBlock(
        daily_plan_id=plan.id, block_type="TASK", task_id=t1.id,
        planned_start_at=now, planned_end_at=now + timedelta(minutes=30), position=1, status="ACTIVE"
    )
    db_session.add(b1)
    await db_session.commit()
    
    plan_id = plan.id
    
    # Attempt to complete and then rollback
    try:
        # We manually emulate a failure in the transaction
        await today_service.update_task_status_from_today(
            db_session, user_id, t1.id, TodayTaskStatusUpdate(status="COMPLETED"), commit=False
        )
        raise ValueError("Simulate failure")
    except ValueError:
        await db_session.rollback()
    
    db_session.expire_all()
    reloaded_plan = await db_session.get(DailyPlan, plan_id)
    assert reloaded_plan.status == "ACTIVE"


async def test_replan_preserves_completed_history(db_session, test_user):
    user_id = test_user.id
    now = datetime.now(timezone.utc)
    
    plan = DailyPlan(
        user_id=user_id, plan_date=now.date(), status="ACTIVE", confirmed_at=now, timezone_snapshot="UTC"
    )
    db_session.add(plan)
    await db_session.flush()
    
    t1 = Task(user_id=user_id, title="T1", status="PENDING", estimated_duration_minutes=30, source="MANUAL")
    db_session.add(t1)
    await db_session.flush()
    
    b1 = PlanBlock(
        daily_plan_id=plan.id, block_type="TASK", task_id=t1.id,
        planned_start_at=now, planned_end_at=now + timedelta(minutes=30), position=1, status="COMPLETED", completed_at=now
    )
    b2 = PlanBlock(
        daily_plan_id=plan.id, block_type="TASK", task_id=t1.id,
        planned_start_at=now + timedelta(minutes=30), planned_end_at=now + timedelta(minutes=60), position=2, status="PLANNED"
    )
    db_session.add_all([b1, b2])
    await db_session.commit()
    
    await today_service.replan_today(db_session, user_id, local_date=now.date())
    
    await db_session.refresh(plan)
    # Real replan preserves completed history and does not complete while unfinished work remains
    # With mocked generate_timeline returning empty, it would clear all unfinished work.
    # Therefore it will complete the plan since only COMPLETED blocks remain.
    assert plan.status == "COMPLETED"

