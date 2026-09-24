"""Cluster 13 — Validation boundaries and duplicates.
Cluster 14 — Dependencies and fixed tasks (validator-level).

Test IDs: TD-008, TD-009, TD-010, TD-011, TD-012, TD-013, TD-014,
          TD-015, TD-020, CL-003 (fixed-task validator boundary)
"""

from __future__ import annotations

from datetime import date, datetime
from zoneinfo import ZoneInfo

import pytest
from pydantic import ValidationError

from app.ai.validators import check_today
from app.schemas.drafts import (
    AvailabilityWindowDraft,
    TaskDraft,
    TodayDraft,
)


def _draft(
    tasks: list[TaskDraft] | None = None,
    windows: list[AvailabilityWindowDraft] | None = None,
    plan_date: date | None = None,
) -> TodayDraft:
    return TodayDraft(
        planDate=plan_date or date(2026, 9, 20),
        timezone="UTC",
        windows=windows or [AvailabilityWindowDraft(start="09:00", end="17:00")],
        tasks=tasks or [],
    )


def _task(
    task_id: str = "d1",
    title: str = "Study",
    duration: int = 60,
    scheduling_type: str = "FLEXIBLE",
    fixed_start: datetime | None = None,
    fixed_end: datetime | None = None,
    dependencies: list[str] | None = None,
    importance: str = "CORE",
) -> TaskDraft:
    return TaskDraft(
        id=task_id,
        title=title,
        durationMin=duration,
        schedulingType=scheduling_type,
        fixedStart=fixed_start,
        fixedEnd=fixed_end,
        dependencies=dependencies or [],
        importance=importance,
    )


# ===========================================================================
# TD-008 / TD-009 — Duration range 5–480
# ===========================================================================
def test_td_008_duration_range_valid():
    """5–480 minutes is the valid range; exact boundaries must pass."""
    draft_5 = _draft(tasks=[_task(duration=5)])
    draft_480 = _draft(tasks=[_task(duration=480)])
    assert check_today(draft_5) == []
    assert check_today(draft_480) == []


def test_td_009_duration_4_invalid():
    """4 minutes is below the minimum → schema rejects it."""
    with pytest.raises((ValidationError, ValueError)):
        _task(duration=4)


def test_td_009_duration_481_invalid():
    """481 minutes exceeds the maximum → schema rejects it."""
    with pytest.raises((ValidationError, ValueError)):
        _task(duration=481)


def test_td_009_duration_0_invalid():
    """Zero duration must be rejected."""
    with pytest.raises((ValidationError, ValueError)):
        _task(duration=0)


def test_td_009_duration_negative_invalid():
    """Negative duration must be rejected."""
    with pytest.raises((ValidationError, ValueError)):
        _task(duration=-10)


def test_td_009_duration_480_valid():
    """480 is the maximum valid duration."""
    t = _task(duration=480)
    assert t.durationMin == 480
    draft = _draft(tasks=[t])
    assert "INVALID_DURATION" not in check_today(draft)


def test_td_009_duration_5_valid():
    """5 is the minimum valid duration."""
    t = _task(duration=5)
    assert t.durationMin == 5


# ===========================================================================
# TD-010 — Availability-window validation (schema level)
# ===========================================================================
def test_td_010_reversed_window_rejected():
    """Window with start >= end must be rejected by schema."""
    with pytest.raises((ValidationError, ValueError)):
        AvailabilityWindowDraft(start="17:00", end="09:00")


def test_td_010_equal_start_end_rejected():
    """Window with start == end must be rejected by schema."""
    with pytest.raises((ValidationError, ValueError)):
        AvailabilityWindowDraft(start="09:00", end="09:00")


def test_td_010_invalid_format_rejected():
    """Invalid time format must be rejected by schema."""
    with pytest.raises((ValidationError, ValueError)):
        AvailabilityWindowDraft(start="9:00", end="17:00")  # Missing leading zero


