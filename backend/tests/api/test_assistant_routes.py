from datetime import date, datetime, timedelta, timezone
from unittest.mock import AsyncMock

import pytest
from app.ai.providers import LLMError, llm_provider
from app.core.config import settings
from app.db.models.goals import Goal, Milestone
from app.db.models.planning import PlanningSession
from app.db.models.tasks import Task
from app.db.models.users import UserSettings
from app.services.reminders_service import reminders_service
from httpx import AsyncClient
from sqlalchemy import func, select
from uuid import UUID


@pytest.mark.asyncio
async def test_authenticated_chat_degrades_when_quota_is_unavailable(
    async_client: AsyncClient,
    auth_headers: dict[str, str],
    monkeypatch,
):
    provider_call = AsyncMock(side_effect=LLMError("rate_limit", 429))
    monkeypatch.setattr(llm_provider, "call", provider_call)
    response = await async_client.post(
        "/api/v1/assistant/chat",
        headers=auth_headers,
        json={"message": "Plan my day"},
    )
    assert response.status_code == 200
    assert response.json()["degraded"] == "RULES_ONLY"
    assert response.json()["draft"] is None
    provider_call.assert_awaited_once()


@pytest.mark.asyncio
async def test_rules_only_budget_never_calls_provider(
    async_client: AsyncClient, auth_headers: dict[str, str], monkeypatch,
):
    monkeypatch.setattr(settings, "AI_TOKEN_BUDGET_24H",
        {model: 0 for model in settings.AI_TOKEN_BUDGET_24H})
    provider_call = AsyncMock()
    monkeypatch.setattr(llm_provider, "call", provider_call)
    response = await async_client.post("/api/v1/assistant/chat", headers=auth_headers,
        json={"message": "Plan my day"})
    assert response.status_code == 200, response.text
    assert response.json()["degraded"] == "RULES_ONLY"
    provider_call.assert_not_awaited()


@pytest.mark.asyncio
async def test_chat_requires_authentication(async_client: AsyncClient, monkeypatch):
    provider_call = AsyncMock()
    monkeypatch.setattr(llm_provider, "call", provider_call)
    response = await async_client.post(
        "/api/v1/assistant/chat", json={"message": "Hello"}
    )
    assert response.status_code in {401, 403}
    provider_call.assert_not_awaited()


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "message,intent,fragment",
    [
        ("Hello", "GREETING", "plan"),
        ("Today what tasks?", "STATUS_TODAY", "no plan"),
        ("Water balance", "STATUS_GARDEN", "Water"),
        ("Statistics", "STATUS_STATS", "7 days"),
        ("My current goal", "STATUS_GOALS", "no open goals"),
        ("What is Pomodoro?", "HELP_FEATURE", "Pomodoro"),
    ],
)
async def test_rules_use_authenticated_services_without_model_calls(
    async_client: AsyncClient,
    auth_headers: dict[str, str],
    monkeypatch,
    message: str,
    intent: str,
    fragment: str,
):
    provider_call = AsyncMock()
    monkeypatch.setattr(llm_provider, "call", provider_call)
    response = await async_client.post(
        "/api/v1/assistant/chat",
        headers=auth_headers,
        json={"message": message},
    )
    assert response.status_code == 200, response.text
    assert response.json()["intent"] == intent
    assert fragment.lower() in response.json()["reply"].lower()
    assert response.json()["suggestions"]
    provider_call.assert_not_awaited()


@pytest.mark.asyncio
async def test_crisis_takes_precedence_over_planning(
    async_client: AsyncClient,
    auth_headers: dict[str, str],
    monkeypatch,
):
    provider_call = AsyncMock()
    monkeypatch.setattr(llm_provider, "call", provider_call)
    response = await async_client.post(
        "/api/v1/assistant/chat",
        headers=auth_headers,
        json={"message": "I might hurt myself; plan my day"},
    )
    assert response.status_code == 200
    assert response.json()["intent"] == "CRISIS"
    assert response.json()["suggestions"] == []
    provider_call.assert_not_awaited()


@pytest.mark.asyncio
async def test_explicit_day_plan_uses_real_preview_with_zero_model_calls(
    async_client: AsyncClient,
    auth_headers: dict[str, str],
    monkeypatch,
):
    provider_call = AsyncMock()
    monkeypatch.setattr(llm_provider, "call", provider_call)
    response = await async_client.post(
        "/api/v1/assistant/chat",
        headers=auth_headers,
        json={"message": "Plan my day: study 60 min, write report 30 min"},
    )
    assert response.status_code == 200, response.text
    data = response.json()
    assert data["tier"] == "PARSER"
    assert data["draft"]["tasks"][0]["title"] == "study"
    assert data["preview"]["preview_token"]
    assert any(block["block_type"] == "TASK" for block in data["preview"]["blocks"])
    assert any(block["block_type"] == "BREAK" for block in data["preview"]["blocks"])
    provider_call.assert_not_awaited()


