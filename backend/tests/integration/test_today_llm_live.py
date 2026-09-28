"""Live integration tests for real LLM semantic extraction.

These tests verify that the real configured LLM provider (e.g. Groq, Gemini)
actually understands natural-language paraphrases and outputs valid structured
planning schemas, without relying on mock data or parser regex.

Opt-in only: skipped by default unless RUN_LIVE_LLM_TESTS=1 is set in the environment.
"""

from __future__ import annotations

import os
import pytest
from datetime import datetime

pytestmark = [pytest.mark.external, pytest.mark.live_llm]
from uuid import uuid4
from zoneinfo import ZoneInfo
from sqlalchemy.ext.asyncio import AsyncSession
from unittest.mock import AsyncMock, create_autospec

from app.ai.context import ChatContext
from app.ai.budget import BudgetMode
from app.ai.handlers import planner
from app.ai.validators import check_today


@pytest.mark.skipif(
    os.environ.get("RUN_LIVE_LLM_TESTS") != "1",
    reason="Live LLM tests are opt-in to avoid paid provider calls in standard CI. Set RUN_LIVE_LLM_TESTS=1 to run.",
)
@pytest.mark.parametrize(
    "phrase,window,tasks",
    [
        (
            "Today I need to study algorithms for 1 hour, write the report for 45 minutes, "
            "and optionally read a book for 30 minutes. I am available from 1 PM to 5 PM.",
            ("13:00", "17:00"),
            [("algorithm", 60, "CORE"), ("report", 45, "CORE"), ("book", 30, "OPTIONAL")],
        ),
        (
            "My afternoon is open between 2 PM and 6 PM. Practice data structures for 90 minutes, "
            "finish my assignment for an hour, and if time allows read documentation for 20 minutes.",
            ("14:00", "18:00"),
            [("data structure", 90, "CORE"), ("assignment", 60, "CORE"), ("documentation", 20, "OPTIONAL")],
        ),
        (
            "I'm free 9 AM through noon today. Spend 50 minutes on database exercises and maybe "
            "review my notes for half an hour.",
            ("09:00", "12:00"),
            [("database", 50, "CORE"), ("notes", 30, "OPTIONAL")],
        ),
    ],
)
@pytest.mark.asyncio
async def test_live_today_semantic_pipeline(monkeypatch, phrase, window, tasks):
    """Real provider semantics survive the complete planner-to-draft pipeline."""
    mock_db = create_autospec(AsyncSession, instance=True)
    mock_db.commit = AsyncMock()
    monkeypatch.setattr(planner, "get_budget_mode", AsyncMock(return_value=BudgetMode.NORMAL))
    monkeypatch.setattr(planner, "available_routes", AsyncMock(return_value=planner.settings.AI_ROUTE_PLANNER_LITE))
    monkeypatch.setattr(planner, "carried_tasks", AsyncMock(return_value=[]))
    ctx = ChatContext(
        db=mock_db,
        user_id=uuid4(),
        now=datetime(2026, 9, 25, 9, 0, tzinfo=ZoneInfo("Asia/Ho_Chi_Minh")),
        timezone=ZoneInfo("Asia/Ho_Chi_Minh"),
        break_minutes=5,
        default_windows=(("08:00", "18:00"),),
        default_date_offset=0,
    )

    response = await planner.plan_day(phrase, ctx, "en")
    await planner.llm_provider.close_client()

    assert response.tier == "LLM"
    assert response.degraded is None
    assert response.preview is None
    assert response.draft is not None
    assert [(item.start, item.end) for item in response.draft.windows] == [window]
    assert response.assumptions == []
    assert len(response.draft.tasks) == len(tasks)
    for task, (title_fragment, duration, importance) in zip(response.draft.tasks, tasks, strict=True):
        assert title_fragment in task.title.lower()
        assert task.durationMin == duration
        assert task.importance == importance
        assert task.fixedStart is None
        assert task.fixedEnd is None
    assert check_today(response.draft) == []


