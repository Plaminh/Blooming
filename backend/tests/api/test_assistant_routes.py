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
    assert response.json()["degraded"] in ("RULES_ONLY", "LLM_FAILED")
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
    assert response.json()["degraded"] in ("RULES_ONLY", "LLM_FAILED")
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
async def test_explicit_day_plan_uses_llm(
    async_client: AsyncClient,
    auth_headers: dict[str, str],
    monkeypatch,
):
    provider_call = AsyncMock(return_value={
        "reply": "Here is your plan.",
        "tasks": [
            {"title": "study", "duration_min": 60, "priority": "MEDIUM", "importance": "CORE"},
            {"title": "write report", "duration_min": 30, "priority": "MEDIUM", "importance": "CORE"}
        ],
        "windows": [],
        "assumptions": []
    })
    monkeypatch.setattr(llm_provider, "call", provider_call)
    response = await async_client.post(
        "/api/v1/assistant/chat",
        headers=auth_headers,
        json={"message": "Plan my day: study 60 min, write report 30 min"},
    )
    assert response.status_code == 200, response.text
    data = response.json()
    assert data["tier"] == "LLM"
    assert data["draft"]["tasks"][0]["title"] == "study"
    
    preview_response = await async_client.post(
        "/api/v1/today/preview",
        headers=auth_headers,
        json={"draft": data["draft"]}
    )
    preview_data = preview_response.json()
    assert preview_data["preview_token"]
    assert any(block["block_type"] == "TASK" for block in preview_data["blocks"])
    assert any(block["block_type"] == "BREAK" for block in preview_data["blocks"])
    provider_call.assert_awaited_once()