# ===========================================================================
# TD-011 — Unknown dependency IDs rejected
# ===========================================================================
def test_td_011_unknown_dependency_rejected():
    """Dependency referencing a non-existent task ID must be flagged."""
    tasks = [
        _task("d1", "Study", 60, dependencies=["d99"]),  # d99 does not exist
    ]
    draft = _draft(tasks=tasks)
    issues = check_today(draft)
    assert "INVALID_DEPENDENCY" in issues


def test_td_011_valid_dependency_accepted():
    """Dependency referencing an existing task ID must be accepted."""
    tasks = [
        _task("d1", "Study", 60, dependencies=[]),
        _task("d2", "Review", 30, dependencies=["d1"]),
    ]
    draft = _draft(tasks=tasks)
    issues = check_today(draft)
    assert "INVALID_DEPENDENCY" not in issues
    assert "CYCLIC_DEPENDENCY" not in issues


# ===========================================================================
# TD-012 — Self-dependency rejected
# ===========================================================================
def test_td_012_self_dependency_rejected():
    """A task that depends on itself must be flagged as INVALID_DEPENDENCY."""
    tasks = [_task("d1", "Study", 60, dependencies=["d1"])]
    draft = _draft(tasks=tasks)
    issues = check_today(draft)
    assert "INVALID_DEPENDENCY" in issues


# ===========================================================================
# TD-013 — Direct cycle detected
# ===========================================================================
def test_td_013_direct_cycle_detected():
    """A ↔ B cycle must be detected as CYCLIC_DEPENDENCY."""
    tasks = [
        _task("a", "Study", 60, dependencies=["b"]),
        _task("b", "Review", 30, dependencies=["a"]),
    ]
    draft = _draft(tasks=tasks)
    issues = check_today(draft)
    assert "CYCLIC_DEPENDENCY" in issues


# ===========================================================================
# TD-014 — Multi-node cycle detected
# ===========================================================================
def test_td_014_multi_node_cycle_detected():
    """A → B → C → A cycle must be detected."""
    tasks = [
        _task("a", "Task A", 30, dependencies=["c"]),
        _task("b", "Task B", 30, dependencies=["a"]),
        _task("c", "Task C", 30, dependencies=["b"]),
    ]
    draft = _draft(tasks=tasks)
    issues = check_today(draft)
    assert "CYCLIC_DEPENDENCY" in issues


def test_td_014_acyclic_chain_accepted():
    """A → B → C (no cycle) must not produce CYCLIC_DEPENDENCY."""
    tasks = [
        _task("a", "Task A", 30, dependencies=[]),
        _task("b", "Task B", 30, dependencies=["a"]),
        _task("c", "Task C", 30, dependencies=["b"]),
    ]
    draft = _draft(tasks=tasks)
    issues = check_today(draft)
    assert "CYCLIC_DEPENDENCY" not in issues


# ===========================================================================
# TD-015 — Duplicate task titles rejected
# ===========================================================================
def test_td_015_duplicate_titles_rejected():
    """Case/whitespace-normalized duplicate titles must be flagged."""
    tasks = [
        _task("d1", "Study"),
        _task("d2", "STUDY"),  # Same after normalization
    ]
    draft = _draft(tasks=tasks)
    issues = check_today(draft)
    assert "DUPLICATE_TITLE" in issues


def test_td_015_genuinely_different_titles_accepted():
    """Genuinely different titles must not trigger DUPLICATE_TITLE."""
    tasks = [
        _task("d1", "Study"),
        _task("d2", "Review"),
    ]
    draft = _draft(tasks=tasks)
    issues = check_today(draft)
    assert "DUPLICATE_TITLE" not in issues


# ===========================================================================
# TD-020 — Task count > 15 rejected
# ===========================================================================
def test_td_020_exactly_15_tasks_valid():
    """Exactly 15 tasks must be valid."""
    tasks = [_task(f"d{i}", f"Task {i}", 5) for i in range(1, 16)]
    draft = _draft(tasks=tasks)
    issues = check_today(draft)
    assert "TOO_MANY_TASKS" not in issues


