import pytest
from httpx import AsyncClient
from unittest.mock import AsyncMock
from app.ai.providers import llm_provider
from app.db.models.users import User
from app.db.models.tasks import Task
from app.db.models.daily_plans import DailyPlan
from sqlalchemy import select
from app.ai.parser import parse
from datetime import datetime

# Helper to spy on LLM calls and fail if called
@pytest.fixture
def no_llm_spy(monkeypatch):
    spy = AsyncMock(side_effect=Exception("LLM provider was called! Zero LLM calls allowed."))
    monkeypatch.setattr(llm_provider, "call", spy)
    return spy


@pytest.mark.asyncio
async def test_ps_019_parser_determinism():
    """Test parser determinism directly at the parser boundary."""
    msg = "Today I need to read chapter 3 for 45 minutes and review flashcards for 30 minutes."
    res1 = parse(msg)
    res2 = parse(msg)
    assert res1 == res2
    assert res1.confidence > 0.7


@pytest.mark.asyncio
async def test_ps_003_valid_simple_request_accepted(async_client: AsyncClient, auth_headers: dict[str, str], no_llm_spy):
    """PS-003: A valid simple request is accepted without LLM."""
    chat_payload = {"message": "Today I need to read chapter 3 for 45 minutes and review flashcards for 30 minutes."}
    res = await async_client.post("/api/v1/assistant/chat", headers=auth_headers, json=chat_payload)
    assert res.status_code == 200
    data = res.json()
    assert data["intent"] == "PLAN_DAY"
    assert data["tier"] == "PARSER"
    no_llm_spy.assert_not_called()


@pytest.mark.asyncio
async def test_td_001_deterministic_parser_produces_correct_draft(async_client: AsyncClient, auth_headers: dict[str, str], no_llm_spy):
    """TD-001: The deterministic parser produces the correct TodayDraft."""
    chat_payload = {"message": "Today I need to read chapter 3 for 45 minutes and review flashcards for 30 minutes."}
    res = await async_client.post("/api/v1/assistant/chat", headers=auth_headers, json=chat_payload)
    draft = res.json().get("draft")
    
    assert draft is not None
    assert draft["type"] == "today"
    assert len(draft["tasks"]) == 2
    assert draft["tasks"][0]["durationMin"] == 45
    assert draft["tasks"][1]["durationMin"] == 30


@pytest.mark.asyncio
async def test_td_019_draft_does_not_persist(async_client: AsyncClient, auth_headers: dict[str, str], db_session, test_user: User, no_llm_spy):
    """TD-019: Creating a draft does not create plan/task database records."""
    chat_payload = {"message": "Today I need to read chapter 3 for 45 minutes and review flashcards for 30 minutes."}
    await async_client.post("/api/v1/assistant/chat", headers=auth_headers, json=chat_payload)
    
    tasks = (await db_session.scalars(select(Task).where(Task.user_id == test_user.id))).all()
    plans = (await db_session.scalars(select(DailyPlan).where(DailyPlan.user_id == test_user.id))).all()
    
    assert len(tasks) == 0
    assert len(plans) == 0


@pytest.mark.asyncio
async def test_pv_001_preview_returns_scheduler_blocks_no_persistence(async_client: AsyncClient, auth_headers: dict[str, str], db_session, test_user: User, no_llm_spy):
    """PV-001: Preview returns scheduler-derived time blocks and does not persist."""
    from unittest.mock import patch
    from app.core.scheduler import DeterministicScheduler
    from app.db.models.daily_plans import DailyPlan
    
    # Obtain draft first
    res = await async_client.post("/api/v1/assistant/chat", headers=auth_headers, json={"message": "Today I need to read chapter 3 for 45 minutes and review flashcards for 30 minutes."})
    draft = res.json()["draft"]
    
    original_schedule = DeterministicScheduler.schedule
    
    with patch.object(DeterministicScheduler, "schedule", side_effect=original_schedule, autospec=True) as mock_schedule:
        # Generate explicit preview
        preview_res = await async_client.post("/api/v1/today/preview", headers=auth_headers, json={"draft": draft})
        assert preview_res.status_code == 200
        preview = preview_res.json()
        
        assert mock_schedule.call_count == 1
        called_tasks = mock_schedule.call_args[0][1] if len(mock_schedule.call_args[0]) > 1 else mock_schedule.call_args.kwargs.get("tasks")
        assert len(called_tasks) == 2
        assert called_tasks[0].estimated_duration_minutes == 45
        assert called_tasks[1].estimated_duration_minutes == 30
    
    blocks = preview["blocks"]
    assert len(blocks) == 4
    assert blocks[0]["block_type"] == "TASK"
    assert blocks[0]["estimated_duration_minutes"] == 45
    assert blocks[1]["block_type"] == "BREAK"
    
    start = datetime.fromisoformat(blocks[0]["planned_start_at"])
    end = datetime.fromisoformat(blocks[0]["planned_end_at"])
    diff_minutes = (end - start).total_seconds() / 60
    assert diff_minutes == 45
    
    # Prove no DB persistence
    tasks = (await db_session.scalars(select(Task).where(Task.user_id == test_user.id))).all()
    assert len(tasks) == 0
    plans = (await db_session.scalars(select(DailyPlan).where(DailyPlan.user_id == test_user.id))).all()
    assert len(plans) == 0


