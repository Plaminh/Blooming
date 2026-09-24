"""Cluster 12 — TodayDraft assembly and assumptions.

Test IDs: TD-001 through TD-007

All tests call the real assemble_today() production function.
"""

from __future__ import annotations

from datetime import date, datetime, timezone
from unittest.mock import AsyncMock
from uuid import uuid4
from zoneinfo import ZoneInfo

import pytest

from app.ai.context import ChatContext
from app.ai.drafts import assemble_today
from app.ai.parser import ParsedPlan, ParsedTask


def _ctx(
    now_utc: datetime | None = None,
    tz_name: str = "UTC",
    calibration: dict | None = None,
    break_minutes: int = 5,
) -> ChatContext:
    if now_utc is None:
        now_utc = datetime(2026, 9, 20, 8, 0, tzinfo=timezone.utc)
    tz = ZoneInfo(tz_name)
    local = now_utc.astimezone(tz)
    return ChatContext(
        db=AsyncMock(),
        user_id=uuid4(),
        now=local,
        timezone=tz,
        break_minutes=break_minutes,
        default_windows=(("09:00", "17:00"),),
        default_date_offset=0,
        calibration=calibration or {},
    )


def _task(
    title: str = "Task",
    duration: int | None = 60,
    source: str = "USER",
    importance: str = "CORE",
    priority: str = "MEDIUM",
    category: str | None = None,
    fixed_start: str | None = None,
    fixed_end: str | None = None,
) -> ParsedTask:
    return ParsedTask(
        title=title,
        duration_min=duration,
        source=source,
        importance=importance,
        priority=priority,
        category=category,
        fixed_start=fixed_start,
        fixed_end=fixed_end,
    )


# ---------------------------------------------------------------------------
# TD-001 — IDs are deterministic d1, d2, ...
# ---------------------------------------------------------------------------
def test_td_001_deterministic_ids():
    """Draft task IDs must be d1, d2, ... in task order."""
    ctx = _ctx()
    plan = ParsedPlan(
        tasks=(_task("Study", 60), _task("Exercise", 30)),
        windows=(("09:00", "17:00"),),
    )
    draft, _ = assemble_today(plan, ctx)
    assert draft.tasks[0].id == "d1"
    assert draft.tasks[1].id == "d2"


def test_td_001_ids_stable_on_repeat():
    """IDs must be the same on repeated identical calls."""
    ctx = _ctx()
    plan = ParsedPlan(tasks=(_task("Study", 60),), windows=(("09:00", "17:00"),))
    draft1, _ = assemble_today(plan, ctx)
    draft2, _ = assemble_today(plan, ctx)
    assert draft1.tasks[0].id == draft2.tasks[0].id == "d1"


# ---------------------------------------------------------------------------
# TD-002 — Task order is stable (preserves parser order)
# ---------------------------------------------------------------------------
def test_td_002_task_order_stable():
    """Assembly preserves the original parser task order."""
    ctx = _ctx()
    plan = ParsedPlan(
        tasks=(_task("Alpha", 30), _task("Beta", 60), _task("Gamma", 45)),
        windows=(("09:00", "17:00"),),
    )
    draft, _ = assemble_today(plan, ctx)
    assert [t.title for t in draft.tasks] == ["Alpha", "Beta", "Gamma"]


# ---------------------------------------------------------------------------
# TD-003 — Importance and scheduler priority remain distinct
# ---------------------------------------------------------------------------
def test_td_003_importance_priority_distinct():
    """importance (CORE/OPTIONAL) and priority (HIGH/MEDIUM/LOW) are independent fields."""
    ctx = _ctx()
    plan = ParsedPlan(
        tasks=(
            _task("Must do A", 60, importance="CORE", priority="LOW"),
            _task("Optional B", 30, importance="OPTIONAL", priority="HIGH"),
        ),
        windows=(("09:00", "17:00"),),
    )
    draft, _ = assemble_today(plan, ctx)
    task_a = draft.tasks[0]
    task_b = draft.tasks[1]

    assert task_a.importance == "CORE"
    assert task_a.priority == "LOW"  # Importance≠priority
    assert task_b.importance == "OPTIONAL"
    assert task_b.priority == "HIGH"  # Optional but HIGH priority allowed


# ---------------------------------------------------------------------------
# TD-004 — OPTIONAL tasks receive lower scheduling priority ONLY per product rule
# ---------------------------------------------------------------------------
def test_td_004_optional_lower_priority_only_per_rule():
    """OPTIONAL importance results in LOW priority when parser signals optional."""
    ctx = _ctx()
    plan = ParsedPlan(
        tasks=(_task("Read", 45, importance="OPTIONAL", priority="LOW"),),
        windows=(("09:00", "17:00"),),
    )
    draft, _ = assemble_today(plan, ctx)
    task = draft.tasks[0]
    assert task.importance == "OPTIONAL"
    assert task.priority == "LOW"
    # Explicit USER duration is not reduced for OPTIONAL tasks
    assert task.durationMin == 45


