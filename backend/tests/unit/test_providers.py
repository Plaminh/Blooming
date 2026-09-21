import json
import logging

import httpx
import pytest
from app.ai.providers import CircuitBreaker, LLMError, LLMProvider, parse_retry_after, strictify_schema
from app.ai.handlers.planner import LLMDayPlan
from app.core.config import settings
from pydantic import SecretStr


def test_circuit_breaker():
    now = [100.0]
    cb = CircuitBreaker(failure_threshold=2, cooldown_seconds=60, clock=lambda: now[0])

    assert cb.is_allowed() == True

    cb.record_failure()
    assert cb.is_allowed() == True

    cb.record_failure()
    assert cb.is_allowed() == False

    now[0] += 60

    # Should be half-open now
    assert cb.is_allowed() == True

    # Successful request resets it
    cb.record_success()
    assert cb.is_allowed() == True


def test_parse_route_and_retry_after():
    provider = LLMProvider()
    assert provider.parse_route(" ollama:qwen2.5:7b , groq:openai/gpt-oss-20b ") == [
        ("ollama", "qwen2.5:7b"),
        ("groq", "openai/gpt-oss-20b"),
    ]
    assert parse_retry_after("120.5") == 120.5
    assert parse_retry_after("9999") == 900
    assert parse_retry_after("invalid") == 60
    for route in ("", "unknown:model", "groq:"):
        with pytest.raises(LLMError):
            provider.parse_route(route)


def envelope(content, usage=None):
    return {"choices": [{"message": {"content": content}}], "usage": usage or {}}


@pytest.mark.asyncio
async def test_fallback_429_opens_only_one_model_and_keeps_logs_private(
    monkeypatch, caplog
):
    monkeypatch.setattr(settings, "GROQ_API_KEY", SecretStr("test-secret"))
    requests = []

    def respond(request):
        body = json.loads(request.content)
        requests.append(body["model"])
        if body["model"] == "small":
            return httpx.Response(
                429, headers={"Retry-After": "120"}, json={"error": "private response"}
            )
        return httpx.Response(200, json=envelope('{"reply":"private response"}'))

    client = httpx.AsyncClient(transport=httpx.MockTransport(respond))
    provider = LLMProvider(client)
    with caplog.at_level(logging.INFO):
        result = await provider.call(
            "groq:small,groq:large",
            [{"role": "user", "content": "private request"}],
            require_json=True,
        )
    assert result == {"reply": "private response"}
    assert requests == ["small", "large"]
    assert provider.get_circuit_breaker("groq", "small").is_allowed() is False
    assert provider.get_circuit_breaker("groq", "large").is_allowed() is True
    await provider.call("groq:small,groq:large", [], require_json=True)
    assert requests == ["small", "large", "large"]
    assert "private request" not in caplog.text
    assert "private response" not in caplog.text
    assert "test-secret" not in caplog.text
    await provider.close_client()


@pytest.mark.asyncio
async def test_upstream_500_cascades(monkeypatch):
    monkeypatch.setattr(settings, "GROQ_API_KEY", SecretStr("test-secret"))
    calls = []

    def respond(request):
        model = json.loads(request.content)["model"]
        calls.append(model)
        if model == "small":
            return httpx.Response(500, json={"error": "unavailable"})
        return httpx.Response(200, json=envelope('{"ok":true}'))

    provider = LLMProvider(httpx.AsyncClient(transport=httpx.MockTransport(respond)))
    assert await provider.call("groq:small,groq:large", [], require_json=True) == {
        "ok": True
    }
    assert calls == ["small", "large"]
    await provider.close_client()


@pytest.mark.asyncio
async def test_timeout_cascades_and_opens_breaker(monkeypatch):
    monkeypatch.setattr(settings, "GROQ_API_KEY", SecretStr("test-secret"))
    calls = []

    def respond(request):
        model = json.loads(request.content)["model"]
        calls.append(model)
        if model == "small":
            raise httpx.ReadTimeout("private timeout detail")
        return httpx.Response(200, json=envelope('{"ok":true}'))

    provider = LLMProvider(httpx.AsyncClient(transport=httpx.MockTransport(respond)))
    for _ in range(3):
        assert await provider.call("groq:small,groq:large", [], require_json=True) == {
            "ok": True
        }
    assert calls == ["small", "large"] * 3
    assert provider.get_circuit_breaker("groq", "small").is_allowed() is False
    assert await provider.call("groq:small,groq:large", [], require_json=True) == {
        "ok": True
    }
    assert calls[-1] == "large"
    assert calls.count("small") == 3
    await provider.close_client()


@pytest.mark.asyncio
async def test_strict_and_json_object_payloads(monkeypatch):
    monkeypatch.setattr(settings, "GROQ_API_KEY", SecretStr("test-secret"))
    captured = []

    def respond(request):
        captured.append(json.loads(request.content))
        return httpx.Response(200, json=envelope('{"ok":true}'))

    provider = LLMProvider(httpx.AsyncClient(transport=httpx.MockTransport(respond)))
    schema = {"type": "object", "properties": {"ok": {"type": "boolean", "default": True}}}
    await provider.call(
        "groq:openai/gpt-oss-20b", [], require_json=True, json_schema=schema
    )
    await provider.call("ollama:qwen2.5:7b", [], require_json=True, json_schema=schema)
    assert captured[0]["response_format"]["json_schema"]["strict"] is True
    strict = captured[0]["response_format"]["json_schema"]["schema"]
    assert strict["required"] == ["ok"]
    assert strict["additionalProperties"] is False
    assert "default" not in strict["properties"]["ok"]
    assert captured[0]["reasoning_effort"] == "low"
    assert captured[1]["response_format"] == {"type": "json_object"}
    assert "schema" in captured[1]["messages"][0]["content"]
    await provider.close_client()


def test_strict_schema_recursively_requires_nullable_fields_and_closes_objects():
    schema = strictify_schema(LLMDayPlan.model_json_schema())
    assert schema["required"] == list(schema["properties"])
    assert schema["additionalProperties"] is False
    task = schema["$defs"]["LLMTask"]
    assert task["required"] == list(task["properties"])
    assert task["additionalProperties"] is False
    assert "default" not in task["properties"]["priority"]
    assert "prefixItems" not in schema["properties"]["windows"]["items"]


@pytest.mark.asyncio
async def test_bad_json_does_not_cascade(monkeypatch):
    monkeypatch.setattr(settings, "GROQ_API_KEY", SecretStr("test-secret"))
    calls = []

    def respond(request):
        calls.append(json.loads(request.content)["model"])
        return httpx.Response(200, json=envelope("not JSON"))

    provider = LLMProvider(httpx.AsyncClient(transport=httpx.MockTransport(respond)))
    with pytest.raises(LLMError, match="bad_output"):
        await provider.call("groq:small,groq:large", [], require_json=True)
    assert calls == ["small"]
    await provider.close_client()


@pytest.mark.asyncio
async def test_client_lifecycle():
    provider = LLMProvider()
    provider.init_client()
    client = provider.client
    provider.init_client()
    assert provider.client is client
    await provider.close_client()
    assert client.is_closed
    assert provider.client is None
