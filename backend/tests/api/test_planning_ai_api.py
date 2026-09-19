import pytest
from httpx import AsyncClient
from app.models.ai_schemas import AIRequestContext
from app.services.ai_router import AIRouterException
import zoneinfo

from unittest.mock import patch, AsyncMock

@pytest.fixture
def mock_ai_router():
    with patch("app.api.routes.planning.AIRouter") as mock:
        yield mock.return_value

@pytest.mark.asyncio
async def test_auth_required(async_client: AsyncClient):
    resp = await async_client.post("/api/v1/planning/draft", json={
        "user_input": "test",
        "context_type": "today_planning"
    })
    assert resp.status_code == 401

@pytest.mark.asyncio
async def test_planning_api_uses_async_router_mock(async_client: AsyncClient, access_token: str, mock_ai_router):
    mock_ai_router.generate_draft = AsyncMock(return_value={
        "status": "success",
        "meta": {"provider_used": "GROQ"},
        "data": {"tasks": []}
    })
    
    resp = await async_client.post("/api/v1/planning/draft", json={
        "user_input": "test",
        "context_type": "today_planning"
    }, headers={"Authorization": f"Bearer {access_token}"})
    
    assert resp.status_code == 200
    assert resp.json()["status"] == "success"

@pytest.mark.asyncio
async def test_success_200(async_client: AsyncClient, access_token: str, mock_ai_router):
    mock_ai_router.generate_draft = AsyncMock(return_value={
        "status": "success",
        "meta": {"provider_used": "GROQ"},
        "data": {"tasks": []}
    })
    
    resp = await async_client.post("/api/v1/planning/draft", json={
        "user_input": "test",
        "context_type": "today_planning"
    }, headers={"Authorization": f"Bearer {access_token}"})
    
    assert resp.status_code == 200
    assert resp.json()["status"] == "success"

@pytest.mark.asyncio
async def test_clarification_200(async_client: AsyncClient, access_token: str, mock_ai_router):
    mock_ai_router.generate_draft = AsyncMock(return_value={
        "status": "needs_clarification",
        "meta": {"provider_used": "GROQ"},
        "clarification": {"questions": ["what?"]}
    })
    
    resp = await async_client.post("/api/v1/planning/draft", json={
        "user_input": "test",
        "context_type": "today_planning"
    }, headers={"Authorization": f"Bearer {access_token}"})
    
    assert resp.status_code == 200
    assert resp.json()["status"] == "needs_clarification"
    assert "questions" in resp.json()["clarification"]

@pytest.mark.asyncio
async def test_business_validation_failure_422(async_client: AsyncClient, access_token: str, mock_ai_router):
    mock_ai_router.generate_draft = AsyncMock(side_effect=AIRouterException(
        code="BUSINESS_VALIDATION_FAILURE",
        message="Bad",
        status_code=422,
        provider_used="GROQ",
        fallback=False,
        latency=100
    ))
    
    resp = await async_client.post("/api/v1/planning/draft", json={
        "user_input": "test",
        "context_type": "today_planning"
    }, headers={"Authorization": f"Bearer {access_token}"})
    
    assert resp.status_code == 422
    data = resp.json()
    assert data["status"] == "error"
    assert data["error"]["code"] == "BUSINESS_VALIDATION_FAILURE"

@pytest.mark.asyncio
async def test_invalid_ai_output_502(async_client: AsyncClient, access_token: str, mock_ai_router):
    mock_ai_router.generate_draft = AsyncMock(side_effect=AIRouterException(
        code="STRUCTURED_OUTPUT_INVALID",
        message="Bad output",
        status_code=502,
        provider_used="GEMINI",
        fallback=True,
        latency=100
    ))
    
    resp = await async_client.post("/api/v1/planning/draft", json={
        "user_input": "test",
        "context_type": "today_planning"
    }, headers={"Authorization": f"Bearer {access_token}"})
    
    assert resp.status_code == 502
    data = resp.json()
    assert data["error"]["code"] == "STRUCTURED_OUTPUT_INVALID"
    
@pytest.mark.asyncio
async def test_providers_unavailable_503(async_client: AsyncClient, access_token: str, mock_ai_router):
    mock_ai_router.generate_draft = AsyncMock(side_effect=AIRouterException(
        code="AI_SERVICE_UNAVAILABLE",
        message="Down",
        status_code=503,
        provider_used="GEMINI",
        fallback=True,
        latency=100
    ))
    
    resp = await async_client.post("/api/v1/planning/draft", json={
        "user_input": "test",
        "context_type": "today_planning"
    }, headers={"Authorization": f"Bearer {access_token}"})
    
    assert resp.status_code == 503
    data = resp.json()
    assert data["error"]["code"] == "AI_SERVICE_UNAVAILABLE"
    
@pytest.mark.asyncio
async def test_unexpected_backend_error_500(async_client: AsyncClient, access_token: str, mock_ai_router):
    mock_ai_router.generate_draft = AsyncMock(side_effect=Exception("Boom"))
    
    resp = await async_client.post("/api/v1/planning/draft", json={
        "user_input": "test",
        "context_type": "today_planning"
    }, headers={"Authorization": f"Bearer {access_token}"})
    
    assert resp.status_code == 500
    data = resp.json()
    assert data["error"]["code"] == "INTERNAL_SERVER_ERROR"
    # Never expose exception strings
    assert "Boom" not in resp.text

@pytest.mark.asyncio
async def test_missing_timezone_422(async_client: AsyncClient, access_token: str, db_session):
    from app.db.models.users import UserSettings
    from sqlalchemy import update
    
    # Empty timezone
    await db_session.execute(update(UserSettings).values(timezone=None))
    await db_session.commit()
    
    resp = await async_client.post("/api/v1/planning/draft", json={
        "user_input": "test",
        "context_type": "today_planning"
    }, headers={"Authorization": f"Bearer {access_token}"})
    
    assert resp.status_code == 422
    assert resp.json()["error"]["code"] == "TIMEZONE_NOT_CONFIGURED"

@pytest.mark.asyncio
async def test_invalid_timezone_422(async_client: AsyncClient, access_token: str, db_session):
    from app.db.models.users import UserSettings
    from sqlalchemy import update
    
    await db_session.execute(update(UserSettings).values(timezone="Invalid/Timezone"))
    await db_session.commit()
    
    resp = await async_client.post("/api/v1/planning/draft", json={
        "user_input": "test",
        "context_type": "today_planning"
    }, headers={"Authorization": f"Bearer {access_token}"})
    
    assert resp.status_code == 422
    assert resp.json()["error"]["code"] == "INVALID_TIMEZONE"