@pytest.mark.asyncio
async def test_overloaded_parser_plan_uses_scheduler_reality_check(
    async_client: AsyncClient,
    auth_headers: dict[str, str],
    monkeypatch,
):
    provider_call = AsyncMock()
    monkeypatch.setattr(llm_provider, "call", provider_call)
    response = await async_client.post(
        "/api/v1/assistant/chat",
        headers=auth_headers,
        json={"message": "Lập lịch rảnh từ 9h đến 10h, học 60p và viết báo cáo 60p"},
    )
    assert response.status_code == 200, response.text
    data = response.json()
    assert data["preview"]["reality_check"] == "OVERLOADED"
    assert data["preview"]["unscheduled_tasks"]
    assert "Không đủ thời gian" in data["reply"]
    provider_call.assert_not_awaited()


@pytest.mark.asyncio
async def test_session_reload_is_owned_and_contains_persisted_messages(
    async_client: AsyncClient,
    auth_headers: dict[str, str],
    auth_headers_two: dict[str, str],
):
    sent = await async_client.post(
        "/api/v1/assistant/chat", headers=auth_headers, json={"message": "Hello"}
    )
    session_id = sent.json()["session_id"]
    loaded = await async_client.get(
        f"/api/v1/assistant/sessions/{session_id}", headers=auth_headers
    )
    assert loaded.status_code == 200
    assert [item["role"] for item in loaded.json()["messages"]] == ["user", "assistant"]
    denied = await async_client.get(
        f"/api/v1/assistant/sessions/{session_id}", headers=auth_headers_two
    )
    assert denied.status_code == 404

    latest = await async_client.get(
        "/api/v1/assistant/sessions/latest", headers=auth_headers
    )
    assert latest.status_code == 200
    assert latest.json()["session_id"] == session_id


@pytest.mark.asyncio
async def test_idle_session_is_closed_and_new_session_is_started(
    async_client: AsyncClient, auth_headers: dict[str, str], db_session, monkeypatch,
):
    first = await async_client.post("/api/v1/assistant/chat", headers=auth_headers,
                                    json={"message": "Hello"})
    old_id = UUID(first.json()["session_id"])
    from app.api.routes import assistant as assistant_routes
    class FutureDatetime(datetime):
        @classmethod
        def now(cls, tz=None):
            future = datetime.now(timezone.utc) + timedelta(hours=13)
            return future.astimezone(tz) if tz else future.replace(tzinfo=None)
    monkeypatch.setattr(assistant_routes, "datetime", FutureDatetime)
    second = await async_client.post("/api/v1/assistant/chat", headers=auth_headers,
        json={"message": "Hello", "session_id": str(old_id)})
    assert second.status_code == 200
    assert second.json()["session_id"] != str(old_id)
    await db_session.refresh(await db_session.get(PlanningSession, old_id))
    assert (await db_session.get(PlanningSession, old_id)).status == "CANCELLED"


@pytest.mark.asyncio
async def test_pending_goal_intent_uses_persisted_history(
    async_client: AsyncClient, auth_headers: dict[str, str], db_session,
):
    first = await async_client.post("/api/v1/assistant/chat", headers=auth_headers,
        json={"message": "Create a goal to learn guitar"})
    assert first.json()["question"]
    session_id = UUID(first.json()["session_id"])
    state = await db_session.get(PlanningSession, session_id)
    await db_session.refresh(state)
    assert state.session_type == "ROADMAP"
    assert state.pending_intent == "CREATE_GOAL"
    second = await async_client.post("/api/v1/assistant/chat", headers=auth_headers,
        json={"message": "2030-01-01", "session_id": str(session_id)})
    assert second.status_code == 200, second.text
    assert second.json()["draft"]["goalTitle"].lower().find("guitar") >= 0
    await db_session.refresh(state)
    assert state.pending_intent is None