@pytest.mark.asyncio
async def test_overloaded_plan_uses_llm_and_scheduler(
    async_client: AsyncClient,
    auth_headers: dict[str, str],
    monkeypatch,
):
    provider_call = AsyncMock(return_value={
        "reply": "Here is your plan.",
        "tasks": [
            {"title": "học", "duration_min": 60, "priority": "MEDIUM", "importance": "CORE"},
            {"title": "viết báo cáo", "duration_min": 60, "priority": "MEDIUM", "importance": "CORE"}
        ],
        "windows": [["09:00", "10:00"]],
        "assumptions": []
    })
    monkeypatch.setattr(llm_provider, "call", provider_call)
    response = await async_client.post(
        "/api/v1/assistant/chat",
        headers=auth_headers,
        json={"message": "Lập lịch rảnh từ 9h đến 10h, học 60p và viết báo cáo 60p"},
    )
    assert response.status_code == 200, response.text
    data = response.json()
    assert data["tier"] == "LLM"
    
    preview_response = await async_client.post(
        "/api/v1/today/preview",
        headers=auth_headers,
        json={"draft": data["draft"]}
    )
    preview_data = preview_response.json()
    assert preview_data["reality_check"] == "OVERLOADED"
    assert preview_data["unscheduled_tasks"]
    provider_call.assert_awaited_once()


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
async def test_chat_contract_accepts_current_draft_without_auto_preview(
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
    assert body["preview"] is None


@pytest.mark.asyncio
@pytest.mark.parametrize(
    ("answer", "durations"),
    [("First one.", [20, 25]), ("Second one.", [30, 20])],
)
async def test_edit_04_session_clarification_resolves_duplicate_by_ordinal(
    async_client: AsyncClient,
    auth_headers: dict[str, str],
    answer: str,
    durations: list[int],
):
    draft = {
        "type": "today", "planDate": date.today().isoformat(), "timezone": "UTC",
        "windows": [{"start": "09:00", "end": "17:00"}],
        "tasks": [
            {"id": "review-1", "title": "Review notes", "durationMin": 30},
            {"id": "review-2", "title": "Review notes", "durationMin": 25},
        ],
    }
    first = await async_client.post(
        "/api/v1/assistant/chat", headers=auth_headers,
        json={"message": "Change Review notes to 20 minutes.", "current_draft": draft},
    )
    assert first.status_code == 200, first.text
    first_body = first.json()
    assert first_body["question"] == "Which task did you mean?"
    assert [task["durationMin"] for task in first_body["draft"]["tasks"]] == [30, 25]

    second = await async_client.post(
        "/api/v1/assistant/chat", headers=auth_headers,
        json={
            "message": answer,
            "session_id": first_body["session_id"],
            "current_draft": first_body["draft"],
        },
    )
    assert second.status_code == 200, second.text
    body = second.json()
    assert body["question"] is None
    assert body["preview"] is None
    assert [task["id"] for task in body["draft"]["tasks"]] == ["review-1", "review-2"]
    assert [task["durationMin"] for task in body["draft"]["tasks"]] == durations


@pytest.mark.asyncio
async def test_new_explicit_today_plan_clears_stale_edit_clarification(
    async_client: AsyncClient,
    auth_headers: dict[str, str],
    db_session,
):
    plan_date = date.today().isoformat()
    conflicting_draft = {
        "type": "today", "planDate": plan_date, "timezone": "UTC",
        "windows": [{"start": "09:00", "end": "12:00"}],
        "tasks": [
            {
                "id": "old-1", "title": "Review notes", "durationMin": 60,
                "schedulingType": "FIXED", "fixedStart": f"{plan_date}T09:00:00",
                "fixedEnd": f"{plan_date}T10:00:00",
            },
            {
                "id": "old-2", "title": "Review notes", "durationMin": 60,
                "schedulingType": "FIXED", "fixedStart": f"{plan_date}T09:30:00",
                "fixedEnd": f"{plan_date}T10:30:00",
            },
        ],
    }
    first = await async_client.post(
        "/api/v1/assistant/chat", headers=auth_headers,
        json={
            "message": "Change Review notes to 20 minutes.",
            "current_draft": conflicting_draft,
        },
    )
    first_body = first.json()
    assert first.status_code == 200, first.text
    assert first_body["question"] == "Which task did you mean?"

    second = await async_client.post(
        "/api/v1/assistant/chat", headers=auth_headers,
        json={
            "message": "Today from 7 PM to 9 PM, review database systems for 1 hour.",
            "session_id": first_body["session_id"],
            "current_draft": first_body["draft"],
        },
    )
    body = second.json()
    assert second.status_code == 200, second.text
    assert body["intent"] == "PLAN_DAY"
    assert body["question"] is None
    assert body["preview"] is None
    assert [(task["title"], task["durationMin"]) for task in body["draft"]["tasks"]] == [
        ("Review database systems", 60)
    ]
    assert body["draft"]["windows"] == [{"start": "19:00", "end": "21:00"}]

    state = await db_session.get(PlanningSession, UUID(body["session_id"]))
    await db_session.refresh(state)
    assert state.status == "OPEN"
    assert state.pending_intent is None


@pytest.mark.asyncio
async def test_explicit_goal_clears_today_edit_state_without_persisting_goal(
    async_client: AsyncClient,
    auth_headers: dict[str, str],
    db_session,
):
    plan_date = date.today().isoformat()
    today_draft = {
        "type": "today", "planDate": plan_date, "timezone": "UTC",
        "windows": [{"start": "09:00", "end": "17:00"}],
        "tasks": [
            {"id": "old-1", "title": "Review notes", "durationMin": 30},
            {"id": "old-2", "title": "Review notes", "durationMin": 25},
        ],
    }
    clarification = await async_client.post(
        "/api/v1/assistant/chat", headers=auth_headers,
        json={
            "message": "Change Review notes to 20 minutes.",
            "current_draft": today_draft,
        },
    )
    clarification_body = clarification.json()
    assert clarification_body["question"] == "Which task did you mean?"
    goals_before = await db_session.scalar(select(func.count(Goal.id)))

    response = await async_client.post(
        "/api/v1/assistant/chat", headers=auth_headers,
        json={
            "message": "I want to finish my AI course project by October 30, 2026.",
            "session_id": clarification_body["session_id"],
            "current_draft": clarification_body["draft"],
        },
    )
    body = response.json()
    assert response.status_code == 200, response.text
    assert body["intent"] == "CREATE_GOAL"
    assert body["draft"]["type"] == "roadmap"
    assert body["draft"]["goalTitle"] == "finish my AI course project"
    assert body["draft"]["targetDate"] == "2026-10-30"
    assert len(body["draft"]["milestones"]) == 3
    assert body["assumptions"][0]["kind"] == "FRAMEWORK"
    assert body["preview"] is None

    state = await db_session.get(PlanningSession, UUID(body["session_id"]))
    await db_session.refresh(state)
    assert state.status == "OPEN"
    assert state.pending_intent is None
    assert await db_session.scalar(select(func.count(Goal.id))) == goals_before


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
    
    preview_response = await async_client.post(
        "/api/v1/today/preview",
        headers=auth_headers,
        json={"draft": body["draft"]}
    )
    preview_data = preview_response.json()
    
    saved = await async_client.post(
        "/api/v1/today/save",
        headers=auth_headers,
        json={
            "session_id": body["session_id"],
            "preview_token": preview_data["preview_token"],
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
