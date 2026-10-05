import pytest
from datetime import datetime, timedelta, timezone
from app.services.today_service import today_service
from app.db.models.daily_plans import DailyPlan, PlanBlock, AvailabilityWindow
from app.db.models.tasks import Task
from app.db.models.focus import FocusRun

pytestmark = pytest.mark.integration

async def test_replan_historical_blocks(db_session, test_user):
    user_id = test_user.id
    now = datetime.now(timezone.utc)
    
    plan = DailyPlan(
        user_id=user_id,
        plan_date=now.date(),
        status="ACTIVE",
        confirmed_at=now,
        timezone_snapshot="UTC",
    )
    db_session.add(plan)
    await db_session.flush()

    db_session.add(AvailabilityWindow(
        daily_plan_id=plan.id,
        available_start_at=now - timedelta(hours=5),
        available_end_at=now + timedelta(hours=5)
    ))
    
    # 1. Missed flexible block
    t_missed = Task(user_id=user_id, title="Missed Flexible", estimated_duration_minutes=30, status="PENDING")
    # 2. Completed past block
    t_completed = Task(user_id=user_id, title="Completed Past", estimated_duration_minutes=30, status="COMPLETED")
    # 3. Fixed past block
    t_fixed = Task(
        user_id=user_id, 
        title="Fixed Past", 
        estimated_duration_minutes=30, 
        scheduling_type="FIXED", 
        status="PENDING",
        fixed_start_at=now - timedelta(minutes=180),
        fixed_end_at=now - timedelta(minutes=150)
    )
    
    db_session.add_all([t_missed, t_completed, t_fixed])
    await db_session.flush()

    b_missed = PlanBlock(
        daily_plan_id=plan.id, block_type="TASK", task_id=t_missed.id,
        planned_start_at=now - timedelta(minutes=60), planned_end_at=now - timedelta(minutes=30),
        position=1, status="PLANNED"
    )
    b_completed = PlanBlock(
        daily_plan_id=plan.id, block_type="TASK", task_id=t_completed.id,
        planned_start_at=now - timedelta(minutes=120), planned_end_at=now - timedelta(minutes=90),
        position=2, status="COMPLETED"
    )
    b_fixed = PlanBlock(
        daily_plan_id=plan.id, block_type="TASK", task_id=t_fixed.id,
        planned_start_at=now - timedelta(minutes=180), planned_end_at=now - timedelta(minutes=150),
        position=3, status="PLANNED"
    )
    
    db_session.add_all([b_missed, b_completed, b_fixed])
    await db_session.commit()

    await today_service.replan_today(db_session, user_id, local_date=now.date())
    
    await db_session.refresh(plan, ["plan_blocks"])
    
    blocks = sorted(plan.plan_blocks, key=lambda b: b.position)
    
    # b_missed should have a new block in the future because it was eligible for replan
    new_missed_blocks = [b for b in blocks if b.task_id == t_missed.id]
    assert len(new_missed_blocks) == 1
    assert new_missed_blocks[0].planned_start_at >= now
    
    # b_completed should remain untouched in the past
    completed_blocks = [b for b in blocks if b.task_id == t_completed.id]
    assert len(completed_blocks) == 1
    assert completed_blocks[0].planned_start_at == now - timedelta(minutes=120)
    
    # b_fixed should remain untouched in the past
    fixed_blocks = [b for b in blocks if b.task_id == t_fixed.id]
    assert len(fixed_blocks) == 1
    assert fixed_blocks[0].planned_start_at == now - timedelta(minutes=180)


async def test_replan_remaining_duration_after_focus(db_session, test_user):
    user_id = test_user.id
    now = datetime.now(timezone.utc)
    
    plan = DailyPlan(
        user_id=user_id,
        plan_date=now.date(),
        status="ACTIVE",
        confirmed_at=now,
        timezone_snapshot="UTC",
    )
    db_session.add(plan)
    await db_session.flush()
    
    # Wide window
    db_session.add(AvailabilityWindow(
        daily_plan_id=plan.id,
        available_start_at=now,
        available_end_at=now + timedelta(hours=5)
    ))
    await db_session.flush()

    # 60 minute task
    t_focus = Task(user_id=user_id, title="Partial Focus Task", estimated_duration_minutes=60, status="PENDING")
    db_session.add(t_focus)
    await db_session.flush()

    # Valid 25 min focus run, ended with NEED_MORE_TIME
    run = FocusRun(
        user_id=user_id, task_id=t_focus.id,
        planned_focus_seconds=25*60,
        status="ENDED", outcome="NEED_MORE_TIME",
        started_at=now - timedelta(minutes=25),
        ended_at=now,
        actual_duration_seconds=25*60
    )
    db_session.add(run)
    await db_session.commit()

    # Replan
    await today_service.replan_today(db_session, user_id, local_date=now.date())
    
    await db_session.refresh(plan, ["plan_blocks"])
    blocks = [b for b in plan.plan_blocks if b.task_id == t_focus.id]
    
    # Only 35 mins remaining (60 - 25)
    assert len(blocks) == 1
    duration = (blocks[0].planned_end_at - blocks[0].planned_start_at).total_seconds() / 60
    assert duration == 35