@pytest.mark.skipif(
    os.environ.get("RUN_LIVE_LLM_TESTS") != "1",
    reason="Live LLM tests are opt-in to avoid paid provider calls in standard CI. Set RUN_LIVE_LLM_TESTS=1 to run.",
)
@pytest.mark.asyncio
async def test_live_llm_unseen_phrase_1():
    """Unseen phrase 1: Afternoon availability with core report task and optional docs reading."""
    mock_db = create_autospec(AsyncSession, instance=True)
    mock_db.commit = AsyncMock()

    ctx = ChatContext(
        db=mock_db,
        user_id=uuid4(),
        now=datetime(2026, 9, 25, 9, 0, tzinfo=ZoneInfo("Asia/Ho_Chi_Minh")),
        timezone=ZoneInfo("Asia/Ho_Chi_Minh"),
        break_minutes=5,
        default_windows=(("08:00", "18:00"),),
        default_date_offset=0,
    )

    phrase = (
        "I've got the afternoon free until six. Spend about an hour polishing my report and, "
        "if I get the chance, twenty minutes reading docs."
    )
    response = await planner.plan_day(phrase, ctx, "en")

    assert response.tier == "LLM"
    assert response.draft is not None
    assert response.preview is None
    assert len(response.draft.tasks) >= 2

    # Check semantic understanding of tasks
    titles_lower = [t.title.lower() for t in response.draft.tasks]
    assert any("report" in t for t in titles_lower)
    assert any("doc" in t for t in titles_lower)

    # Report should be ~60 min CORE, docs should be ~20 min OPTIONAL
    report_task = next(t for t in response.draft.tasks if "report" in t.title.lower())
    docs_task = next(t for t in response.draft.tasks if "doc" in t.title.lower())

    assert 45 <= report_task.durationMin <= 75
    assert 15 <= docs_task.durationMin <= 30
    assert docs_task.importance == "OPTIONAL"

    # Invariant: check_today passes
    assert check_today(response.draft) == []


@pytest.mark.skipif(
    os.environ.get("RUN_LIVE_LLM_TESTS") != "1",
    reason="Live LLM tests are opt-in to avoid paid provider calls in standard CI. Set RUN_LIVE_LLM_TESTS=1 to run.",
)
@pytest.mark.asyncio
async def test_live_llm_unseen_phrase_2():
    """Unseen phrase 2: Afternoon window with database exercises and notes review."""
    mock_db = create_autospec(AsyncSession, instance=True)
    mock_db.commit = AsyncMock()

    ctx = ChatContext(
        db=mock_db,
        user_id=uuid4(),
        now=datetime(2026, 9, 25, 9, 0, tzinfo=ZoneInfo("Asia/Ho_Chi_Minh")),
        timezone=ZoneInfo("Asia/Ho_Chi_Minh"),
        break_minutes=5,
        default_windows=(("08:00", "18:00"),),
        default_date_offset=0,
    )

    phrase = (
        "Between two and five I want to work on database exercises for roughly 50 minutes, "
        "then maybe review my notes for half an hour."
    )
    response = await planner.plan_day(phrase, ctx, "en")

    assert response.tier == "LLM"
    assert response.draft is not None
    assert response.preview is None
    assert len(response.draft.tasks) >= 2

    titles_lower = [t.title.lower() for t in response.draft.tasks]
    assert any("database" in t or "exercise" in t or "sql" in t for t in titles_lower)
    assert any("note" in t or "review" in t for t in titles_lower)

    db_task = next(t for t in response.draft.tasks if "database" in t.title.lower() or "exercise" in t.title.lower())
    notes_task = next(t for t in response.draft.tasks if "note" in t.title.lower() or "review" in t.title.lower())

    assert 40 <= db_task.durationMin <= 60
    assert 25 <= notes_task.durationMin <= 40

    assert check_today(response.draft) == []


@pytest.mark.skipif(
    os.environ.get("RUN_LIVE_LLM_TESTS") != "1",
    reason="Live LLM tests are opt-in to avoid paid provider calls in standard CI. Set RUN_LIVE_LLM_TESTS=1 to run.",
)
@pytest.mark.asyncio
async def test_live_llm_unseen_phrase_3():
    """Unseen phrase 3: Tomorrow morning algorithm and email tasks with 9-12 availability."""
    mock_db = create_autospec(AsyncSession, instance=True)
    mock_db.commit = AsyncMock()

    ctx = ChatContext(
        db=mock_db,
        user_id=uuid4(),
        now=datetime(2026, 9, 25, 9, 0, tzinfo=ZoneInfo("Asia/Ho_Chi_Minh")),
        timezone=ZoneInfo("Asia/Ho_Chi_Minh"),
        break_minutes=5,
        default_windows=(("08:00", "18:00"),),
        default_date_offset=0,
    )

    phrase = (
        "Tomorrow morning I need 90 minutes for algorithms and 30 minutes for email. "
        "I'm available nine to noon."
    )
    response = await planner.plan_day(phrase, ctx, "en")

    assert response.tier == "LLM"
    assert response.draft is not None
    assert response.preview is None
    assert str(response.draft.planDate) == "2026-09-26"
    assert len(response.draft.tasks) >= 2

    titles_lower = [t.title.lower() for t in response.draft.tasks]
    assert any("algorithm" in t for t in titles_lower)
    assert any("email" in t for t in titles_lower)

    algo_task = next(t for t in response.draft.tasks if "algorithm" in t.title.lower())
    email_task = next(t for t in response.draft.tasks if "email" in t.title.lower())

    assert 80 <= algo_task.durationMin <= 100
    assert 20 <= email_task.durationMin <= 40

    # Availability window 9 to 12
    if response.draft.windows:
        assert any(w.start >= "09:00" and w.end <= "13:00" for w in response.draft.windows)

    assert check_today(response.draft) == []
