from datetime import datetime, timezone
from unittest.mock import AsyncMock
from uuid import uuid4
from zoneinfo import ZoneInfo

import pytest
from app.ai.llm.budget import BudgetMode
from app.ai.context import ChatContext
from app.ai.handlers import planner


def context():
    return ChatContext(
        db=AsyncMock(),
        user_id=uuid4(),
        now=datetime(2026, 9, 20, 9, tzinfo=timezone.utc),
        timezone=ZoneInfo("UTC"),
        break_minutes=5,
        default_windows=(("09:00", "17:00"),),
        default_date_offset=0,
    )


@pytest.mark.asyncio
async def test_invalid_draft_gets_exactly_one_repair(monkeypatch):
    call = AsyncMock(
        side_effect=[
            {"reply": "text survives", "tasks": [{"title": "A", "duration_min": 0}]},
            {"reply": "fixed", "tasks": [{"title": "A", "duration_min": 30}]},
        ]
    )
    monkeypatch.setattr(planner.llm_provider, "call", call)
    result = await planner._llm_plan("ambiguous", context(), BudgetMode.NORMAL)
    assert result and result[0].tasks[0].duration_min == 30
    assert result[1] == "text survives"
    assert call.await_count == 2


@pytest.mark.asyncio
async def test_lean_mode_never_repairs(monkeypatch):
    call = AsyncMock(
        return_value={
            "reply": "keep this",
            "tasks": [{"title": "A", "duration_min": 0}],
        }
    )
    monkeypatch.setattr(planner.llm_provider, "call", call)
    result = await planner._llm_plan("ambiguous", context(), BudgetMode.LEAN)
    assert result and result[0].tasks == () and result[1] == "keep this"
    assert call.await_count == 1


def test_llm_cannot_choose_plan_date_or_duration_provenance():
    value = planner.LLMDayPlan.model_validate(
        {
            "reply": "draft",
            "plan_date": "2099-01-01",
            "tasks": [
                {"title": "study", "duration_min": 60},
                {"title": "write report", "duration_min": 45},
            ],
        }
    )
    parsed = planner._parsed_from_llm(
        value,
        context(),
        "Plan my day: study 60 min and write report",
    )
    assert parsed.plan_date_offset == context().default_date_offset
    assert parsed.tasks[0].source == "USER"
    assert parsed.tasks[1].source == "AI"