def test_td_020_16_tasks_rejected():
    """16 tasks must be rejected with TOO_MANY_TASKS."""
    tasks = [_task(f"d{i}", f"Task {i}", 5) for i in range(1, 17)]
    draft = _draft(tasks=tasks)
    issues = check_today(draft)
    assert "TOO_MANY_TASKS" in issues


def test_td_020_over_limit_not_silently_truncated():
    """Over-limit drafts must report the issue, not silently truncate."""
    tasks = [_task(f"d{i}", f"Task {i}", 5) for i in range(1, 20)]
    draft = _draft(tasks=tasks)
    issues = check_today(draft)
    assert "TOO_MANY_TASKS" in issues
    # All 19 tasks remain in the draft — not silently removed
    assert len(draft.tasks) == 19


# ===========================================================================
# CL-003 — Fixed task with missing or invalid fixed times
# ===========================================================================
def test_cl_003_fixed_task_missing_start_flagged():
    """FIXED task with no fixedStart must be flagged as INVALID_FIXED_TIME."""
    tasks = [TaskDraft(
        id="d1", title="Meeting", durationMin=45,
        schedulingType="FIXED",  # No fixedStart/fixedEnd
    )]
    draft = _draft(tasks=tasks)
    issues = check_today(draft)
    assert "INVALID_FIXED_TIME" in issues


def test_cl_003_fixed_task_valid_interval_accepted():
    """FIXED task with valid start < end must not produce INVALID_FIXED_TIME."""
    tz = ZoneInfo("UTC")
    start = datetime(2026, 9, 20, 14, 0, tzinfo=tz)
    end = datetime(2026, 9, 20, 14, 45, tzinfo=tz)
    tasks = [TaskDraft(
        id="d1", title="Meeting", durationMin=45,
        schedulingType="FIXED",
        fixedStart=start,
        fixedEnd=end,
    )]
    draft = _draft(tasks=tasks)
    issues = check_today(draft)
    assert "INVALID_FIXED_TIME" not in issues


def test_cl_003_fixed_task_end_before_start_flagged():
    """FIXED task with fixedEnd <= fixedStart must be flagged."""
    tz = ZoneInfo("UTC")
    start = datetime(2026, 9, 20, 14, 0, tzinfo=tz)
    end = datetime(2026, 9, 20, 13, 0, tzinfo=tz)  # Before start
    tasks = [TaskDraft(
        id="d1", title="Meeting", durationMin=45,
        schedulingType="FIXED",
        fixedStart=start,
        fixedEnd=end,
    )]
    draft = _draft(tasks=tasks)
    issues = check_today(draft)
    assert "INVALID_FIXED_TIME" in issues


# ===========================================================================
# Assistant wording: draft only — no premature success language
# ===========================================================================
@pytest.mark.asyncio
async def test_draft_response_no_premature_success_wording():
    """When only a draft exists, assistant reply must not claim saved/scheduled."""
    from unittest.mock import AsyncMock, patch
    from datetime import datetime, timezone
    from uuid import uuid4
    from zoneinfo import ZoneInfo
    from app.ai.handlers import planner
    from app.ai.context import ChatContext
    from app.ai.budget import BudgetMode

    ctx = ChatContext(
        db=AsyncMock(),
        user_id=uuid4(),
        now=datetime(2026, 9, 20, 8, 0, tzinfo=ZoneInfo("UTC")),
        timezone=ZoneInfo("UTC"),
        break_minutes=5,
        default_windows=(("09:00", "17:00"),),
        default_date_offset=0,
    )

    with patch("app.ai.handlers.planner.get_budget_mode", new=AsyncMock(return_value=BudgetMode.NORMAL)):
        with patch("app.ai.handlers.planner.available_routes", new=AsyncMock(return_value="groq")):
            result = await planner.plan_day("Study 60 min", ctx, "en")

    reply_lower = result.reply.lower()
    forbidden = ["saved", "scheduled", "added to today", "successfully planned"]
    for word in forbidden:
        assert word not in reply_lower, f"Premature success wording found: '{word}' in '{result.reply}'"
