import pytest
from httpx import AsyncClient
from unittest.mock import AsyncMock
from sqlalchemy import select, func

from app.db.models.planning import PlanningSession, PlanningMessage
from app.db.models.ai_usage import AiUsageLog
from app.db.models.users import User
from app.ai.llm.providers import llm_provider


@pytest.mark.asyncio
async def test_ct_001_authentication_required(async_client: AsyncClient):
    endpoints = [
        ("POST", "/api/v1/assistant/chat", {"message": "hello"}),
        ("GET", "/api/v1/assistant/sessions/latest", None),
        (
            "GET",
            "/api/v1/assistant/sessions/00000000-0000-0000-0000-000000000000",
            None,
        ),
        ("POST", "/api/v1/assistant/apply-patch", {"draft": {}, "ops": []}),
        ("POST", "/api/v1/assistant/actions/REPLAN_TODAY", None),
        (
            "POST",
            "/api/v1/assistant/events",
            {"event_id": "test", "event_name": "SKIP"},
        ),
    ]
    for method, url, json_data in endpoints:
        if method == "POST":
            response = await async_client.post(url, json=json_data)
        else:
            response = await async_client.get(url)
        assert response.status_code == 401, (
            f"{method} {url} returned {response.status_code}"
        )


@pytest.mark.asyncio
async def test_sec_007_cross_user_session_isolation(
    async_client: AsyncClient,
    db_session,
    monkeypatch,
    test_user: User,
    test_user_two: User,
    auth_headers_two: dict[str, str],
):
    provider_call = AsyncMock()
    monkeypatch.setattr(llm_provider, "call", provider_call)

    # Create Session A owned by User A (test_user)
    session_a = PlanningSession(
        user_id=test_user.id, session_type="DAILY_PLAN", status="OPEN"
    )
    db_session.add(session_a)
    await db_session.commit()
    session_a_id = session_a.id
    user_a_id = test_user.id

    # State before
    before_sessions = await db_session.scalar(select(func.count(PlanningSession.id)))
    before_messages = await db_session.scalar(select(func.count(PlanningMessage.id)))
    before_usage = await db_session.scalar(select(func.count(AiUsageLog.id)))

    # Try to access Session A as User B (test_user_two)
    headers = auth_headers_two

    # 1. POST /chat with session_a id
    response1 = await async_client.post(
        "/api/v1/assistant/chat",
        json={"message": "hello", "session_id": str(session_a_id)},
        headers=headers,
    )
    assert response1.status_code == 404

    # 2. GET /sessions/{session_id}
    response2 = await async_client.get(
        f"/api/v1/assistant/sessions/{session_a_id}", headers=headers
    )
    assert response2.status_code == 404

    # State after
    after_sessions = await db_session.scalar(select(func.count(PlanningSession.id)))
    after_messages = await db_session.scalar(select(func.count(PlanningMessage.id)))
    after_usage = await db_session.scalar(select(func.count(AiUsageLog.id)))

    # Assert isolation prevented mutations
    assert before_sessions == after_sessions
    assert before_messages == after_messages
    assert before_usage == after_usage

    # Assert isolation prevented provider leak
    provider_call.assert_not_awaited()

    # Assert Session A still belongs to User A
    final_session = await db_session.scalar(
        select(PlanningSession).where(PlanningSession.id == session_a_id)
    )
    assert final_session is not None
    assert final_session.user_id == user_a_id


@pytest.mark.asyncio
async def test_ss_003_unauthorized_request_creates_no_side_effects(
    async_client: AsyncClient, db_session, monkeypatch
):
    provider_call = AsyncMock()
    monkeypatch.setattr(llm_provider, "call", provider_call)

    before_sessions = await db_session.scalar(select(func.count(PlanningSession.id)))
    before_messages = await db_session.scalar(select(func.count(PlanningMessage.id)))
    before_usage = await db_session.scalar(select(func.count(AiUsageLog.id)))

    response = await async_client.post(
        "/api/v1/assistant/chat", json={"message": "hello"}
    )
    assert response.status_code == 401

    after_sessions = await db_session.scalar(select(func.count(PlanningSession.id)))
    after_messages = await db_session.scalar(select(func.count(PlanningMessage.id)))
    after_usage = await db_session.scalar(select(func.count(AiUsageLog.id)))

    assert before_sessions == after_sessions
    assert before_messages == after_messages
    assert before_usage == after_usage
    provider_call.assert_not_awaited()
