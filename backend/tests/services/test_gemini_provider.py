import pytest
import httpx
from unittest.mock import AsyncMock, patch
from app.services.gemini_provider import GeminiProvider
from app.models.ai_schemas import AIRequestContext
from app.services.ai_provider import AIProviderException, ProviderErrorCategory
from datetime import datetime
import zoneinfo
from pydantic import SecretStr

@pytest.fixture
def req_context():
    return AIRequestContext(
        user_input="test",
        context_type="roadmap_planning",
        current_time=datetime.now(zoneinfo.ZoneInfo("UTC")),
        timezone="UTC"
    )

@pytest.fixture
def mock_settings():
    with patch("app.services.gemini_provider.settings") as s:
        s.GEMINI_API_KEY = SecretStr("fake_key")
        s.AI_GATEWAY_URL = "https://gateway"
        s.CF_AIG_TOKEN = SecretStr("cf_token")
        s.GEMINI_MODEL = "model"
        yield s

@pytest.mark.asyncio
@patch("httpx.AsyncClient.post", new_callable=AsyncMock)
async def test_gemini_success(mock_post, req_context, mock_settings):
    provider = GeminiProvider()
    mock_response = mock_post.return_value
    mock_response.status_code = 200
    mock_response.json = lambda: {
        "candidates": [{"content": {"parts": [{"text": '{"status": "DRAFT", "proposal": {"goal_title": "G", "milestones": []}}'}]}}]
    }
    mock_response.raise_for_status = lambda: None
    
    res = await provider.invoke(req_context)
    assert res["status"] == "DRAFT"
    
    # Assert correct gateway URL used
    mock_post.assert_called_once()
    args, kwargs = mock_post.call_args
    assert kwargs["headers"]["cf-aig-authorization"] == "Bearer cf_token"
    assert kwargs["headers"]["x-goog-api-key"] == "fake_key"
    assert args[0] == "https://gateway/google-ai-studio/v1/models/model:generateContent"
    assert kwargs["json"]["generationConfig"]["responseMimeType"] == "application/json"
    assert "responseJsonSchema" in kwargs["json"]["generationConfig"]
    assert "fake_key" not in args[0]
    
@pytest.mark.asyncio
@patch("httpx.AsyncClient.post", new_callable=AsyncMock)
async def test_gemini_today_context(mock_post, mock_settings):
    provider = GeminiProvider()
    req = AIRequestContext(
        user_input="test",
        context_type="today_planning",
        current_time=datetime.now(zoneinfo.ZoneInfo("UTC")),
        timezone="UTC"
    )
    mock_response = mock_post.return_value
    mock_response.status_code = 200
    mock_response.json = lambda: {
        "candidates": [{"content": {"parts": [{"text": '{"status": "DRAFT"}'}]}}]
    }
    
    await provider.invoke(req)
    args, kwargs = mock_post.call_args
    schema = kwargs["json"]["generationConfig"]["responseJsonSchema"]
    assert "$defs" in schema
    assert schema["title"] == "TodayAIInterpretation"
    assert "fake_key" not in args[0]

@pytest.mark.asyncio
@patch("httpx.AsyncClient.post", new_callable=AsyncMock)
async def test_gemini_direct_url(mock_post, req_context, mock_settings):
    mock_settings.AI_GATEWAY_URL = None
    provider = GeminiProvider()
    mock_response = mock_post.return_value
    mock_response.status_code = 200
    mock_response.json = lambda: {
        "candidates": [{"content": {"parts": [{"text": '{"status": "DRAFT"}'}]}}]
    }
    
    await provider.invoke(req_context)
    args, kwargs = mock_post.call_args
    assert args[0] == "https://generativelanguage.googleapis.com/v1beta/models/model:generateContent"
    assert "fake_key" not in args[0]

@pytest.mark.asyncio
@patch("httpx.AsyncClient.post", new_callable=AsyncMock)
async def test_gemini_timeout(mock_post, req_context, mock_settings):
    provider = GeminiProvider()
    mock_post.side_effect = httpx.TimeoutException("Timeout")
    
    with pytest.raises(AIProviderException) as exc:
        await provider.invoke(req_context)
    assert exc.value.category == ProviderErrorCategory.TIMEOUT

@pytest.mark.asyncio
@patch("httpx.AsyncClient.post", new_callable=AsyncMock)
async def test_gemini_403(mock_post, req_context, mock_settings):
    provider = GeminiProvider()
    mock_post.return_value.status_code = 403
    
    with pytest.raises(AIProviderException) as exc:
        await provider.invoke(req_context)
    assert exc.value.category == ProviderErrorCategory.AUTH_ERROR

@pytest.mark.asyncio
@patch("httpx.AsyncClient.post", new_callable=AsyncMock)
async def test_gemini_429(mock_post, req_context, mock_settings):
    provider = GeminiProvider()
    mock_post.return_value.status_code = 429
    
    with pytest.raises(AIProviderException) as exc:
        await provider.invoke(req_context)
    assert exc.value.category == ProviderErrorCategory.RATE_LIMIT

@pytest.mark.asyncio
@patch("httpx.AsyncClient.post", new_callable=AsyncMock)
async def test_gemini_500(mock_post, req_context, mock_settings):
    provider = GeminiProvider()
    mock_post.return_value.status_code = 500
    
    with pytest.raises(AIProviderException) as exc:
        await provider.invoke(req_context)
    assert exc.value.category == ProviderErrorCategory.PROVIDER_5XX

@pytest.mark.asyncio
@patch("httpx.AsyncClient.post", new_callable=AsyncMock)
async def test_gemini_malformed(mock_post, req_context, mock_settings):
    provider = GeminiProvider()
    mock_response = mock_post.return_value
    mock_response.status_code = 200
    mock_response.json = lambda: {
        "candidates": [{"content": {"parts": [{"text": 'invalid json'}]}}]
    }
    mock_response.raise_for_status = lambda: None
    
    with pytest.raises(AIProviderException) as exc:
        await provider.invoke(req_context)
    assert exc.value.category == ProviderErrorCategory.MALFORMED_RESPONSE
