from datetime import datetime, time, timedelta, timezone
from uuid import uuid4

from app.ai.coach.proactive import NudgeGate


def test_nudge_deduplicates_and_enforces_cooldown():
    gate = NudgeGate(cooldown=timedelta(minutes=30))
    user = uuid4()
    now = datetime(2026, 9, 20, 10, tzinfo=timezone.utc)
    assert (
        gate.evaluate(
            user_id=user, event_id="1", event_name="NEED_MORE_TIME", local_now=now
        )
        is None
    )
    assert (
        gate.evaluate(
            user_id=user, event_id="1", event_name="NEED_MORE_TIME", local_now=now
        )
        is None
    )
    assert gate.evaluate(
        user_id=user,
        event_id="2",
        event_name="NEED_MORE_TIME",
        local_now=now + timedelta(minutes=1),
    )
    assert (
        gate.evaluate(
            user_id=user,
            event_id="3",
            event_name="BEHIND_SCHEDULE",
            local_now=now + timedelta(minutes=20),
        )
        is None
    )
    assert gate.evaluate(
        user_id=user,
        event_id="4",
        event_name="BEHIND_SCHEDULE",
        local_now=now + timedelta(minutes=31),
    )


def test_skip_requires_two_events_and_morning_no_plan_is_immediate():
    gate = NudgeGate()
    user = uuid4()
    now = datetime(2026, 9, 20, 9, tzinfo=timezone.utc)
    assert (
        gate.evaluate(user_id=user, event_id="s1", event_name="SKIP", local_now=now)
        is None
    )
    assert gate.evaluate(user_id=user, event_id="s2", event_name="SKIP", local_now=now)
    other = uuid4()
    assert (
        gate.evaluate(
            user_id=other, event_id="m1", event_name="MORNING_NO_PLAN", local_now=now
        )["action"]
        == "PLAN_TODAY"
    )


def test_persisted_focus_streak_can_drive_nudge_after_process_restart():
    gate = NudgeGate()
    user = uuid4()
    now = datetime(2026, 9, 20, 10, tzinfo=timezone.utc)
    assert (
        gate.evaluate(
            user_id=user,
            event_id="focus-1",
            event_name="NEED_MORE_TIME",
            local_now=now,
            consecutive_count=1,
        )
        is None
    )
    assert gate.evaluate(
        user_id=user,
        event_id="focus-2",
        event_name="NEED_MORE_TIME",
        local_now=now,
        consecutive_count=2,
    )


def test_nudge_respects_overnight_quiet_hours():
    gate = NudgeGate()
    result = gate.evaluate(
        user_id=uuid4(),
        event_id="quiet",
        event_name="NEED_MORE_TIME",
        local_now=datetime(2026, 9, 20, 23, tzinfo=timezone.utc),
        quiet_start=time(22),
        quiet_end=time(7),
        quiet_enabled=True,
    )
    assert result is None