@pytest.mark.asyncio
async def test_sv_001_save_creates_real_plan_and_tasks(async_client: AsyncClient, auth_headers: dict[str, str], db_session, test_user: User, no_llm_spy):
    """SV-001: Save creates a real plan and its tasks matching preview exactly."""
    res = await async_client.post("/api/v1/assistant/chat", headers=auth_headers, json={"message": "Today I need to read chapter 3 for 45 minutes and review flashcards for 30 minutes."})
    data = res.json()
    
    user_id = test_user.id
    
    save_payload = {
        "draft": data["draft"],
        "preview_token": data["preview"]["preview_token"],
        "session_id": data["session_id"]
    }
    
    save_res = await async_client.post("/api/v1/today/save", headers=auth_headers, json=save_payload)
    assert save_res.status_code == 200
    
    db_session.expunge_all()
    tasks = (await db_session.scalars(select(Task).where(Task.user_id == user_id).order_by(Task.created_at))).all()
    plans = (await db_session.scalars(select(DailyPlan).where(DailyPlan.user_id == user_id))).all()
    
    assert len(plans) == 1
    assert len(tasks) == 2
    
    assert plans[0].user_id == user_id
    assert tasks[0].title == "Today I need to read chapter 3 for"
    assert tasks[0].estimated_duration_minutes == 45
    assert tasks[1].title == "review flashcards for"
    assert tasks[1].estimated_duration_minutes == 30


@pytest.mark.asyncio
async def test_sv_010_repeated_save_idempotency(async_client: AsyncClient, auth_headers: dict[str, str], db_session, test_user: User, no_llm_spy):
    """SV-010: Repeated Save submissions must return exactly 409 and not create duplicates."""
    res = await async_client.post("/api/v1/assistant/chat", headers=auth_headers, json={"message": "Today I need to read chapter 3 for 45 minutes and review flashcards for 30 minutes."})
    data = res.json()
    user_id = test_user.id
    
    save_payload = {
        "draft": data["draft"],
        "preview_token": data["preview"]["preview_token"],
        "session_id": data["session_id"]
    }
    
    # First save
    save_res1 = await async_client.post("/api/v1/today/save", headers=auth_headers, json=save_payload)
    assert save_res1.status_code == 200
    
    # Second save (exact duplicate)
    save_res2 = await async_client.post("/api/v1/today/save", headers=auth_headers, json=save_payload)
    assert save_res2.status_code == 409  # Explicitly expect 409 as per existing contract
    
    db_session.expunge_all()
    tasks = (await db_session.scalars(select(Task).where(Task.user_id == user_id))).all()
    plans = (await db_session.scalars(select(DailyPlan).where(DailyPlan.user_id == user_id))).all()
    
    assert len(plans) == 1
    assert len(tasks) == 2


@pytest.mark.asyncio
async def test_reload_verification(async_client: AsyncClient, auth_headers: dict[str, str], db_session, test_user: User, no_llm_spy):
    """Assert GET Today returns the exact expected tasks."""
    res = await async_client.post("/api/v1/assistant/chat", headers=auth_headers, json={"message": "Today I need to read chapter 3 for 45 minutes and review flashcards for 30 minutes."})
    data = res.json()
    save_payload = {
        "draft": data["draft"],
        "preview_token": data["preview"]["preview_token"],
        "session_id": data["session_id"]
    }
    await async_client.post("/api/v1/today/save", headers=auth_headers, json=save_payload)
    
    today_res = await async_client.get("/api/v1/today", headers=auth_headers)
    assert today_res.status_code == 200
    today_data = today_res.json()
    
    blocks = today_data["blocks"]
    task_blocks = [b for b in blocks if b["block_type"] == "TASK"]
    assert len(task_blocks) == 2
    assert task_blocks[0]["title"] == "Today I need to read chapter 3 for"
    assert task_blocks[0]["estimated_duration_minutes"] == 45
    assert task_blocks[1]["title"] == "review flashcards for"
    assert task_blocks[1]["estimated_duration_minutes"] == 30
    
    assert today_data["plan_date"] == data["draft"]["planDate"]
    assert today_data["status"] == "ACTIVE"
    
    assert task_blocks[0]["planned_start_at"] < task_blocks[0]["planned_end_at"]
    assert task_blocks[0]["planned_end_at"] <= task_blocks[1]["planned_start_at"]
    assert task_blocks[1]["planned_start_at"] < task_blocks[1]["planned_end_at"]
