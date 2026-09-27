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
