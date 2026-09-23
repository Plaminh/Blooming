import pytest
from unittest.mock import AsyncMock, create_autospec
from zoneinfo import ZoneInfo
from sqlalchemy.ext.asyncio import AsyncSession

@pytest.mark.asyncio
async def test_integration_zero_llm_calls_for_supported_input(monkeypatch):
    mock_session = create_autospec(AsyncSession, instance=True)

    # Mock LLM provider to ensure it's NEVER called
    mock_llm = AsyncMock()
    monkeypatch.setattr("app.ai.handlers.planner.llm_provider.call", mock_llm)

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
        timezone=ZoneInfo("UTC")
    )

    from app.schemas.today import TodayPreviewResponse
    mock_preview = AsyncMock(return_value=TodayPreviewResponse(
        plan_date=datetime.now().date(),
        timezone="UTC",
        preview_token="token",
        reality_check="OK",
        scheduled_tasks=[],
        unscheduled_tasks=[],
        available_minutes=100,
        required_minutes=0
    ))
    monkeypatch.setattr("app.ai.handlers.planner.today_service.preview_today_draft", mock_preview)

    from app.ai.handlers.planner import plan_day
    response = await plan_day(
        "Today: read chapter 3 for 45 min; review flashcards for 30 min",
        context,
        "en",
    )

    assert response.tier == "PARSER"
    body = response.model_dump(mode="json")
    draft = body["draft"]
    assert draft is not None
    assert len(draft["tasks"]) == 2
    assert draft["tasks"][0]["title"] == "read chapter 3"
    assert draft["tasks"][0]["durationMin"] == 45
    assert draft["tasks"][1]["title"] == "review flashcards"
    assert draft["tasks"][1]["durationMin"] == 30

    mock_llm.assert_not_called()
    mock_session.add.assert_not_called()
    mock_session.add_all.assert_not_called()
    mock_session.flush.assert_not_awaited()
    mock_session.commit.assert_not_awaited()
