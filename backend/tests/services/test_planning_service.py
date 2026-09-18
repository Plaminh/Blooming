from datetime import date, datetime, timezone
from types import SimpleNamespace
from uuid import UUID, uuid4

import pytest
from app.core.errors import PlanAlreadyExistsError, ResourceNotFoundError
from app.crud.crud_daily_plan import daily_plan as crud_daily_plan
from app.db.models.daily_plans import DailyPlan, PlanBlock
from app.services.planning_service import planning_service
from sqlalchemy import select, text
from sqlalchemy.exc import IntegrityError

pytestmark = pytest.mark.integration
NOW = datetime(2026, 1, 1, 8, tzinfo=timezone.utc)
DAY = date(2026, 1, 1)


async def create_plan(db, user_id, status="DRAFT", plan_date=DAY, plan_id=None):
    plan = DailyPlan(
        id=plan_id or uuid4(),
        user_id=user_id,
        plan_date=plan_date,
        timezone_snapshot="UTC",
        status=status,
        confirmed_at=None if status == "DRAFT" else NOW,
        completed_at=NOW if status == "COMPLETED" else None,
    )
    db.add(plan)
    await db.commit()
    return plan


async def test_one_active_plan_per_user_date(db_session, test_user):
    draft = await crud_daily_plan.create_draft(
        db_session,
        user_id=test_user.id,
        plan_date=DAY,
        timezone_snapshot="UTC",
        reality_check="COMFORTABLE",
    )
    await db_session.commit()
    saved = await planning_service.save_daily_plan(
        db_session, SimpleNamespace(draft_id=draft.id), test_user.id
    )
    assert saved.status == "CONFIRMED"
    with pytest.raises(PlanAlreadyExistsError):
        await crud_daily_plan.create_draft(
            db_session,
            user_id=test_user.id,
            plan_date=DAY,
            timezone_snapshot="UTC",
            reality_check="COMFORTABLE",
        )
    assert len((await db_session.scalars(select(DailyPlan))).all()) == 1


@pytest.mark.parametrize("old_status", ["CONFIRMED", "ACTIVE"])
@pytest.mark.parametrize("old_first", [True, False])
async def test_replace_existing_preserves_history_and_only_one_active(
    db_session, test_user, old_status, old_first
):
    # The index includes DRAFT, so two active drafts cannot coexist. A historical
    # plan is a valid persisted candidate for save_daily_plan's replacement path.
    old = await create_plan(
        db_session, test_user.id, old_status, plan_id=UUID(int=1 if old_first else 2)
    )
    candidate = await create_plan(
        db_session, test_user.id, "ARCHIVED", plan_id=UUID(int=2 if old_first else 1)
    )
    block = PlanBlock(
        daily_plan_id=old.id,
        block_type="BREAK",
        title="Historical break",
        planned_start_at=NOW,
        planned_end_at=NOW.replace(hour=9),
        position=0,
    )
    db_session.add(block)
    await db_session.commit()
    old_id, candidate_id, block_id = old.id, candidate.id, block.id
    saved = await planning_service.save_daily_plan(
        db_session,
        SimpleNamespace(draft_id=candidate_id, replace_existing=True),
        test_user.id,
    )
    assert saved.id == candidate_id
    db_session.expire_all()
    old = await db_session.get(DailyPlan, old_id)
    assert (old.status, old.plan_date) == ("ARCHIVED", DAY)
    active = (
        await db_session.scalars(
            select(DailyPlan).where(
                DailyPlan.status.in_(("DRAFT", "CONFIRMED", "ACTIVE"))
            )
        )
    ).all()
    assert [(p.id, p.status, p.plan_date) for p in active] == [
        (candidate_id, "CONFIRMED", DAY)
    ]
    historical = await db_session.get(PlanBlock, block_id)
    assert (
        historical.daily_plan_id,
        historical.title,
        historical.planned_start_at,
    ) == (old_id, "Historical break", NOW)


async def test_replace_existing_false_rejected(db_session, test_user):
    old = await create_plan(db_session, test_user.id, "ACTIVE")
    candidate = await create_plan(db_session, test_user.id, "ARCHIVED")
    with pytest.raises(PlanAlreadyExistsError):
        await planning_service.save_daily_plan(
            db_session,
            SimpleNamespace(draft_id=candidate.id, replace_existing=False),
            test_user.id,
        )
    await db_session.refresh(old)
    await db_session.refresh(candidate)
    assert (old.status, candidate.status) == ("ACTIVE", "ARCHIVED")


async def test_same_date_different_users(db_session, test_user, test_user_two):
    one = await create_plan(db_session, test_user.id)
    two = await create_plan(db_session, test_user_two.id)
    for plan in (one, two):
        saved = await planning_service.save_daily_plan(
            db_session, SimpleNamespace(draft_id=plan.id), plan.user_id
        )
        assert saved.status == "CONFIRMED"
    assert len((await db_session.scalars(select(DailyPlan))).all()) == 2


async def test_different_dates_one_user(db_session, test_user):
    for day in (DAY, date(2026, 1, 2)):
        draft = await create_plan(db_session, test_user.id, plan_date=day)
        saved = await planning_service.save_daily_plan(
            db_session, SimpleNamespace(draft_id=draft.id), test_user.id
        )
        assert (saved.status, saved.plan_date) == ("CONFIRMED", day)
    assert len((await db_session.scalars(select(DailyPlan))).all()) == 2


@pytest.mark.parametrize("status", ["DRAFT", "CONFIRMED", "ACTIVE"])
async def test_duplicate_active_plans_rejected_by_postgresql(
    db_session, test_user, status
):
    await create_plan(db_session, test_user.id, status)
    with pytest.raises(IntegrityError) as exc:
        await db_session.execute(
            text("""
            INSERT INTO daily_plans (user_id, plan_date, status, timezone_snapshot, confirmed_at)
            VALUES (:user_id, :day, :status, 'UTC', :now)
        """),
            {"user_id": test_user.id, "day": DAY, "status": status, "now": NOW},
        )
    assert (
        exc.value.orig.diag.constraint_name == "daily_plans_one_active_per_local_date"
    )
    await db_session.rollback()


async def test_multiple_archived_completed_plans_allowed(db_session, test_user):
    for status in ("ARCHIVED", "ARCHIVED", "COMPLETED", "COMPLETED", "ACTIVE"):
        await create_plan(db_session, test_user.id, status)
    plans = (await db_session.scalars(select(DailyPlan))).all()
    assert sorted(p.status for p in plans) == [
        "ACTIVE",
        "ARCHIVED",
        "ARCHIVED",
        "COMPLETED",
        "COMPLETED",
    ]
    assert all(p.completed_at == NOW for p in plans if p.status == "COMPLETED")


async def test_completed_requires_completed_at(db_session, test_user):
    with pytest.raises(IntegrityError) as exc:
        await db_session.execute(
            text("""
            INSERT INTO daily_plans (user_id, plan_date, status, timezone_snapshot, confirmed_at)
            VALUES (:user_id, :day, 'COMPLETED', 'UTC', :now)
        """),
            {"user_id": test_user.id, "day": DAY, "now": NOW},
        )
    assert exc.value.orig.diag.constraint_name == "daily_plans_completion_valid"
    await db_session.rollback()


async def test_cross_user_save_rejected(db_session, test_user, test_user_two):
    draft = await create_plan(db_session, test_user.id)
    with pytest.raises(ResourceNotFoundError):
        await planning_service.save_daily_plan(
            db_session, SimpleNamespace(draft_id=draft.id), test_user_two.id
        )
    await db_session.refresh(draft)
    assert draft.status == "DRAFT"
