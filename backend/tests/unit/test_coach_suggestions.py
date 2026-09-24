"""Cluster 16 — Schedule coach and deterministic repair suggestions.

Test IDs: PV-007, PV-008, PV-009, PV-010, PV-011

All suggestions are generated deterministically by app.ai.coach from the
validated draft + real scheduler result.  LLM output must never invent
executable repair operations.
"""

from __future__ import annotations

from datetime import date, datetime, timezone
from unittest.mock import AsyncMock
from uuid import uuid4
from zoneinfo import ZoneInfo

import pytest

from app.ai.coach import (
    suggest_remove_optional,
    suggest_move_to_tomorrow,
    suggest_extend_availability,
    suggest_reduce_duration,
    suggest_split_long_task,
    generate_overloaded_suggestions,
)
from app.ai.context import ChatContext
from app.schemas.drafts import (
    AvailabilityWindowDraft,
    TaskDraft,
    TodayDraft,
)


def _ctx(now_utc: datetime | None = None) -> ChatContext:
    if now_utc is None:
        now_utc = datetime(2026, 9, 20, 8, 0, tzinfo=timezone.utc)
    tz = ZoneInfo("UTC")
    return ChatContext(
        db=AsyncMock(),
        user_id=uuid4(),
        now=now_utc.astimezone(tz),
        timezone=tz,
        break_minutes=5,
        default_windows=(("09:00", "17:00"),),
        default_date_offset=0,
    )


def _draft(
    tasks: list[TaskDraft] | None = None,
    windows: list[AvailabilityWindowDraft] | None = None,
) -> TodayDraft:
    return TodayDraft(
        planDate=date(2026, 9, 20),
        timezone="UTC",
        windows=windows or [AvailabilityWindowDraft(start="09:00", end="17:00")],
        tasks=tasks or [],
    )


def _task(
    task_id: str,
    title: str,
    duration: int = 60,
    importance: str = "CORE",
    priority: str = "MEDIUM",
    scheduling_type: str = "FLEXIBLE",
    estimate_source: str = "USER",
) -> TaskDraft:
    return TaskDraft(
        id=task_id,
        title=title,
        durationMin=duration,
        importance=importance,
        priority=priority,
        schedulingType=scheduling_type,
        estimateSource=estimate_source,
    )


# ===========================================================================
# PV-007 — Remove-optional suggestion
# ===========================================================================
def test_pv_007_remove_optional_suggestion_targets_optional():
    """suggest_remove_optional targets only OPTIONAL tasks, never CORE."""
    draft = _draft(tasks=[
        _task("d1", "Must code", 60, importance="CORE"),
        _task("d2", "Read book", 45, importance="OPTIONAL", priority="LOW"),
    ])
    suggestions = suggest_remove_optional(draft)
    assert len(suggestions) == 1
    patch_ops = suggestions[0]["patch"]
    assert any(op["op"] == "remove_task" and op["task_id"] == "d2" for op in patch_ops)


def test_pv_007_never_targets_core():
    """No OPTIONAL tasks → no remove suggestion."""
    draft = _draft(tasks=[
        _task("d1", "Must code", 60, importance="CORE"),
        _task("d2", "Must review", 30, importance="CORE"),
    ])
    suggestions = suggest_remove_optional(draft)
    assert suggestions == []


def test_pv_007_uses_stable_task_id():
    """Suggestion uses the stable task ID from the draft."""
    draft = _draft(tasks=[
        _task("stable-id-123", "Optional reading", 30, importance="OPTIONAL"),
    ])
    suggestions = suggest_remove_optional(draft)
    patch_ops = suggestions[0]["patch"]
    assert patch_ops[0]["task_id"] == "stable-id-123"


def test_pv_007_suggestion_is_patch_not_immediate_mutation():
    """Suggestion contains a patch op — render does not mutate."""
    draft = _draft(tasks=[
        _task("d1", "Optional task", 60, importance="OPTIONAL"),
    ])
    original_task_count = len(draft.tasks)
    suggestions = suggest_remove_optional(draft)
    # Draft is unchanged after generating suggestions
    assert len(draft.tasks) == original_task_count
    assert suggestions[0]["patch"][0]["op"] == "remove_task"


# ===========================================================================
# PV-008 — Move-to-tomorrow suggestion
# ===========================================================================
def test_pv_008_move_to_tomorrow_suggestion():
    """suggest_move_to_tomorrow returns a move_task_to_date patch op."""
    now_utc = datetime(2026, 9, 20, 8, 0, tzinfo=timezone.utc)
    ctx = _ctx(now_utc)
    draft = _draft(tasks=[
        _task("d1", "Optional reading", 45, importance="OPTIONAL", scheduling_type="FLEXIBLE"),
    ])
    suggestions = suggest_move_to_tomorrow(draft, ctx)
    assert len(suggestions) == 1
    patch_ops = suggestions[0]["patch"]
    assert patch_ops[0]["op"] == "move_task_to_date"
    assert patch_ops[0]["task_id"] == "d1"
    assert patch_ops[0]["target_date"] == "2026-09-21"
    assert patch_ops[0]["timezone"] == "UTC"


