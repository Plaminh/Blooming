import pytest
from datetime import date, datetime, timezone, timedelta
from app.db.models.daily_plans import DailyPlan
from app.services.statistics_service import get_statistics_summary

pytestmark = pytest.mark.asyncio

async def test_statistics_summary_plan_counts(db_session, test_user):
    today = date.today()
    now = datetime.now(timezone.utc)
    
    # 1 COMPLETED
    p1 = DailyPlan(
        user_id=test_user.id, plan_date=today, status="COMPLETED",
        timezone_snapshot="UTC", confirmed_at=now, completed_at=now
    )
    # 2 ACTIVE (unfinished)
    p2 = DailyPlan(
        user_id=test_user.id, plan_date=today - timedelta(days=1), status="ACTIVE",
        timezone_snapshot="UTC", confirmed_at=now
    )
    p3 = DailyPlan(
        user_id=test_user.id, plan_date=today - timedelta(days=2), status="CONFIRMED",
        timezone_snapshot="UTC", confirmed_at=now
    )
    # 1 DRAFT (excluded)
    p4 = DailyPlan(
        user_id=test_user.id, plan_date=today - timedelta(days=3), status="DRAFT",
        timezone_snapshot="UTC"
    )
    # 1 COMPLETED but outside range
    p5 = DailyPlan(
        user_id=test_user.id, plan_date=today - timedelta(days=10), status="COMPLETED",
        timezone_snapshot="UTC", confirmed_at=now, completed_at=now
    )
    
    db_session.add_all([p1, p2, p3, p4, p5])
    await db_session.commit()
    
    start_date = today - timedelta(days=7)
    end_date = today
    
    summary = await get_statistics_summary(db_session, test_user.id, start_date, end_date)
    
    assert summary.completed_plan_count == 1
    assert summary.unfinished_plan_count == 2
    
async def test_statistics_excludes_other_users_and_does_not_mutate(db_session, test_user, test_user_two):
    today = date.today()
    now = datetime.now(timezone.utc)
    
    p1 = DailyPlan(
        user_id=test_user.id, plan_date=today, status="ACTIVE",
        timezone_snapshot="UTC", confirmed_at=now
    )
    p2_other = DailyPlan(
        user_id=test_user_two.id, plan_date=today, status="ACTIVE",
        timezone_snapshot="UTC", confirmed_at=now
    )
    db_session.add_all([p1, p2_other])
    await db_session.commit()
    
    summary = await get_statistics_summary(db_session, test_user.id, today - timedelta(days=7), today)
    assert summary.unfinished_plan_count == 1
    
    await db_session.refresh(p1)
    assert p1.status == "ACTIVE" # Did not magically complete because it's empty

from app.db.models.focus import FocusRun

async def test_statistics_empty(db_session, test_user):
    target_date = date(2026, 6, 5)
    start_date = target_date - timedelta(days=7)
    summary = await get_statistics_summary(db_session, test_user.id, start_date, target_date)
    assert summary.completed_plan_count == 0
    assert summary.unfinished_plan_count == 0
    assert summary.study_time_hours == 0
    assert summary.study_time_minutes == 0
    assert summary.study_day_count == 0

async def test_statistics_focus_runs_and_deduplication(db_session, test_user):
    target_date = date(2026, 6, 5)
    now = datetime(2026, 6, 5, 12, 0, 0, tzinfo=timezone.utc)
    
    # 2 ended runs today: 30 mins (1800s) + 40 mins (2400s) = 70 mins
    fr1 = FocusRun(user_id=test_user.id, quick_task_title="t1", status="ENDED", planned_focus_seconds=1800, actual_duration_seconds=1800, started_at=now, ended_at=now)
    fr2 = FocusRun(user_id=test_user.id, quick_task_title="t2", status="ENDED", planned_focus_seconds=2400, actual_duration_seconds=2400, started_at=now, ended_at=now)
    
    # 1 ended run yesterday: 20 mins
    yesterday = now - timedelta(days=1)
    fr3 = FocusRun(user_id=test_user.id, quick_task_title="t3", status="ENDED", planned_focus_seconds=1200, actual_duration_seconds=1200, started_at=yesterday, ended_at=yesterday)
    
    # 1 ACTIVE run today (should be ignored for stats)
    fr4 = FocusRun(user_id=test_user.id, quick_task_title="t4", status="FOCUSING", planned_focus_seconds=1800, started_at=now)
    
    # 1 ENDED run but outside date range
    outside = now - timedelta(days=10)
    fr5 = FocusRun(user_id=test_user.id, quick_task_title="t5", status="ENDED", planned_focus_seconds=1800, actual_duration_seconds=1800, started_at=outside, ended_at=outside)
    
    db_session.add_all([fr1, fr2, fr3, fr4, fr5])
    await db_session.commit()
    
    start_date = target_date - timedelta(days=7)
    end_date = target_date
    
    summary = await get_statistics_summary(db_session, test_user.id, start_date, end_date)
    
    # 70 mins (today) + 20 mins (yesterday) = 90 mins -> 1 hour, 30 mins
    assert summary.study_time_hours == 1
    assert summary.study_time_minutes == 30
    
    # Study days: today and yesterday -> 2 days (deduplicating the 2 runs on today)
    assert summary.study_day_count == 2

from app.db.models.users import UserSettings
from sqlalchemy import select

async def test_statistics_timezone_boundary(db_session, test_user):
    # Timezone: Asia/Ho_Chi_Minh (UTC+7)
    # UTC timestamp: 2026-06-01T20:00:00Z -> Local time: 2026-06-02T03:00:00+07:00
    # Expected local study date: 2026-06-02
    
    # 1. Set the test user's persisted UserSettings.timezone
    result = await db_session.execute(select(UserSettings).where(UserSettings.user_id == test_user.id))
    settings = result.scalar_one_or_none()
    if not settings:
        settings = UserSettings(user_id=test_user.id, timezone="Asia/Ho_Chi_Minh")
        db_session.add(settings)
    else:
        settings.timezone = "Asia/Ho_Chi_Minh"
    
    # 3. Create the explicit ENDED FocusRun
    run_utc = datetime(2026, 6, 1, 20, 0, 0, tzinfo=timezone.utc)
    
    fr1 = FocusRun(
        user_id=test_user.id,
        quick_task_title="Late night study",
        status="ENDED",
        planned_focus_seconds=1800,
        actual_duration_seconds=1800,
        started_at=run_utc,
        ended_at=run_utc + timedelta(seconds=1800)
    )
    
    db_session.add(fr1)
    
    # 2. Commit it.
    await db_session.commit()
    
    # 4. Call get_statistics_summary using the same arguments/path production uses.
    # Test range: exactly 2026-06-02 local (should INCLUDE the run)
    start_date = date(2026, 6, 2)
    end_date = date(2026, 6, 2)
    
    # Note: requested_tz is NOT passed, it should rely on UserSettings.timezone
    summary_included = await get_statistics_summary(
        db_session, test_user.id, start_date, end_date
    )
    
    # 5. Assert local range 2026-06-02 -> includes 30 minutes / 1 study day
    assert summary_included.study_day_count == 1
    assert summary_included.study_time_minutes == 30
    
    # Test range: exactly 2026-06-01 local (should EXCLUDE the run)
    start_date_excl = date(2026, 6, 1)
    end_date_excl = date(2026, 6, 1)
    
    summary_excluded = await get_statistics_summary(
        db_session, test_user.id, start_date_excl, end_date_excl
    )
    
    # Assert local range 2026-06-01 -> excludes it
    assert summary_excluded.study_day_count == 0
    assert summary_excluded.study_time_minutes == 0