def test_td_004_optional_user_duration_not_reduced():
    """An OPTIONAL task with USER duration keeps that exact duration."""
    ctx = _ctx()
    plan = ParsedPlan(
        tasks=(_task("Long optional", 480, source="USER", importance="OPTIONAL"),),
        windows=(("09:00", "17:00"),),
    )
    draft, _ = assemble_today(plan, ctx)
    # USER duration must be preserved even for OPTIONAL
    assert draft.tasks[0].durationMin == 480


# ---------------------------------------------------------------------------
# TD-005 — USER duration is never calibrated or overwritten
# ---------------------------------------------------------------------------
def test_td_005_user_duration_not_calibrated():
    """USER source duration must pass through unchanged regardless of calibration."""
    # Provide a calibration that would inflate study tasks
    calibration = {"Learning": 1.5}
    ctx = _ctx(calibration=calibration)
    plan = ParsedPlan(
        tasks=(_task("Study", 60, source="USER", category="Learning"),),
        windows=(("09:00", "17:00"),),
    )
    draft, _ = assemble_today(plan, ctx)
    # USER duration: must NOT be multiplied by 1.5
    assert draft.tasks[0].durationMin == 60
    assert draft.tasks[0].estimateSource == "USER"


def test_td_005_rule_duration_calibrated():
    """RULE source duration IS calibrated when category matches."""
    calibration = {"Learning": 1.5}
    ctx = _ctx(calibration=calibration)
    plan = ParsedPlan(
        tasks=(_task("Study", 60, source="RULE", category="Learning"),),
        windows=(("09:00", "17:00"),),
    )
    draft, _ = assemble_today(plan, ctx)
    # RULE duration: multiplied by calibration (capped at 480)
    assert draft.tasks[0].durationMin == 90  # 60 * 1.5
    assert draft.tasks[0].estimateSource == "HISTORY"


# ---------------------------------------------------------------------------
# TD-006 — RULE and AI estimates produce user-readable assumptions
# ---------------------------------------------------------------------------
def test_td_006_rule_estimate_produces_assumption():
    """RULE source tasks produce an assumption about the estimated duration."""
    ctx = _ctx()
    plan = ParsedPlan(
        tasks=(_task("meeting", 45, source="RULE"),),
        windows=(("09:00", "17:00"),),
    )
    draft, assumptions = assemble_today(plan, ctx)
    assumption_texts = [a.text for a in assumptions]
    # Must contain an assumption about the estimate
    assert any("meeting" in t.lower() or "45" in t for t in assumption_texts)


def test_td_006_ai_estimate_produces_assumption():
    """AI source tasks also produce an assumption."""
    ctx = _ctx()
    plan = ParsedPlan(
        tasks=(_task("Project planning", 90, source="AI"),),
        windows=(("09:00", "17:00"),),
    )
    _, assumptions = assemble_today(plan, ctx)
    assumption_texts = [a.text for a in assumptions]
    assert any("90" in t or "project" in t.lower() for t in assumption_texts)


def test_td_006_user_estimate_no_duration_assumption():
    """USER source tasks do NOT produce a duration estimate assumption."""
    ctx = _ctx()
    plan = ParsedPlan(
        tasks=(_task("Report", 60, source="USER"),),
        windows=(("09:00", "17:00"),),
    )
    _, assumptions = assemble_today(plan, ctx)
    # No DURATION assumption for USER source
    duration_assumptions = [a for a in assumptions if a.kind == "DURATION"]
    assert len(duration_assumptions) == 0


# ---------------------------------------------------------------------------
# TD-007 — Equivalent assumptions are deduplicated
# ---------------------------------------------------------------------------
def test_td_007_default_window_assumption_appears_once():
    """The default-window assumption must appear at most once even with multiple tasks."""
    ctx = _ctx()
    plan = ParsedPlan(
        tasks=(
            _task("A", 30, source="RULE"),
            _task("B", 45, source="RULE"),
        ),
        windows=(),  # No explicit windows → default used
    )
    _, assumptions = assemble_today(plan, ctx)
    window_assumptions = [a for a in assumptions if a.kind == "WINDOW"]
    assert len(window_assumptions) == 1  # Deduplicated


def test_td_007_no_duplicate_window_assumption():
    """When explicit windows are provided, no window assumption is added."""
    ctx = _ctx()
    plan = ParsedPlan(
        tasks=(_task("Study", 60, source="USER"),),
        windows=(("10:00", "15:00"),),
    )
    _, assumptions = assemble_today(plan, ctx)
    window_assumptions = [a for a in assumptions if a.kind == "WINDOW"]
    assert len(window_assumptions) == 0


# ---------------------------------------------------------------------------
# Additional: Assumptions must not expose internal IDs or debug text
# ---------------------------------------------------------------------------
def test_td_assumptions_are_user_readable():
    """Assumption texts must be human-readable (no UUIDs, no Python repr)."""
    ctx = _ctx()
    plan = ParsedPlan(
        tasks=(_task("Study", 60, source="RULE"),),
        windows=(),
    )
    _, assumptions = assemble_today(plan, ctx)
    import re
    uuid_pattern = re.compile(r"[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}", re.I)
    for assumption in assumptions:
        assert not uuid_pattern.search(assumption.text), f"UUID in assumption: {assumption.text}"
        assert "object at 0x" not in assumption.text  # No Python repr
