from datetime import date, datetime, timezone
from unittest.mock import AsyncMock
from uuid import uuid4
from zoneinfo import ZoneInfo

import pytest

from app.ai.budget import BudgetMode
from app.ai.context import ChatContext
from app.ai.handlers import editor
from app.schemas.drafts import TaskDraft, TodayDraft


def _context():
    return ChatContext(
        db=AsyncMock(),
        user_id=uuid4(),
        now=datetime.now(timezone.utc),
        timezone=ZoneInfo("UTC"),
        break_minutes=5,
        default_windows=(("09:00", "17:00"),),
        default_date_offset=0,
    )


@pytest.mark.asyncio
async def test_deterministic_editor_returns_updated_draft_without_auto_preview(monkeypatch):
    provider = AsyncMock()
    monkeypatch.setattr(editor.llm_provider, "call", provider)
    monkeypatch.setattr(
        editor, "get_budget_mode", AsyncMock(return_value=BudgetMode.LEAN)
    )
    draft = TodayDraft(
        planDate=date.today(),
        windows=[{"start": "09:00", "end": "17:00"}],
        tasks=[TaskDraft(id="d1", title="Read", durationMin=30)],
    )
    result = await editor.edit("change task 1 to 45 min", draft, _context())
    assert result.draft.tasks[0].durationMin == 45
    assert result.preview is None
    assert result.degraded == "LEAN"
    provider.assert_not_awaited()


@pytest.mark.asyncio
async def test_edit_03_unique_article_near_match_updates_only_target(monkeypatch):
    monkeypatch.setattr(editor, "get_budget_mode", AsyncMock(return_value=BudgetMode.LEAN))
    draft = TodayDraft(
        planDate=date.today(), windows=[{"start": "09:00", "end": "17:00"}],
        tasks=[
            TaskDraft(id="d1", title="Study Algorithms", durationMin=45),
            TaskDraft(id="d2", title="Read Book", durationMin=30, importance="CORE"),
        ],
    )

    result = await editor.edit(
        "Change Read a book to 20 minutes and mark it optional.", draft, _context()
    )

    assert result.question is None
    assert result.preview is None
    assert [(task.id, task.title, task.durationMin, task.importance) for task in result.draft.tasks] == [
        ("d1", "Study Algorithms", 45, "CORE"),
        ("d2", "Read Book", 20, "OPTIONAL"),
    ]


@pytest.mark.asyncio
async def test_lean_editor_does_not_use_llm_for_ambiguous_edit(monkeypatch):
    provider = AsyncMock()
    monkeypatch.setattr(editor.llm_provider, "call", provider)
    monkeypatch.setattr(
        editor, "get_budget_mode", AsyncMock(return_value=BudgetMode.LEAN)
    )
    draft = TodayDraft(
        planDate=date.today(),
        windows=[{"start": "09:00", "end": "17:00"}],
        tasks=[TaskDraft(id="d1", title="Read", durationMin=30)],
    )
    result = await editor.edit("make it better", draft, _context())
    assert result.question
    assert result.degraded == "LEAN"
    provider.assert_not_awaited()
