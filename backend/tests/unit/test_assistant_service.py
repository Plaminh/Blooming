import json as jsonlib
from unittest.mock import Mock

import pytest
from pydantic import SecretStr

from app.schemas.assistant import ChatRequest, ChatTurn
from app.services import assistant_service


@pytest.mark.asyncio
async def test_chat_sends_history_and_returns_model_draft(monkeypatch):
    sent = {}

    class Client:
        async def __aenter__(self):
            return self

        async def __aexit__(self, *_):
            return None

        async def post(self, url, *, headers, json):
            sent.update(url=url, headers=headers, body=json)
            response = Mock()
            response.json.return_value = {"choices": [{"message": {"content": jsonlib.dumps({
                "reply": "Here is your plan.",
                "draft": {"type": "today", "availability": {"start": "09:00", "end": "12:00", "totalHours": 3},
                          "tasks": [{"title": "Write report", "durationMin": 90, "priority": "Core"}]},
            })}}]}
            return response

    monkeypatch.setattr(assistant_service.httpx, "AsyncClient", lambda **_: Client())
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
