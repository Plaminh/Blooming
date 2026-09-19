import pytest
import httpx
from unittest.mock import AsyncMock, patch
from app.services.groq_provider import GroqProvider
from app.models.ai_schemas import AIRequestContext
from app.services.ai_provider import AIProviderException, ProviderErrorCategory
from datetime import datetime
import zoneinfo
from pydantic import SecretStr

@pytest.fixture
def req_context():
    return AIRequestContext(
        user_input="test",
        context_type="today_planning",
        current_time=datetime.now(zoneinfo.ZoneInfo("UTC")),
        timezone="UTC"
    )

@pytest.fixture
def mock_settings():
    with patch("app.services.groq_provider.settings") as s:
        s.GROQ_API_KEY = SecretStr("fake_key")
        s.AI_GATEWAY_URL = "https://gateway"
        s.CF_AIG_TOKEN = SecretStr("cf_token")
        s.GROQ_MODEL = "model"
        yield s

@pytest.mark.asyncio
@patch("httpx.AsyncClient.post", new_callable=AsyncMock)
async def test_groq_success(mock_post, req_context, mock_settings):
    provider = GroqProvider()
    mock_response = mock_post.return_value
    mock_response.status_code = 200
    mock_response.json = lambda: {
        "choices": [{"message": {"content": '{"status": "DRAFT", "proposal": {"tasks": []}}'}}]
    }
    mock_response.raise_for_status = lambda: None
    
    res = await provider.invoke(req_context)
    assert res["status"] == "DRAFT"
    
    # Assert correct gateway URL used
    mock_post.assert_called_once()
    args, kwargs = mock_post.call_args
    assert kwargs["headers"]["cf-aig-authorization"] == "Bearer cf_token"
    assert kwargs["headers"]["Authorization"] == "Bearer fake_key"
    assert args[0] == "https://gateway/groq/chat/completions"
    assert kwargs["json"]["response_format"]["type"] == "json_schema"
    assert kwargs["json"]["response_format"]["json_schema"]["strict"] is False
    assert kwargs["json"]["response_format"]["json_schema"]["name"] == "today_interpretation"
    assert "schema" in kwargs["json"]["response_format"]["json_schema"]

@pytest.mark.asyncio
@patch("httpx.AsyncClient.post", new_callable=AsyncMock)
async def test_groq_roadmap_context(mock_post, mock_settings):
    provider = GroqProvider()
    req = AIRequestContext(
        user_input="test",
        context_type="roadmap_planning",
        current_time=datetime.now(zoneinfo.ZoneInfo("UTC")),
        timezone="UTC"
    )
    mock_response = mock_post.return_value
    mock_response.status_code = 200
    mock_response.json = lambda: {
        "choices": [{"message": {"content": '{"status": "DRAFT"}'}}]
    }
    
    await provider.invoke(req)
    _, kwargs = mock_post.call_args
    assert kwargs["json"]["response_format"]["json_schema"]["name"] == "roadmap_interpretation"
    
@pytest.mark.asyncio
@patch("httpx.AsyncClient.post", new_callable=AsyncMock)
async def test_groq_direct_url(mock_post, req_context, mock_settings):
    mock_settings.AI_GATEWAY_URL = None
    provider = GroqProvider()
    mock_response = mock_post.return_value
    mock_response.status_code = 200
    mock_response.json = lambda: {
        "choices": [{"message": {"content": '{"status": "DRAFT"}'}}]
    }
    
    await provider.invoke(req_context)
    args, kwargs = mock_post.call_args
    assert args[0] == "https://api.groq.com/openai/v1/chat/completions"

@pytest.mark.asyncio
@patch("httpx.AsyncClient.post", new_callable=AsyncMock)
async def test_groq_timeout(mock_post, req_context, mock_settings):
    provider = GroqProvider()
    mock_post.side_effect = httpx.TimeoutException("Timeout")
    
    with pytest.raises(AIProviderException) as exc:
        await provider.invoke(req_context)
    assert exc.value.category == ProviderErrorCategory.TIMEOUT

@pytest.mark.asyncio
@patch("httpx.AsyncClient.post", new_callable=AsyncMock)
async def test_groq_401(mock_post, req_context, mock_settings):
    provider = GroqProvider()
    mock_post.return_value.status_code = 401
    
    with pytest.raises(AIProviderException) as exc:
        await provider.invoke(req_context)
    assert exc.value.category == ProviderErrorCategory.AUTH_ERROR

@pytest.mark.asyncio
@patch("httpx.AsyncClient.post", new_callable=AsyncMock)
async def test_groq_429(mock_post, req_context, mock_settings):
    provider = GroqProvider()
    mock_post.return_value.status_code = 429
    
    with pytest.raises(AIProviderException) as exc:
        await provider.invoke(req_context)
    assert exc.value.category == ProviderErrorCategory.RATE_LIMIT

@pytest.mark.asyncio
@patch("httpx.AsyncClient.post", new_callable=AsyncMock)
async def test_groq_500(mock_post, req_context, mock_settings):
    provider = GroqProvider()
    mock_post.return_value.status_code = 500
    
    with pytest.raises(AIProviderException) as exc:
        await provider.invoke(req_context)
    assert exc.value.category == ProviderErrorCategory.PROVIDER_5XX

@pytest.mark.asyncio
@patch("httpx.AsyncClient.post", new_callable=AsyncMock)
async def test_groq_malformed(mock_post, req_context, mock_settings):
    provider = GroqProvider()
    mock_response = mock_post.return_value
    mock_response.status_code = 200
    mock_response.json = lambda: {
        "choices": [{"message": {"content": 'invalid json'}}]
    }
    mock_response.raise_for_status = lambda: None
    
    with pytest.raises(AIProviderException) as exc:
        await provider.invoke(req_context)
    assert exc.value.category == ProviderErrorCategory.MALFORMED_RESPONSE
