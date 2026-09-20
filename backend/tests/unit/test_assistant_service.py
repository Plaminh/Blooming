import json as jsonlib
from unittest.mock import Mock, AsyncMock

import pytest
import httpx
from pydantic import SecretStr
from fastapi import HTTPException

from app.schemas.assistant import ChatRequest, ChatTurn
from app.services import assistant_service


@pytest.mark.asyncio
async def test_chat_sends_history_and_returns_model_draft(monkeypatch):
    sent = {}

    class Client:
        async def post(self, url, *, headers, json):
            sent.update(url=url, headers=headers, body=json)
            response = Mock()
            response.raise_for_status = Mock()
            response.json.return_value = {"choices": [{"message": {"content": jsonlib.dumps({
                "reply": "Here is your plan.",
                "draft": {"type": "today", "planDate": "2026-09-20", "windows": [{"start": "09:00", "end": "12:00"}],
                          "tasks": [{"title": "Write report", "durationMin": 90, "id": "t1", "priority": "MEDIUM"}]},
            })}}]}
            return response

    monkeypatch.setattr(assistant_service, "ai_client", Client())
    monkeypatch.setattr(assistant_service.settings, "GROQ_API_KEY", SecretStr("test-key"))
    result = await assistant_service.chat(ChatRequest(
        message="Plan my report", history=[ChatTurn(role="user", content="I have three hours")]
    ))

    assert sent["url"].endswith("/chat/completions")
    assert sent["body"]["messages"][-2:] == [
        {"role": "user", "content": "I have three hours"},
        {"role": "user", "content": "Plan my report"},
    ]
    assert result.draft.type == "today"
    assert result.draft.tasks[0].title == "Write report"


@pytest.mark.asyncio
async def test_chat_error_mapping(monkeypatch):
    class ErrorClient:
        def __init__(self, exc):
            self.exc = exc

        async def post(self, url, *, headers, json):
            raise self.exc

    # Test 429 Rate Limit
    response_429 = Mock()
    response_429.status_code = 429
    monkeypatch.setattr(assistant_service, "ai_client", ErrorClient(httpx.HTTPStatusError("rate limited", request=Mock(), response=response_429)))
    monkeypatch.setattr(assistant_service.settings, "GROQ_API_KEY", SecretStr("test-key"))
    
    with pytest.raises(HTTPException) as excinfo:
        await assistant_service.chat(ChatRequest(message="Hello"))
    assert excinfo.value.status_code == 429
    assert excinfo.value.detail == "rate_limit"

    # Test Timeout
import json as jsonlib
from unittest.mock import Mock, AsyncMock

import pytest
import httpx
from pydantic import SecretStr
from fastapi import HTTPException

from app.schemas.assistant import ChatRequest, ChatTurn
from app.services import assistant_service


@pytest.mark.asyncio
async def test_chat_sends_history_and_returns_model_draft(monkeypatch):
    sent = {}

    class Client:
        async def post(self, url, *, headers, json):
            sent.update(url=url, headers=headers, body=json)
            response = Mock()
            response.raise_for_status = Mock()
            response.json.return_value = {"choices": [{"message": {"content": jsonlib.dumps({
                "reply": "Here is your plan.",
                "draft": {"type": "today", "planDate": "2026-09-20", "windows": [{"start": "09:00", "end": "12:00"}],
                          "tasks": [{"title": "Write report", "durationMin": 90, "id": "t1", "priority": "MEDIUM"}]},
            })}}]}
            return response

    monkeypatch.setattr(assistant_service, "ai_client", Client())
    monkeypatch.setattr(assistant_service.settings, "GROQ_API_KEY", SecretStr("test-key"))
    result = await assistant_service.chat(ChatRequest(
        message="Plan my report", history=[ChatTurn(role="user", content="I have three hours")]
    ))

    assert sent["url"].endswith("/chat/completions")
    assert sent["body"]["messages"][-2:] == [
        {"role": "user", "content": "I have three hours"},
        {"role": "user", "content": "Plan my report"},
    ]
    assert result.draft.type == "today"
    assert result.draft.tasks[0].title == "Write report"


