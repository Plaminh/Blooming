import pytest
from httpx import AsyncClient
from unittest.mock import AsyncMock
from datetime import datetime, timezone
from app.db.models.users import User, UserSettings
from app.ai.providers import llm_provider
from app.ai.parser import ParsedPlan

@pytest.mark.asyncio
async def test_ct_003_canonical_today_draft(async_client: AsyncClient, test_user: User, auth_headers: dict[str, str], db_session, monkeypatch, clock):
    provider_call = AsyncMock()
    
    # We will inject malicious task ID and duration to prove they are overwritten/recalculated.
    # By providing a window in the future (12:00-14:00 when clock is at 09:00), assemble_today will use offset 0.
    raw_output = {
        "reply": "Here is your plan.",
        "tasks": [{"id": "malicious-id", "title": "Buy groceries", "duration_min": 30, "priority": "MEDIUM", "importance": "CORE"}],
        "windows": [["12:00", "14:00"]],
        "assumptions": []
    }
    provider_call.return_value = raw_output
    monkeypatch.setattr(llm_provider, "call", provider_call)
    monkeypatch.setattr("app.ai.handlers.planner.parse", lambda _message: ParsedPlan())
    monkeypatch.setattr("app.services.assistant_service.datetime", clock)
    
    settings = await db_session.scalar(
        __import__("sqlalchemy").select(UserSettings).where(UserSettings.user_id == test_user.id)
    )
    expected_tz = settings.timezone if settings else "UTC"
    import zoneinfo
    tz = zoneinfo.ZoneInfo(expected_tz)
    
    # clock fixture sets datetime.now(tz) to 2026-01-01 09:00:00 UTC
    mock_now = datetime(2026, 1, 1, 9, 0, 0, tzinfo=timezone.utc)
    local_now = mock_now.astimezone(tz)
    
    # With a future window, planning rule offset is 0, so planDate is today
    expected_plan_date = local_now.strftime("%Y-%m-%d")
    
    response = await async_client.post(
        "/api/v1/assistant/chat",
        headers=auth_headers,
        json={"message": "Plan my day. Buy groceries."}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["reply"] == "Here is your plan."
    draft = data.get("draft")
    assert draft is not None
    assert draft["type"] == "today"
    
    # Exact timezone verification
    assert draft["timezone"] == expected_tz
    
    # Exact Date verification
    assert draft["planDate"] == expected_plan_date
    
    # Task ID must not be the malicious ID
    assert draft["tasks"][0]["id"] != "malicious-id"
    
    preview = data.get("preview")
    assert preview is None

@pytest.mark.asyncio
async def test_ct_004_canonical_roadmap_draft(async_client: AsyncClient, auth_headers: dict[str, str], monkeypatch):
    provider_call = AsyncMock()
    monkeypatch.setattr(llm_provider, "call", provider_call)
    
    response = await async_client.post(
        "/api/v1/assistant/chat",
        headers=auth_headers,
        json={"message": "create a goal by 2026-12-31"}
    )
    assert response.status_code == 200
    data = response.json()
    draft = data.get("draft")
    assert draft is not None
    assert draft["type"] == "roadmap"
    assert draft["targetDate"] == "2026-12-31"
    
    # Assert Today fields did not leak
    assert "tasks" not in draft
    assert "windows" not in draft
    assert "planDate" not in draft
    assert "timezone" not in draft
    
    # Assert provider was never invoked (pure rules-engine)
    provider_call.assert_not_awaited()

@pytest.mark.asyncio
async def test_ctx_011_preserve_reply_when_draft_invalid(async_client: AsyncClient, auth_headers: dict[str, str], monkeypatch):
    provider_call = AsyncMock()
    
    # Provably invalid: duration_min=1 violates LLMTask constraint ge=5
    raw_output = {
        "reply": "I tried my best.",
        "tasks": [{"title": "Invalid task", "duration_min": 1}],
        "windows": [],
        "assumptions": []
    }
    provider_call.return_value = raw_output
    monkeypatch.setattr(llm_provider, "call", provider_call)
    monkeypatch.setattr("app.ai.handlers.planner.parse", lambda _message: ParsedPlan())
    
    response = await async_client.post(
        "/api/v1/assistant/chat",
        headers=auth_headers,
        json={"message": "Plan my day with an invalid task."}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["reply"] == "I tried my best."
    assert data.get("draft") is None
