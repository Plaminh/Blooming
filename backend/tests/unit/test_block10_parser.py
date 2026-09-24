"""Cluster 10 — Parser priority, estimates, and confidence.

Test IDs: PS-011, PS-012, PS-013, PS-014, PS-016, PS-017, PS-018,
          PS-019, PS-020, PS-021
"""

from __future__ import annotations

import pytest
from datetime import date, datetime, timezone
from unittest.mock import AsyncMock, patch
from uuid import uuid4
from zoneinfo import ZoneInfo

from app.ai.parser import parse, ParsedPlan, ParsedTask
from app.ai.budget import BudgetMode


# ---------------------------------------------------------------------------
# PS-011 — Explicit mandatory language maps to CORE
# ---------------------------------------------------------------------------
def test_ps_011_mandatory_language_maps_to_core():
    """Must/phải maps task importance to CORE."""
    result = parse("Must finish the report for 60 min")
    assert len(result.tasks) == 1
    task = result.tasks[0]
    assert task.importance == "CORE"
    assert task.duration_min == 60
    assert task.source == "USER"


def test_ps_011_must_do_phải():
    """Vietnamese phải xong also maps to CORE (urgent keyword raises to HIGH priority)."""
    result = parse("phải xong báo cáo 45 phút")
    assert result.tasks[0].importance == "CORE"
    assert result.tasks[0].duration_min == 45


# ---------------------------------------------------------------------------
# PS-012 — Explicit optional language maps to OPTIONAL
# ---------------------------------------------------------------------------
def test_ps_012_optional_language_maps_to_optional():
    """'if there is time' / 'optional' maps to OPTIONAL importance."""
    result = parse("Read chapter 4 if there is time for 45 min")
    assert len(result.tasks) == 1
    task = result.tasks[0]
    assert task.importance == "OPTIONAL"
    assert task.priority == "LOW"
    assert task.duration_min == 45


def test_ps_012_vietnamese_optional():
    """'nếu còn thời gian' maps to OPTIONAL."""
    result = parse("đọc sách nếu còn thời gian 30p")
    assert result.tasks[0].importance == "OPTIONAL"


def test_ps_012_task_order_does_not_determine_importance():
    """Task position in the list must not determine importance; keywords determine it."""
    result = parse("Code 90 min and read if time 30 min")
    # First task: no optional keyword → CORE
    assert result.tasks[0].importance == "CORE"
    # Second task: 'if time' → OPTIONAL
    assert result.tasks[1].importance == "OPTIONAL"


# ---------------------------------------------------------------------------
# PS-013 — Known task without duration maps to RULE source
# ---------------------------------------------------------------------------
def test_ps_013_known_task_rule_source():
    """Known keyword task without explicit duration → source=RULE, estimate used."""
    result = parse("meeting")
    assert len(result.tasks) == 1
    task = result.tasks[0]
    assert task.source == "RULE"
    assert task.duration_min == 45  # meeting estimate


def test_ps_013_user_duration_not_rule():
    """Explicit duration → source=USER, not RULE."""
    result = parse("meeting for 60 min")
    assert result.tasks[0].source == "USER"
    assert result.tasks[0].duration_min == 60


def test_ps_013_unknown_task_unresolved():
    """Unknown task without duration → unresolved (duration=None in strict mode)."""
    result = parse("organize the attic")
    assert result.tasks[0].source == "RULE"  # still RULE (no user duration)
    assert result.tasks[0].duration_min is None  # unresolved
    assert 0 in result.unresolved


# ---------------------------------------------------------------------------
# PS-014 — Empty or no-task input returns clarification (low confidence)
# ---------------------------------------------------------------------------
def test_ps_014_empty_input_zero_confidence():
    """Empty input produces zero confidence and zero tasks."""
    result = parse("")
    assert result.confidence == 0.0
    assert len(result.tasks) == 0


def test_ps_014_whitespace_only_zero_confidence():
    result = parse("   ")
    assert result.confidence == 0.0
    assert len(result.tasks) == 0


def test_ps_014_pure_question_lowers_confidence():
    """A pure question without tasks has very low confidence."""
    # The parser flags '?' as a confidence penalty (-0.3)
    result = parse("What should I do today?")
    # May find tasks or not — but with question mark and no explicit tasks, confidence < 0.8
    # Unresolved tasks further reduce confidence by -0.15 each
    assert result.confidence < 0.8


