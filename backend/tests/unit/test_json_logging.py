import json
import logging
import pytest
from uuid import UUID
from starlette.requests import Request
from starlette.responses import Response

from app.core.logging import JsonFormatter, RequestContextFilter, request_id_context
from app.core.request_middleware import request_logging


def test_formatter_redacts_sensitive_primitive_extras():
    record = logging.LogRecord("test", logging.INFO, __file__, 1, "safe", (), None)
    record.method = "GET"
    record.path = "/api/v1/health"
    record.status = 200
    record.access_token = "raw-token"
    record.authorization = "Bearer raw"
    record.password = "raw-password"
    record.client_secret = "raw-secret"
    record.api_key = "raw-key"
    record.email = "person@example.com"
    output = json.loads(JsonFormatter().format(record))
    assert output["method"] == "GET"
    assert output["path"] == "/api/v1/health"
    assert output["status"] == 200
    for field in ("access_token", "authorization", "password", "client_secret", "api_key", "email"):
        assert output[field] == "[REDACTED]"


def test_request_context_filter_propagates_and_preserves_request_id():
    token = request_id_context.set("request-123")
    try:
        record = logging.LogRecord("test", logging.INFO, __file__, 1, "inside", (), None)
        assert RequestContextFilter().filter(record)
        assert record.request_id == "request-123"
        explicit = logging.LogRecord("test", logging.INFO, __file__, 1, "inside", (), None)
        explicit.request_id = "incoming-id"
        RequestContextFilter().filter(explicit)
        assert explicit.request_id == "incoming-id"
    finally:
        request_id_context.reset(token)


@pytest.mark.asyncio
async def test_request_middleware_preserves_incoming_id_for_nested_logs_and_response():
    seen: list[str | None] = []

    async def call_next(_request):
        seen.append(request_id_context.get())
        return Response("ok")

    request = Request({
        "type": "http",
        "method": "GET",
        "path": "/inside",
        "raw_path": b"/inside",
        "query_string": b"",
        "headers": [(b"x-request-id", b"incoming-123")],
        "scheme": "http",
        "server": ("test", 80),
        "client": ("test", 123),
        "root_path": "",
        "http_version": "1.1",
    })
    response = await request_logging(request, call_next)
    assert seen == ["incoming-123"]
    assert response.headers["X-Request-ID"] == "incoming-123"
    assert request_id_context.get() is None


@pytest.mark.asyncio
async def test_request_middleware_generates_uuid_when_header_is_absent():
    async def call_next(_request):
        return Response("ok")

    request = Request({
        "type": "http", "method": "GET", "path": "/generated",
        "raw_path": b"/generated", "query_string": b"", "headers": [],
        "scheme": "http", "server": ("test", 80), "client": ("test", 123),
        "root_path": "", "http_version": "1.1",
    })
    response = await request_logging(request, call_next)
    assert str(UUID(response.headers["X-Request-ID"])) == response.headers["X-Request-ID"]
