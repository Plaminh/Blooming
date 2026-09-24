from datetime import date, datetime, timezone
from unittest.mock import AsyncMock
from uuid import uuid4
from zoneinfo import ZoneInfo

import pytest

from app.ai.budget import BudgetMode
from app.ai.context import ChatContext
from app.ai.handlers import editor
from app.schemas.drafts import TaskDraft, TodayDraft
from app.schemas.today import TodayPreviewResponse


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
async def test_deterministic_editor_returns_fresh_preview_without_llm(monkeypatch):
    provider = AsyncMock()
    monkeypatch.setattr(editor.llm_provider, "call", provider)
    monkeypatch.setattr(
        editor, "get_budget_mode", AsyncMock(return_value=BudgetMode.LEAN)
    )
    monkeypatch.setattr(
        editor.today_service,
        "preview_today_draft",
        AsyncMock(
            return_value=TodayPreviewResponse(
                plan_date=date.today(),
                timezone="UTC",
                preview_token="token",
            )
        ),
    )
    draft = TodayDraft(
        planDate=date.today(),
        windows=[{"start": "09:00", "end": "17:00"}],
        tasks=[TaskDraft(id="d1", title="Read", durationMin=30)],
    )
    result = await editor.edit("change task 1 to 45 min", draft, _context())
    assert result.draft.tasks[0].durationMin == 45
    assert result.preview is not None
    assert result.preview.preview_token == "token"
    assert result.degraded == "LEAN"
    provider.assert_not_awaited()


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