@pytest.mark.asyncio
async def test_chat_error_mapping(monkeypatch):
    class ErrorClient:
        def __init__(self, exc):
            self.exc = exc

        async def post(self, url, *, headers, json):
            raise self.exc

    # Test 429 Rate Limit
    response_429 = Mock()
    response_429.status_code = 429
    monkeypatch.setattr(assistant_service, "ai_client", ErrorClient(httpx.HTTPStatusError("rate limited", request=Mock(), response=response_429)))
    monkeypatch.setattr(assistant_service.settings, "GROQ_API_KEY", SecretStr("test-key"))
    
    with pytest.raises(HTTPException) as excinfo:
        await assistant_service.chat(ChatRequest(message="Hello"))
    assert excinfo.value.status_code == 429
    assert excinfo.value.detail == "rate_limit"

    # Test Timeout
    monkeypatch.setattr(assistant_service, "ai_client", ErrorClient(httpx.TimeoutException("timeout")))
    with pytest.raises(HTTPException) as excinfo:
        await assistant_service.chat(ChatRequest(message="Hello"))
    assert excinfo.value.status_code == 504
    assert excinfo.value.detail == "timeout"

    # Test Missing Config
    monkeypatch.setattr(assistant_service.settings, "GROQ_API_KEY", None)
    with pytest.raises(HTTPException) as excinfo:
        await assistant_service.chat(ChatRequest(message="Hello"))
    assert excinfo.value.status_code == 503
    assert excinfo.value.detail == "config"


@pytest.mark.asyncio
async def test_chat_draft_repair_success(monkeypatch):
    responses = [
        {"choices": [{"message": {"content": jsonlib.dumps({
            "reply": "Here is your plan.",
            "draft": {"type": "today", "planDate": "2026-09-20", "windows": [{"start": "09:00", "end": "12:00"}],
                      "tasks": [{"id": "t1", "title": "Invalid task", "durationMin": 0, "priority": "MEDIUM"}]}, # invalid duration
        })}}]},
        {"choices": [{"message": {"content": jsonlib.dumps({
            "reply": "Here is your plan.",
            "draft": {"type": "today", "planDate": "2026-09-20", "windows": [{"start": "09:00", "end": "12:00"}],
                      "tasks": [{"id": "t1", "title": "Invalid task", "durationMin": 30, "priority": "MEDIUM"}]}, # valid duration
        })}}]}
    ]

    class RepairClient:
        def __init__(self):
            self.calls = 0

        async def post(self, url, *, headers, json):
            res = responses[self.calls]
            self.calls += 1
            response = Mock()
            response.raise_for_status = Mock()
            response.json.return_value = res
            return response

    monkeypatch.setattr(assistant_service, "ai_client", RepairClient())
    monkeypatch.setattr(assistant_service.settings, "GROQ_API_KEY", SecretStr("test-key"))
    
    result = await assistant_service.chat(ChatRequest(message="Plan something"))
    assert result.reply == "Here is your plan."
    assert result.draft is not None
    assert result.draft.tasks[0].durationMin == 30


@pytest.mark.asyncio
async def test_chat_draft_repair_failure_preserves_reply(monkeypatch):
    responses = [
        {"choices": [{"message": {"content": jsonlib.dumps({
            "reply": "Here is your plan.",
            "draft": {"type": "today", "planDate": "2026-09-20", "windows": [{"start": "09:00", "end": "12:00"}],
                      "tasks": [{"title": "Invalid task", "durationMin": 0, "id": "t1", "priority": "MEDIUM"}]}, # invalid duration
        })}}]},
        {"choices": [{"message": {"content": jsonlib.dumps({
            "reply": "Here is your plan.",
            "draft": {"type": "today", "planDate": "2026-09-20", "windows": [{"start": "09:00", "end": "12:00"}],
                      "tasks": [{"title": "Invalid task", "durationMin": -10, "id": "t1", "priority": "MEDIUM"}]}, # still invalid duration
        })}}]}
    ]

    class RepairFailClient:
        def __init__(self):
            self.calls = 0

        async def post(self, url, *, headers, json):
            res = responses[self.calls]
            self.calls += 1
            response = Mock()
            response.raise_for_status = Mock()
            response.json.return_value = res
            return response

    monkeypatch.setattr(assistant_service, "ai_client", RepairFailClient())
    monkeypatch.setattr(assistant_service.settings, "GROQ_API_KEY", SecretStr("test-key"))
    
    result = await assistant_service.chat(ChatRequest(message="Plan something"))
    assert "Here is your plan." in result.reply
    assert "(I had some trouble" in result.reply
    assert result.draft is None