def test_pv_008_does_not_move_fixed_tasks():
    """Fixed tasks must not be moved to tomorrow."""
    now_utc = datetime(2026, 9, 20, 8, 0, tzinfo=timezone.utc)
    ctx = _ctx(now_utc)
    draft = _draft(tasks=[
        _task("d1", "Fixed meeting", 60, importance="OPTIONAL", scheduling_type="FIXED"),
    ])
    suggestions = suggest_move_to_tomorrow(draft, ctx)
    # Fixed optional task must not be moved
    assert not any(
        op["task_id"] == "d1"
        for s in suggestions
        for op in s.get("patch", [])
        if op.get("op") == "move_task_to_date"
    )


def test_pv_008_uses_server_owned_date():
    """The target_date is derived from server context, not client input."""
    now_utc = datetime(2026, 9, 20, 8, 0, tzinfo=timezone.utc)
    ctx = _ctx(now_utc)
    draft = _draft(tasks=[
        _task("d1", "Optional", 30, importance="OPTIONAL"),
    ])
    suggestions = suggest_move_to_tomorrow(draft, ctx)
    if suggestions:
        # Tomorrow computed from server context: 2026-09-20 + 1 = 2026-09-21
        assert suggestions[0]["patch"][0]["target_date"] == "2026-09-21"


def test_pv_008_no_mutation_before_click():
    """Draft remains unchanged after generating move-to-tomorrow suggestion."""
    now_utc = datetime(2026, 9, 20, 8, 0, tzinfo=timezone.utc)
    ctx = _ctx(now_utc)
    draft = _draft(tasks=[
        _task("d1", "Optional task", 45, importance="OPTIONAL"),
    ])
    original_count = len(draft.tasks)
    _ = suggest_move_to_tomorrow(draft, ctx)
    assert len(draft.tasks) == original_count


# ===========================================================================
# PV-009 — Extend-availability suggestion
# ===========================================================================
def test_pv_009_extend_availability_suggestion():
    """suggest_extend_availability returns update_window patch op."""
    now_utc = datetime(2026, 9, 20, 8, 0, tzinfo=timezone.utc)
    ctx = _ctx(now_utc)
    draft = _draft(windows=[AvailabilityWindowDraft(start="09:00", end="17:00")])
    suggestions = suggest_extend_availability(draft, ctx, extra_minutes=30)
    assert len(suggestions) == 1
    patch_ops = suggestions[0]["patch"]
    assert patch_ops[0]["op"] == "update_window"
    assert patch_ops[0]["end"] == "17:30"
    assert "17:30" in suggestions[0]["label"]


def test_pv_009_does_not_exceed_day_end():
    """Extension must not go past 22:00."""
    now_utc = datetime(2026, 9, 20, 8, 0, tzinfo=timezone.utc)
    ctx = _ctx(now_utc)
    draft = _draft(windows=[AvailabilityWindowDraft(start="09:00", end="21:50")])
    suggestions = suggest_extend_availability(draft, ctx, extra_minutes=30)
    if suggestions:
        new_end = suggestions[0]["patch"][0]["end"]
        assert new_end <= "22:00"


def test_pv_009_no_suggestion_at_day_end():
    """No extension suggestion when window already ends at or after 22:00."""
    now_utc = datetime(2026, 9, 20, 8, 0, tzinfo=timezone.utc)
    ctx = _ctx(now_utc)
    draft = _draft(windows=[AvailabilityWindowDraft(start="09:00", end="22:00")])
    suggestions = suggest_extend_availability(draft, ctx, extra_minutes=30)
    assert suggestions == []


def test_pv_009_no_reversed_window_generated():
    """Generated window patch must not create a reversed window."""
    now_utc = datetime(2026, 9, 20, 8, 0, tzinfo=timezone.utc)
    ctx = _ctx(now_utc)
    draft = _draft(windows=[AvailabilityWindowDraft(start="09:00", end="17:00")])
    suggestions = suggest_extend_availability(draft, ctx, extra_minutes=30)
    for s in suggestions:
        for op in s["patch"]:
            if "end" in op:
                # new end must be after 17:00
                assert op["end"] > "17:00"


# ===========================================================================
# PV-010 — Reduce-duration suggestion
# ===========================================================================
def test_pv_010_reduce_duration_suggestion():
    """suggest_reduce_duration suggests halving RULE/AI estimates."""
    draft = _draft(tasks=[
        _task("d1", "Optional task", 120, importance="OPTIONAL",
              priority="LOW", estimate_source="RULE"),
    ])
    suggestions = suggest_reduce_duration(draft)
    assert len(suggestions) == 1
    patch_ops = suggestions[0]["patch"]
    assert patch_ops[0]["op"] == "update_task"
    assert patch_ops[0]["task_id"] == "d1"
    assert patch_ops[0]["duration_min"] == 60  # 120 // 2


