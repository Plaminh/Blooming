from unittest.mock import AsyncMock
from uuid import uuid4

import pytest
from app.core.economy import WATER_PER_POMODORO
from app.core.errors import InvalidStatusTransitionError, ResourceNotFoundError
from app.db.models.daily_plans import PlanBlock, PlanRevision
from app.db.models.focus import FocusRun, FocusRunEvent
from app.db.models.garden import GardenState, RewardEvent
from app.db.models.tasks import Task
from app.schemas.focus import FocusSessionFinish, FocusSessionStart
from app.services.focus_service import focus_service
from app.services.today_service import today_service
from sqlalchemy import select

pytestmark = pytest.mark.integration


async def start(db, user, task):
    return await focus_service.start_session(
        db, user.id, FocusSessionStart(task_id=task.id, planned_focus_seconds=1500)
    )


async def test_focus_start_and_second_active_session_conflict(
    db_session, test_user, test_task, clock
):
    run = await start(db_session, test_user, test_task)
    assert run.status == "FOCUSING"
    assert run.started_at == clock.instant
    with pytest.raises(InvalidStatusTransitionError):
        await start(db_session, test_user, test_task)
    assert len((await db_session.scalars(select(FocusRun))).all()) == 1


@pytest.mark.parametrize("finish_paused", [False, True])
async def test_focus_pause_resume_and_actual_duration(
    db_session, test_user, test_task, clock, finish_paused
):
    run = await start(db_session, test_user, test_task)
    expected_end = run.expected_end_at
    clock.advance(600)
    run = await focus_service.pause_session(db_session, test_user.id)
    assert run.status == "PAUSED"
    assert run.paused_at == clock.instant
    clock.advance(120)
    if not finish_paused:
        run = await focus_service.resume_session(db_session, test_user.id)
        assert run.status == "FOCUSING"
        assert run.paused_at is None
        assert run.total_paused_seconds == 120
        assert (run.expected_end_at - expected_end).total_seconds() == 120
        clock.advance(300)
    run = await focus_service.finish_session(
        db_session,
        test_user.id,
        FocusSessionFinish(
            run_id=run.id, outcome="DONE", actual_duration_seconds=99999
        ),
    )
    assert run.total_paused_seconds == 120
    assert run.actual_duration_seconds == (600 if finish_paused else 900)
    assert run.ended_at == clock.instant
    assert run.paused_at is None
    events = (await db_session.scalars(select(FocusRunEvent.event_type))).all()
    assert sorted(events) == sorted(
        ["STARTED", "PAUSED", "ENDED"] + ([] if finish_paused else ["RESUMED"])
    )


@pytest.mark.parametrize(
    "outcome,task_status,water",
    [
        ("DONE", "COMPLETED", WATER_PER_POMODORO),
        ("FINISHED_EARLY", "COMPLETED", WATER_PER_POMODORO),
        ("NEED_MORE_TIME", "PENDING", WATER_PER_POMODORO),
        ("SKIP", "SKIPPED", 0),
    ],
)
async def test_supported_outcomes_and_exactly_once_rewards(
    db_session, test_user, test_task, clock, outcome, task_status, water
):
    run = await start(db_session, test_user, test_task)
    clock.advance(900)
    request = FocusSessionFinish(run_id=run.id, outcome=outcome)
    run = await focus_service.finish_session(db_session, test_user.id, request)
    assert (run.status, run.outcome, run.actual_duration_seconds) == (
        "ENDED",
        outcome,
        900,
    )
    await focus_service.finish_session(db_session, test_user.id, request)
    db_session.expire_all()
    task = await db_session.scalar(select(Task))
    assert task.status == task_status
    garden = await db_session.scalar(select(GardenState))
    assert (garden.water_balance if garden else 0) == water
    rewards = (
        await db_session.scalars(
            select(RewardEvent).where(RewardEvent.resource_type == "WATER")
        )
    ).all()
    assert len(rewards) == (1 if water else 0)
    if rewards:
        assert rewards[0].amount == water
        assert rewards[0].source_focus_run_id == request.run_id
        assert rewards[0].idempotency_key == f"focus_completed_{request.run_id}"
    ended = (
        await db_session.scalars(
            select(FocusRunEvent).where(FocusRunEvent.event_type == "ENDED")
        )
    ).all()
    assert len(ended) == 1


