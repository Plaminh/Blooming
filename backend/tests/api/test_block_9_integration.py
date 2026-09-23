import pytest
from unittest.mock import AsyncMock, create_autospec
from zoneinfo import ZoneInfo
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime

@pytest.fixture
def base_context_factory(monkeypatch):
    def factory(now=None, tz_name="UTC"):
        mock_session = create_autospec(AsyncSession, instance=True)
        # Mock LLM provider to ensure it's NEVER called
        mock_llm = AsyncMock()
        monkeypatch.setattr("app.ai.handlers.planner.llm_provider.call", mock_llm)

        from app.ai.context import ChatContext
        context = ChatContext(
            db=mock_session,
            user_id="00000000-0000-0000-0000-000000000000",
            now=now or datetime(2026, 9, 23, 16, 0, tzinfo=ZoneInfo(tz_name)),
            default_date_offset=0,
            calibration={},
            break_minutes=5,
            default_windows=(("08:00", "22:00"),),
            timezone=ZoneInfo(tz_name)
        )

        from app.schemas.today import TodayPreviewResponse
        mock_preview = AsyncMock(return_value=TodayPreviewResponse(
            plan_date=context.now.date(),
            timezone=tz_name,
            preview_token="token",
            reality_check="OK",
            scheduled_tasks=[],
            unscheduled_tasks=[],
            available_minutes=100,
            required_minutes=0
        ))
        monkeypatch.setattr("app.ai.handlers.planner.today_service.preview_today_draft", mock_preview)
        
        return context, mock_session, mock_llm
    return factory

def assert_no_persistence(mock_session):
    mock_session.add.assert_not_called()
    mock_session.add_all.assert_not_called()
    mock_session.flush.assert_not_awaited()
    mock_session.commit.assert_not_awaited()

@pytest.mark.asyncio
async def test_block_9_fixed_interval_integration(base_context_factory):
    context, mock_session, mock_llm = base_context_factory()
    
    from app.ai.handlers.planner import plan_day
    response = await plan_day("Practice SQL from 14:00 to 15:30", context, "en")
    
    assert response.tier == "PARSER"
    mock_llm.assert_not_called()
    assert_no_persistence(mock_session)
    
    draft = response.model_dump(mode="json")["draft"]
    assert len(draft["tasks"]) == 1
    task = draft["tasks"][0]
    assert task["title"] == "Practice SQL"
    assert task["durationMin"] == 90
    assert task["fixedStart"] is not None
    assert task["fixedEnd"] is not None
    assert "T14:00:00" in task["fixedStart"]
    assert "T15:30:00" in task["fixedEnd"]

@pytest.mark.asyncio
async def test_block_9_explicit_availability_integration(base_context_factory):
    context, mock_session, mock_llm = base_context_factory()
    
    from app.ai.handlers.planner import plan_day
    response = await plan_day("I am available from 18:00 to 21:00; study algorithms for 60 min", context, "en")
    
    assert response.tier == "PARSER"
    mock_llm.assert_not_called()
    assert_no_persistence(mock_session)
    
    draft = response.model_dump(mode="json")["draft"]
    assert len(draft["tasks"]) == 1
    task = draft["tasks"][0]
    assert task["title"] == "study algorithms"
    assert task["durationMin"] == 60
    assert draft["windows"] == [{"start": "18:00", "end": "21:00"}]

@pytest.mark.asyncio
async def test_block_9_time_budget_integration(base_context_factory):
    context, mock_session, mock_llm = base_context_factory()
    
    from app.ai.handlers.planner import plan_day
    response = await plan_day("I only have 2 hours available today", context, "en")
    
    assert response.tier == "PARSER"
    mock_llm.assert_not_called()
    assert_no_persistence(mock_session)
    
    draft = response.model_dump(mode="json")["draft"]
    assert len(draft["tasks"]) == 0
    # Expected in assumptions since schema has no dedicated budget field
    assert any("Normalized budget: 120 minutes" in a.text for a in response.assumptions)

@pytest.mark.asyncio
async def test_block_9_tomorrow_offset_integration(base_context_factory):
    # Test month boundary and non-UTC timezone
    context, mock_session, mock_llm = base_context_factory(
        now=datetime(2026, 9, 30, 22, 0, tzinfo=ZoneInfo("Asia/Ho_Chi_Minh")),
        tz_name="Asia/Ho_Chi_Minh"
    )
    
    from app.ai.handlers.planner import plan_day
    response = await plan_day("Tomorrow, study algorithms for 60 min", context, "en")
    
    assert response.tier == "PARSER"
    mock_llm.assert_not_called()
    assert_no_persistence(mock_session)
    
    draft = response.model_dump(mode="json")["draft"]
    assert draft["planDate"] == "2026-10-01"
    assert len(draft["tasks"]) == 1
    assert draft["tasks"][0]["title"] == "study algorithms"

@pytest.mark.asyncio
async def test_block_9_invalid_interval_integration(base_context_factory):
    context, mock_session, mock_llm = base_context_factory()
    
    from app.ai.handlers.planner import plan_day
    # End before start
    response = await plan_day("Practice SQL from 15:30 to 14:00 for 90m", context, "en")
    
    assert response.tier == "PARSER"
    assert_no_persistence(mock_session)
    # Clarification returned
    assert response.question is not None
    assert response.preview is None
    
    draft = response.model_dump(mode="json")["draft"]
    task = draft["tasks"][0]
    assert task["title"] == "Practice SQL"
    assert task["durationMin"] == 90
    assert task["fixedStart"] is not None
    assert task["fixedEnd"] is not None
    assert "T15:30:00" in task["fixedStart"]
    assert "T14:00:00" in task["fixedEnd"]
