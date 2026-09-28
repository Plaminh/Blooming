import pytest
from unittest.mock import AsyncMock, create_autospec
from zoneinfo import ZoneInfo
from sqlalchemy.ext.asyncio import AsyncSession


@pytest.mark.asyncio
async def test_integration_llm_first_for_supported_input(monkeypatch):
    mock_session = create_autospec(AsyncSession, instance=True)

    # Mock LLM provider to return valid extracted tasks matching input
    mock_llm = AsyncMock(
        return_value={
            "reply": "Here is your plan.",
            "tasks": [
                {
                    "title": "read chapter 3",
                    "duration_min": 45,
                    "importance": "CORE",
                    "priority": "MEDIUM",
                },
                {
                    "title": "review flashcards",
                    "duration_min": 30,
                    "importance": "CORE",
                    "priority": "MEDIUM",
                },
            ],
            "windows": [],
            "assumptions": [],
        }
    )
    monkeypatch.setattr("app.ai.handlers.planner.llm_provider.call", mock_llm)
    from app.ai.llm.budget import BudgetMode

    monkeypatch.setattr(
        "app.ai.handlers.planner.get_budget_mode",
        AsyncMock(return_value=BudgetMode.NORMAL),
    )
    monkeypatch.setattr(
        "app.ai.handlers.planner.available_routes", AsyncMock(return_value="groq:llama")
    )
    monkeypatch.setattr(
        "app.ai.handlers.planner.carried_tasks", AsyncMock(return_value=[])
    )

    from app.ai.context import ChatContext
    from datetime import datetime

    context = ChatContext(
        db=mock_session,
        user_id="00000000-0000-0000-0000-000000000000",
        now=datetime.now(),
        default_date_offset=0,
        calibration={},
        break_minutes=5,
        default_windows=(("08:00", "22:00"),),
        timezone=ZoneInfo("UTC"),
    )

    from app.ai.handlers.planner import plan_day

    response = await plan_day(
        "Today: read chapter 3 for 45 min; review flashcards for 30 min",
        context,
        "en",
    )

    assert response.tier == "LLM"
    assert response.preview is None
    body = response.model_dump(mode="json")
    draft = body["draft"]
    assert draft is not None
    assert len(draft["tasks"]) == 2
    assert draft["tasks"][0]["title"] == "read chapter 3"
    assert draft["tasks"][0]["durationMin"] == 45
    assert draft["tasks"][1]["title"] == "review flashcards"
    assert draft["tasks"][1]["durationMin"] == 30

    mock_llm.assert_awaited_once()
    mock_session.add.assert_not_called()
    mock_session.add_all.assert_not_called()
    mock_session.flush.assert_not_awaited()