@pytest.mark.asyncio
async def test_tired_user_without_plan_gets_light_draft_from_pending_work(
    async_client: AsyncClient, auth_headers: dict[str, str], test_user, db_session,
):
    db_session.add(Task(user_id=test_user.id, title="Prepare report",
        estimated_duration_minutes=90, category="Work", source="AI", status="PENDING"))
    await db_session.commit()
    response = await async_client.post("/api/v1/assistant/chat", headers=auth_headers,
        json={"message": "I'm tired"})
    assert response.status_code == 200, response.text
    body = response.json()
    assert body["intent"] == "MOOD"
    assert body["draft"]["tasks"][0]["importance"] == "OPTIONAL"
    assert body["draft"]["tasks"][0]["durationMin"] <= 25
    assert all(item.get("action") != "SKIP_OPTIONAL_TODAY" for item in body["suggestions"])


@pytest.mark.asyncio
async def test_chat_contract_accepts_current_draft_and_returns_fresh_preview(
    async_client: AsyncClient,
    auth_headers: dict[str, str],
):
    draft = {
        "type": "today",
        "planDate": date.today().isoformat(),
        "timezone": "UTC",
        "windows": [{"start": "09:00", "end": "17:00"}],
        "tasks": [{"id": "d1", "title": "Read", "durationMin": 30}],
    }
    response = await async_client.post(
        "/api/v1/assistant/chat",
        headers=auth_headers,
        json={"message": "change task 1 to 45 min", "current_draft": draft},
    )
    assert response.status_code == 200, response.text
    body = response.json()
    assert body["intent"] == "EDIT_DRAFT"
    assert body["tier"] == "RULES"
    assert body["draft"]["tasks"][0]["durationMin"] == 45
    assert body["preview"]["preview_token"]


@pytest.mark.asyncio
async def test_successful_today_save_completes_planning_session(
    async_client: AsyncClient,
    auth_headers: dict[str, str],
):
    chat_response = await async_client.post(
        "/api/v1/assistant/chat",
        headers=auth_headers,
        json={"message": "Plan my day: study 60 min"},
    )
    body = chat_response.json()
    saved = await async_client.post(
        "/api/v1/today/save",
        headers=auth_headers,
        json={
            "session_id": body["session_id"],
            "preview_token": body["preview"]["preview_token"],
            "draft": body["draft"],
        },
    )
    assert saved.status_code == 200, saved.text
    session = await async_client.get(
        f"/api/v1/assistant/sessions/{body['session_id']}", headers=auth_headers
    )
    assert session.json()["status"] == "COMPLETED"


@pytest.mark.asyncio
async def test_atomic_roadmap_rolls_back_when_reminder_creation_fails(
    async_client: AsyncClient,
    auth_headers: dict[str, str],
    db_session,
    monkeypatch,
):
    monkeypatch.setattr(
        reminders_service,
        "sync_milestone_reminder",
        AsyncMock(side_effect=RuntimeError("fail")),
    )
    response = await async_client.post(
        "/api/v1/goals/from-roadmap",
        headers=auth_headers,
        json={
            "draft": {
                "type": "roadmap",
                "goalTitle": "Learn",
                "goalDescription": "",
                "targetDate": "2026-12-31",
                "milestones": [
                    {"id": "m1", "title": "Start", "targetDate": "2026-11-01"}
                ],
            }
        },
    )
    assert response.status_code == 500
    await db_session.rollback()
    assert await db_session.scalar(select(func.count(Goal.id))) == 0


@pytest.mark.asyncio
async def test_roadmap_milestone_due_at_is_local_end_of_day(
    async_client: AsyncClient,
    auth_headers: dict[str, str],
    test_user: dict,
    db_session,
):
    user_settings = await db_session.scalar(
        select(UserSettings).where(UserSettings.user_id == test_user.id)
    )
    if user_settings is None:
        user_settings = UserSettings(
            user_id=test_user.id,
            timezone="Asia/Ho_Chi_Minh",
        )
        db_session.add(user_settings)
    user_settings.timezone = "Asia/Ho_Chi_Minh"
    await db_session.commit()
    target = date.today() + timedelta(days=10)
    response = await async_client.post(
        "/api/v1/goals/from-roadmap",
        headers=auth_headers,
        json={
            "draft": {
                "type": "roadmap",
                "goalTitle": "Learn",
                "goalDescription": "",
                "targetDate": target.isoformat(),
                "milestones": [
                    {
                        "id": "m1",
                        "title": "Finish",
                        "targetDate": target.isoformat(),
                    }
                ],
            }
        },
    )
    assert response.status_code == 201, response.text
    milestone = await db_session.scalar(select(Milestone))
    assert milestone.due_at.hour == 16
    assert milestone.due_at.minute == 59
    assert milestone.due_at.date() == target