# ---------------------------------------------------------------------------
# PS-016 — High-confidence (≥ 0.8) input routes to parser, zero LLM calls
# (Unit-level provider spy — no DB required)
# ---------------------------------------------------------------------------
@pytest.mark.asyncio
async def test_ps_016_high_confidence_zero_llm():
    """High-confidence fully-specified input must not call LLM provider."""
    from app.ai.handlers import planner
    from app.ai.context import ChatContext

    spy = AsyncMock(side_effect=AssertionError("LLM must not be called for high-confidence input"))

    ctx = ChatContext(
        db=AsyncMock(),
        user_id=uuid4(),
        now=datetime(2026, 9, 20, 8, 0, tzinfo=ZoneInfo("UTC")),
        timezone=ZoneInfo("UTC"),
        break_minutes=5,
        default_windows=(("09:00", "17:00"),),
        default_date_offset=0,
    )

    with patch.object(planner.llm_provider, "call", spy):
        with patch("app.ai.handlers.planner.get_budget_mode", new=AsyncMock(return_value=BudgetMode.NORMAL)):
            with patch("app.ai.handlers.planner.available_routes", new=AsyncMock(return_value="groq:llama")):
                # This message must produce confidence >= 0.8 and skip LLM
                response = await planner.plan_day(
                    "Read 45 min and code 60 min",
                    ctx,
                    "en",
                )

    spy.assert_not_called()
    assert response.draft is not None
    assert response.tier == "PARSER"


# ---------------------------------------------------------------------------
# PS-017 — Low-confidence input calls LLM route
# ---------------------------------------------------------------------------
@pytest.mark.asyncio
async def test_ps_017_low_confidence_calls_llm():
    """Low-confidence or unresolved input calls the configured LLM route."""
    from app.ai.handlers import planner
    from app.ai.context import ChatContext

    llm_spy = AsyncMock(return_value={
        "reply": "Here are your tasks",
        "windows": [["09:00", "17:00"]],
        "tasks": [{"title": "Organize tasks", "duration_min": 45, "importance": "CORE", "priority": "MEDIUM"}],
        "assumptions": [],
    })

    ctx = ChatContext(
        db=AsyncMock(),
        user_id=uuid4(),
        now=datetime(2026, 9, 20, 8, 0, tzinfo=ZoneInfo("UTC")),
        timezone=ZoneInfo("UTC"),
        break_minutes=5,
        default_windows=(("09:00", "17:00"),),
        default_date_offset=0,
    )

    with patch.object(planner.llm_provider, "call", llm_spy):
        with patch("app.ai.handlers.planner.get_budget_mode", new=AsyncMock(return_value=BudgetMode.NORMAL)):
            with patch("app.ai.handlers.planner.available_routes", new=AsyncMock(return_value="groq:llama")):
                # Low-confidence: unresolved tasks + question mark → confidence < 0.8
                response = await planner.plan_day(
                    "I'm not sure what to do today, maybe organize something?",
                    ctx,
                    "en",
                )

    llm_spy.assert_called_once()


# ---------------------------------------------------------------------------
# PS-018 — LLM enrichment must not delete parser-discovered tasks
# ---------------------------------------------------------------------------
def test_ps_018_llm_preserves_parser_tasks():
    from app.ai.handlers.planner import _parsed_from_llm, LLMDayPlan, LLMTask
    from app.ai.context import ChatContext
    from uuid import uuid4
    from datetime import datetime
    from zoneinfo import ZoneInfo
    from unittest.mock import AsyncMock

    ctx = ChatContext(
        db=AsyncMock(),
        user_id=uuid4(),
        now=datetime(2026, 9, 20, 8, 0, tzinfo=ZoneInfo("UTC")),
        timezone=ZoneInfo("UTC"),
        break_minutes=5,
        default_windows=(("09:00", "17:00"),),
        default_date_offset=0,
    )

    # Parser finds A and B ("Task A 30m" and "Task B"). LLM only returns A and invents C.
    llm_plan = LLMDayPlan(
        reply="Plan",
        tasks=[
            LLMTask(title="Task A", duration_min=30, importance="CORE"),
            LLMTask(title="Task C", duration_min=15, importance="OPTIONAL")
        ]
    )

    result = _parsed_from_llm(llm_plan, ctx, "Task A 30m\nTask B")

    # Output must have A, B, and C exactly once.
    titles = [t.title for t in result.tasks]
    assert len(titles) == 3
    assert titles == ["Task A", "Task B", "Task C"]  # Preserves parser order, then adds LLM inventions


    task_a = next(t for t in result.tasks if t.title == "Task A")
    assert task_a.source == "USER"
    assert task_a.duration_min == 30

    task_b = next(t for t in result.tasks if t.title == "Task B")
    # Parser had no duration for B -> RULE
    assert task_b.source == "RULE"

    task_c = next(t for t in result.tasks if t.title == "Task C")
    assert task_c.source == "AI"