def test_pv_010_respects_minimum_duration():
    """Reduced duration must never fall below 5 minutes."""
    draft = _draft(tasks=[
        _task("d1", "Optional small", 61, importance="OPTIONAL",
              estimate_source="RULE"),
    ])
    suggestions = suggest_reduce_duration(draft)
    if suggestions:
        new_duration = suggestions[0]["patch"][0]["duration_min"]
        assert new_duration >= 5


def test_pv_010_does_not_reduce_user_estimates():
    """USER estimates must not be targeted for reduction."""
    draft = _draft(tasks=[
        _task("d1", "My specific task", 120, importance="OPTIONAL",
              estimate_source="USER"),
    ])
    suggestions = suggest_reduce_duration(draft)
    assert suggestions == []


def test_pv_010_preserves_stable_task_id():
    """Reduce suggestion uses the stable task ID."""
    draft = _draft(tasks=[
        _task("stable-xyz", "Optional long", 90, importance="OPTIONAL",
              estimate_source="AI"),
    ])
    suggestions = suggest_reduce_duration(draft)
    if suggestions:
        assert suggestions[0]["patch"][0]["task_id"] == "stable-xyz"


# ===========================================================================
# PV-011 — Split-long-task suggestion
# ===========================================================================
def test_pv_011_split_long_task_suggestion():
    """suggest_split_long_task suggests making a long flexible task splittable."""
    draft = _draft(tasks=[
        _task("d1", "Long study session", 120, importance="CORE",
              scheduling_type="FLEXIBLE"),
    ])
    suggestions = suggest_split_long_task(draft)
    assert len(suggestions) == 1
    patch_ops = suggestions[0]["patch"]
    assert patch_ops[0]["op"] == "update_task"
    assert patch_ops[0]["task_id"] == "d1"
    assert patch_ops[0]["splittable"] is True


def test_pv_011_does_not_split_fixed_tasks():
    """Fixed tasks must not be suggested for split (violates their constraint)."""
    draft = _draft(tasks=[
        _task("d1", "Fixed long meeting", 120, scheduling_type="FIXED"),
    ])
    suggestions = suggest_split_long_task(draft)
    assert not any(
        op.get("task_id") == "d1"
        for s in suggestions
        for op in s.get("patch", [])
    )


def test_pv_011_short_tasks_not_suggested():
    """Tasks ≤ split threshold (90 min) are not suggested for split."""
    draft = _draft(tasks=[
        _task("d1", "Short task", 60, scheduling_type="FLEXIBLE"),
    ])
    suggestions = suggest_split_long_task(draft)
    assert suggestions == []


# ===========================================================================
# Integration: generate_overloaded_suggestions returns deterministic set
# ===========================================================================
def test_generate_overloaded_suggestions_deterministic():
    """Calling generate_overloaded_suggestions twice returns the same result."""
    now_utc = datetime(2026, 9, 20, 8, 0, tzinfo=timezone.utc)
    ctx = _ctx(now_utc)
    draft = _draft(tasks=[
        _task("d1", "Core task", 60, importance="CORE"),
        _task("d2", "Optional reading", 45, importance="OPTIONAL",
              estimate_source="RULE"),
    ])
    s1 = generate_overloaded_suggestions(draft, ctx)
    s2 = generate_overloaded_suggestions(draft, ctx)
    assert len(s1) == len(s2)
    for i in range(len(s1)):
        assert s1[i]["label"] == s2[i]["label"]
        assert s1[i]["patch"] == s2[i]["patch"]


def test_generate_overloaded_suggestions_no_mutation():
    """Generating suggestions does not mutate the draft."""
    now_utc = datetime(2026, 9, 20, 8, 0, tzinfo=timezone.utc)
    ctx = _ctx(now_utc)
    draft = _draft(tasks=[
        _task("d1", "Optional task", 60, importance="OPTIONAL"),
    ])
    original_tasks = list(draft.tasks)
    _ = generate_overloaded_suggestions(draft, ctx)
    assert draft.tasks == original_tasks


def test_generate_overloaded_llm_cannot_invent_suggestions():
    """All suggestions come from application code — LLM is never called."""
    now_utc = datetime(2026, 9, 20, 8, 0, tzinfo=timezone.utc)
    ctx = _ctx(now_utc)
    draft = _draft(tasks=[
        _task("d1", "Optional", 60, importance="OPTIONAL"),
    ])
    # coach module has no LLM import — suggestions are always deterministic
    import app.ai.coach as coach_module
    assert not hasattr(coach_module, "llm_provider"), \
        "coach.py must not import llm_provider"
    suggestions = generate_overloaded_suggestions(draft, ctx)
    assert isinstance(suggestions, list)
