import pytest
from datetime import timedelta
from app.db.models.daily_plans import DailyPlan, PlanBlock
from app.db.models.tasks import Task
from app.services.statistics_service import get_statistics_summary
from app.services.focus_service import focus_service
from app.schemas.focus import FocusSessionStart, FocusSessionFinish

pytestmark = pytest.mark.asyncio

async def test_statistics_core_loop_integration(
    db_session, test_user, test_task, test_daily_plan, test_plan_block, clock
):
    # 1-3. Create user/settings, ACTIVE DailyPlan, task + TASK PlanBlock (already done via fixtures)
    test_daily_plan.status = "ACTIVE"
    test_daily_plan.plan_date = clock.instant.date()
    test_daily_plan.timezone_snapshot = "UTC"
    test_plan_block.status = "PLANNED"
    await db_session.commit()
    
    # Pre-check statistics
    summary_before = await get_statistics_summary(db_session, test_user.id, clock.instant.date(), clock.instant.date())
    assert summary_before.completed_plan_count == 0
    assert summary_before.unfinished_plan_count == 1
    assert summary_before.study_time_hours == 0
    assert summary_before.study_time_minutes == 0
    
    # 4. Start a real focus session
    run = await focus_service.start_session(db_session, test_user.id, FocusSessionStart(
        task_id=test_task.id, planned_focus_seconds=1500, block_id=test_plan_block.id
    ))
    
    # 5. Advance controlled test clock
    clock.advance(1500) # 25 minutes
    
    # 6-7. Finish with qualifying outcome DONE
    run = await focus_service.finish_session(
        db_session, test_user.id, FocusSessionFinish(
            run_id=run.id, outcome="DONE", actual_duration_seconds=1500, should_replan=False
        )
    )
    
    # 8. Verify mutated records
    await db_session.refresh(run)
    assert run.status == "ENDED"
    assert run.actual_duration_seconds == 1500
    
    await db_session.refresh(test_task)
    assert test_task.status == "COMPLETED"
    
    await db_session.refresh(test_daily_plan)
    assert test_daily_plan.status == "COMPLETED"
    
    # 9-10. Call Statistics and verify aggregate
    summary_after = await get_statistics_summary(db_session, test_user.id, clock.instant.date(), clock.instant.date())
    assert summary_after.study_time_hours == 0
    assert summary_after.study_time_minutes == 25
    assert summary_after.completed_plan_count == 1
    assert summary_after.unfinished_plan_count == 0
    assert summary_after.study_day_count == 1
    
    # 11-13. Repeated read (same session)
    # Limitation: This uses the same db_session and is not a true cross-session reload test.
    # An independent session is currently unavailable in this test context.
    summary_after_again = await get_statistics_summary(db_session, test_user.id, clock.instant.date(), clock.instant.date())
    assert summary_after_again.study_time_minutes == 25
    assert summary_after_again.completed_plan_count == 1

async def test_partial_plan_integration(
    db_session, test_user, test_task, test_daily_plan, test_plan_block, clock
):
    # Add a second task and block
    task2 = Task(user_id=test_user.id, title="Second task", status="PENDING", estimated_duration_minutes=25)
    db_session.add(task2)
    await db_session.flush()
    block2 = PlanBlock(daily_plan_id=test_daily_plan.id, block_type="TASK", task_id=task2.id, position=2, status="PLANNED", planned_start_at=clock.instant, planned_end_at=clock.instant + timedelta(minutes=25))
    db_session.add(block2)
    
    test_daily_plan.status = "ACTIVE"
    test_daily_plan.plan_date = clock.instant.date()
    await db_session.commit()
    
    # Start and finish first task
    run = await focus_service.start_session(db_session, test_user.id, FocusSessionStart(
        task_id=test_task.id, planned_focus_seconds=1500, block_id=test_plan_block.id
    ))
    clock.advance(1500)
    await focus_service.finish_session(
        db_session, test_user.id, FocusSessionFinish(
            run_id=run.id, outcome="DONE", actual_duration_seconds=1500, should_replan=False
        )
    )
    
    await db_session.refresh(test_daily_plan)
    assert test_daily_plan.status == "ACTIVE" # because task2 is pending
    
    summary_mid = await get_statistics_summary(db_session, test_user.id, clock.instant.date(), clock.instant.date())
    assert summary_mid.unfinished_plan_count == 1
    assert summary_mid.completed_plan_count == 0
    
    # Start and finish second task
    run2 = await focus_service.start_session(db_session, test_user.id, FocusSessionStart(
        task_id=task2.id, planned_focus_seconds=1500, block_id=block2.id
    ))
    clock.advance(1500)
    await focus_service.finish_session(
        db_session, test_user.id, FocusSessionFinish(
            run_id=run2.id, outcome="DONE", actual_duration_seconds=1500, should_replan=False
        )
    )
    
    await db_session.refresh(test_daily_plan)
    assert test_daily_plan.status == "COMPLETED"
    
    summary_final = await get_statistics_summary(db_session, test_user.id, clock.instant.date(), clock.instant.date())
    assert summary_final.unfinished_plan_count == 0
    assert summary_final.completed_plan_count == 1
    assert summary_final.study_time_minutes == 50

async def test_replan_preservation(
    db_session, test_user, test_task, test_daily_plan, test_plan_block, test_availability_window, clock
):
    test_daily_plan.status = "ACTIVE"
    test_daily_plan.plan_date = clock.instant.date()
    await db_session.commit()
    
    # Finish task1 with NEED_MORE_TIME and trigger replan
    run = await focus_service.start_session(db_session, test_user.id, FocusSessionStart(
        task_id=test_task.id, planned_focus_seconds=1500, block_id=test_plan_block.id
    ))
    clock.advance(1500)
    await focus_service.finish_session(
        db_session, test_user.id, FocusSessionFinish(
            run_id=run.id, outcome="NEED_MORE_TIME", actual_duration_seconds=1500, should_replan=True
        )
    )
    
    await db_session.refresh(test_daily_plan)
    assert test_daily_plan.status == "ACTIVE"
    
    summary = await get_statistics_summary(db_session, test_user.id, clock.instant.date(), clock.instant.date())
    assert summary.unfinished_plan_count == 1
    assert summary.completed_plan_count == 0
    assert summary.study_time_minutes == 25