# ---------------------------------------------------------------------------
# PS-019 — Deterministic repeat output (parser level)
# ---------------------------------------------------------------------------
def test_ps_019_deterministic_repeat_output():
    """Same input produces identical ParsedPlan on repeated calls."""
    msg = "Read chapter 4 for 45 min and email for 15 min and meeting at 14:00 for 30 min"
    r1 = parse(msg)
    r2 = parse(msg)
    assert r1 == r2
    assert r1.confidence == r2.confidence
    assert r1.tasks == r2.tasks


# ---------------------------------------------------------------------------
# PS-020 — High-confidence (≥ 0.8, no unresolved) skips LLM
# ---------------------------------------------------------------------------
@pytest.mark.asyncio
async def test_ps_020_high_confidence_skips_llm():
    """Confidence ≥ 0.8 with no unresolved tasks routes to PARSER tier."""
    from app.ai.handlers import planner
    from app.ai.context import ChatContext

    no_llm = AsyncMock(side_effect=AssertionError("LLM called on high-confidence input"))

    ctx = ChatContext(
        db=AsyncMock(),
        user_id=uuid4(),
        now=datetime(2026, 9, 20, 8, 0, tzinfo=ZoneInfo("UTC")),
        timezone=ZoneInfo("UTC"),
        break_minutes=5,
        default_windows=(("09:00", "17:00"),),
        default_date_offset=0,
    )

    with patch.object(planner.llm_provider, "call", no_llm):
        with patch("app.ai.handlers.planner.get_budget_mode", new=AsyncMock(return_value=BudgetMode.NORMAL)):
            with patch("app.ai.handlers.planner.available_routes", new=AsyncMock(return_value="groq")):
                result = await planner.plan_day(
                    "Study 60 min and exercise 30 min",
                    ctx,
                    "en",
                )

    no_llm.assert_not_called()
    assert result.tier == "PARSER"


# ---------------------------------------------------------------------------
# PS-021 — RULES_ONLY fallback: 45-minute default + assumption added
# ---------------------------------------------------------------------------
@pytest.mark.asyncio
async def test_ps_021_rules_only_45min_assumption():
    """RULES_ONLY mode: unresolved task gets 45 min default + assumption text."""
    from app.ai.handlers import planner
    from app.ai.context import ChatContext

    ctx = ChatContext(
        db=AsyncMock(),
        user_id=uuid4(),
        now=datetime(2026, 9, 20, 8, 0, tzinfo=ZoneInfo("UTC")),
        timezone=ZoneInfo("UTC"),
        break_minutes=5,
        default_windows=(("09:00", "17:00"),),
        default_date_offset=0,
    )

    # With RULES_ONLY mode the planner falls back to lenient=True parse
    with patch("app.ai.handlers.planner.get_budget_mode", new=AsyncMock(return_value=BudgetMode.RULES_ONLY)):
        with patch("app.ai.handlers.planner.available_routes", new=AsyncMock(return_value="")):
            result = await planner.plan_day(
                "organize the attic",  # Unknown task → unresolved in strict mode
                ctx,
                "en",
            )

    # Parser found the task (lenient=True), duration defaulted to 45
    assert result.draft is not None
    draft = result.draft
    assert len(draft.tasks) >= 1
    task = draft.tasks[0]
    assert task.durationMin == 45

    # An assumption must state the default
    assumption_texts = [a.text for a in result.assumptions]
    assert any("45" in t for t in assumption_texts), f"Expected 45-min assumption, got: {assumption_texts}"