@pytest.mark.parametrize("should_replan", [False, True])
async def test_replan_only_when_requested(
    db_session,
    test_user,
    test_task,
    test_plan_block,
    test_availability_window,
    clock,
    monkeypatch,
    should_replan,
):
    spy = AsyncMock(wraps=today_service.replan_today)
    monkeypatch.setattr(today_service, "replan_today", spy)
    run = await start(db_session, test_user, test_task)
    clock.advance(600)
    run = await focus_service.finish_session(
        db_session,
        test_user.id,
        FocusSessionFinish(
            run_id=run.id, outcome="NEED_MORE_TIME", should_replan=should_replan
        ),
    )
    revisions = (await db_session.scalars(select(PlanRevision))).all()
    blocks = (await db_session.scalars(select(PlanBlock))).all()
    assert len(revisions) == int(should_replan)
    task_blocks = [block for block in blocks if block.block_type == "TASK"]
    assert len(task_blocks) == 1
    if should_replan:
        spy.assert_awaited_once_with(db_session, test_user.id, commit=False)
        # The elapsed block is immutable history; replanning only replaces
        # unfinished future work.
        assert task_blocks[0].planned_start_at < clock.instant
        assert run.replan is not None
        event = await db_session.scalar(
            select(FocusRunEvent).where(FocusRunEvent.event_type == "ENDED")
        )
        assert event.payload["replan"] is not None
    else:
        spy.assert_not_awaited()
        assert blocks[0].id == test_plan_block.id
        assert run.replan is None


async def test_finish_rolls_back_reward_task_and_replan(
    db_session,
    test_user,
    test_task,
    test_plan_block,
    test_availability_window,
    clock,
    monkeypatch,
):
    run = await start(db_session, test_user, test_task)
    run_id, user_id, task_id, block_id = (
        run.id,
        test_user.id,
        test_task.id,
        test_plan_block.id,
    )
    real_replan = today_service.replan_today

    async def fail_after_replan(*args, **kwargs):
        await real_replan(*args, **kwargs)
        raise RuntimeError("injected failure after replan writes")

    monkeypatch.setattr(today_service, "replan_today", fail_after_replan)
    with pytest.raises(RuntimeError, match="injected failure"):
        await focus_service.finish_session(
            db_session,
            user_id,
            FocusSessionFinish(run_id=run_id, outcome="DONE", should_replan=True),
        )
    # The request owns rollback; the service must not commit partial work.
    await db_session.rollback()
    db_session.expire_all()
    assert (await db_session.get(FocusRun, run_id)).status == "FOCUSING"
    assert (await db_session.get(Task, task_id)).status == "PENDING"
    assert (await db_session.get(PlanBlock, block_id)).status == "PLANNED"
    assert (await db_session.scalars(select(RewardEvent))).all() == []
    assert (await db_session.scalars(select(PlanRevision))).all() == []
    assert (await db_session.scalars(select(FocusRunEvent.event_type))).all() == [
        "STARTED"
    ]
    assert await db_session.get(GardenState, user_id) is None


async def test_cross_user_rejection(db_session, test_user, test_user_two, test_task):
    run = await start(db_session, test_user, test_task)
    with pytest.raises(ResourceNotFoundError):
        await focus_service.finish_session(
            db_session,
            test_user_two.id,
            FocusSessionFinish(run_id=run.id, outcome="DONE"),
        )
    await db_session.refresh(run)
    assert run.status == "FOCUSING"


async def test_semantic_missing_session_errors(db_session, test_user):
    with pytest.raises(ResourceNotFoundError):
        await focus_service.finish_session(
            db_session, test_user.id, FocusSessionFinish(run_id=uuid4(), outcome="DONE")
        )

async def test_focus_outcome_completes_daily_plan(db_session, test_user, test_task, test_daily_plan, test_plan_block, clock):
    from sqlalchemy import select
    from app.db.models.daily_plans import DailyPlan
    run = await start(db_session, test_user, test_task)
    clock.advance(600)
    await focus_service.finish_session(
        db_session,
        test_user.id,
        FocusSessionFinish(run_id=run.id, outcome="DONE", should_replan=False)
    )
    await db_session.refresh(test_daily_plan)
    assert test_daily_plan.status == "COMPLETED"
    assert test_daily_plan.completed_at is not None

async def test_focus_outcome_need_more_time_keeps_plan_active(db_session, test_user, test_task, test_daily_plan, test_plan_block, clock):
    from sqlalchemy import select
    from app.db.models.daily_plans import DailyPlan
    run = await start(db_session, test_user, test_task)
    clock.advance(600)
    await focus_service.finish_session(
        db_session,
        test_user.id,
        FocusSessionFinish(run_id=run.id, outcome="NEED_MORE_TIME", should_replan=False)
    )
    await db_session.refresh(test_daily_plan)
    assert test_daily_plan.status == "ACTIVE"
    assert test_daily_plan.completed_at is None
