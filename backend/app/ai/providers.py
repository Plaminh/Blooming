import json
import logging
import time
from copy import deepcopy
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
from typing import TYPE_CHECKING, Any, Dict, List, Optional
from uuid import UUID

import httpx

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings

logger = logging.getLogger(__name__)


def strictify_schema(schema: dict) -> dict:
    """Make Pydantic's schema suitable for strict structured output.

    Keep the local Pydantic model as the authority for constraints omitted from
    the provider's smaller JSON Schema dialect.
    """
    result = deepcopy(schema)

    def visit(node: Any) -> None:
        if isinstance(node, list):
            for item in node:
                visit(item)
            return
        if not isinstance(node, dict):
            return
        for key in ("title", "default", "examples", "minLength", "maxLength",
                    "pattern", "minimum", "maximum", "minItems", "maxItems"):
            node.pop(key, None)
        if "prefixItems" in node:
            # Fixed tuples are validated by Pydantic after the response arrives.
            items = node.pop("prefixItems")
            node["items"] = items[0] if len(items) == 1 else {"anyOf": items}
        if node.get("type") == "object" or "properties" in node:
            properties = node.get("properties", {})
            node["required"] = list(properties)
            node["additionalProperties"] = False
        for key, value in node.items():
            if key in {"properties", "$defs"} and isinstance(value, dict):
                for child_schema in value.values():
                    visit(child_schema)
            else:
                visit(value)

    visit(result)
    return result


class LLMError(Exception):
    def __init__(self, message: str, status_code: int = 500, retry_after: float = 0):
        super().__init__(message)
        self.status_code = status_code
        self.retry_after = retry_after


class RateLimitError(LLMError):
    pass


class CircuitBreakerOpenError(LLMError):
    def __init__(self):
        super().__init__("budget", status_code=429)


class CircuitBreaker:
    def __init__(
        self, failure_threshold: int = 3, cooldown_seconds: float = 60.0, clock=None
    ):
        self.failure_threshold = failure_threshold
        self.cooldown_seconds = cooldown_seconds
        self.clock = clock or time.monotonic
        self.failures = 0
        self.open_until = 0.0
        self.state = "CLOSED"

    def record_failure(self, retry_after: float = 0):
        self.failures += 1
        cooldown = retry_after or (
            self.cooldown_seconds if self.failures >= self.failure_threshold else 0
        )
        if cooldown:
            self.open_until = self.clock() + cooldown
            self.state = "OPEN"

    def record_success(self):
        self.failures = 0
        self.open_until = 0.0
        self.state = "CLOSED"

    def is_allowed(self) -> bool:
        if self.state == "CLOSED":
            return True
        if self.clock() >= self.open_until:
            self.state = "HALF_OPEN"
            return True
        return False


def parse_retry_after(value: str | None) -> float:
    if not value:
        return 60.0
    try:
        seconds = float(value)
    except ValueError:
        try:
            seconds = (
                parsedate_to_datetime(value) - datetime.now(timezone.utc)
            ).total_seconds()
        except (TypeError, ValueError, OverflowError):
            return 60.0
    return min(900.0, max(0.0, seconds))


class LLMProvider:
    def __init__(self, client: httpx.AsyncClient | None = None):
        self.client: httpx.AsyncClient | None = client
        self.circuit_breakers: Dict[tuple[str, str], CircuitBreaker] = {}
        self.last_usage: dict = {}
        self.last_latency_ms: int = 0

    def init_client(self):
        if not self.client:
            self.client = httpx.AsyncClient(timeout=settings.AI_TIMEOUT_SECONDS)

    async def close_client(self):
        if self.client:
            await self.client.aclose()
            self.client = None

    def get_circuit_breaker(self, provider: str, model: str) -> CircuitBreaker:
        return self.circuit_breakers.setdefault((provider, model), CircuitBreaker())

    def parse_route(self, route_str: str) -> List[tuple[str, str]]:
        routes = []
        for p in route_str.split(","):
            if not p.strip():
                continue
            parts = [part.strip() for part in p.split(":", 1)]
            if len(parts) != 2 or parts[0] not in {"groq", "ollama"} or not parts[1]:
                raise LLMError("config", status_code=503)
            routes.append((parts[0], parts[1]))
        if not routes:
            raise LLMError("config", status_code=503)
        return routes

    def _get_base_url_and_headers(self, provider: str) -> tuple[str, dict]:
        if provider == "groq":
            api_key = (
                settings.GROQ_API_KEY.get_secret_value()
                if settings.GROQ_API_KEY
                else ""
            )
            if not api_key.strip() or api_key == "your_groq_api_key_here":
                raise LLMError("config", status_code=503)
            return settings.GROQ_BASE_URL.rstrip("/"), {
                "Authorization": f"Bearer {api_key}"
            }
        elif provider == "ollama":
            return settings.OLLAMA_BASE_URL.rstrip("/"), {}
        raise LLMError("config", status_code=503)

    async def _call_single(
        self,
        provider: str,
        model: str,
        messages: list[dict],
        temperature: float,
        max_tokens: int,
        response_format: Optional[dict] = None,
    ) -> dict:
        cb = self.get_circuit_breaker(provider, model)
        if not cb.is_allowed():
            raise CircuitBreakerOpenError()

        base_url, headers = self._get_base_url_and_headers(provider)
        url = f"{base_url}/chat/completions"

        payload: dict[str, Any] = {
            "model": model,
            "messages": messages,
            "temperature": temperature,
            "max_completion_tokens" if provider == "groq" else "max_tokens": max_tokens,
        }

        if response_format:
            payload["response_format"] = response_format

        if provider == "groq" and model.startswith("openai/gpt-oss"):
            payload["reasoning_effort"] = "low"

        start_time = time.monotonic()
        try:
            if not self.client:
                self.init_client()
            assert self.client is not None
            response = await self.client.post(url, headers=headers, json=payload)
            latency = int((time.monotonic() - start_time) * 1000)

            if response.status_code == 429:
                retry_after = parse_retry_after(response.headers.get("Retry-After"))
                cb.record_failure(retry_after)
                logger.warning(f"Rate limited by {provider}, retry_after={retry_after}")
                raise RateLimitError(
                    "rate_limit", status_code=429, retry_after=retry_after
                )

            response.raise_for_status()

            data = response.json()
            if not isinstance(data, dict):
                raise ValueError("invalid response envelope")

            usage = data.get("usage") or {}
            if not isinstance(usage, dict):
                usage = {}
            prompt_tokens = usage.get("prompt_tokens", 0)
            completion_tokens = usage.get("completion_tokens", 0)
            logger.info(
                "AI transport success: provider=%s model=%s latency=%sms prompt_tokens=%s completion_tokens=%s",
                provider,
                model,
                latency,
                prompt_tokens if isinstance(prompt_tokens, int) else 0,
                completion_tokens if isinstance(completion_tokens, int) else 0,
            )

            cb.record_success()
            return data

        except httpx.TimeoutException:
            cb.record_failure()
            logger.error(f"Timeout calling {provider}")
            raise LLMError("timeout", status_code=504)
        except httpx.HTTPStatusError as e:
            if e.response.status_code >= 500:
                cb.record_failure()
            logger.error(f"HTTP error from {provider}: {e.response.status_code}")
            raise LLMError(
                "upstream" if e.response.status_code >= 500 else "config",
                status_code=e.response.status_code,
            ) from None
        except httpx.RequestError:
            cb.record_failure()
            logger.error("Transport error calling %s", provider)
            raise LLMError("upstream") from None
        except (ValueError, TypeError):
            logger.error("Invalid response from %s", provider)
            raise LLMError("bad_output") from None

    async def call(
        self,
        route_str: str,
        messages: list[dict],
        temperature: float = 0.0,
        max_tokens: int = 1000,
        require_json: bool = False,
        json_schema: Optional[dict] = None,
        *,
        db: "AsyncSession | None" = None,
        user_id: UUID | None = None,
        purpose: str = "PLANNER",
    ) -> dict:
        routes = self.parse_route(route_str)
        last_error = None

        for provider, model in routes:
            response_format = None
            request_messages = messages
            if require_json:
                if (
                    json_schema
                    and provider == "groq"
                    and model in settings.AI_STRICT_MODELS
                ):
                    response_format = {
                        "type": "json_schema",
                        "json_schema": {
                            "name": "structured_output",
                            "strict": True,
                            "schema": strictify_schema(json_schema),
                        },
                    }
                else:
                    response_format = {"type": "json_object"}
                    if json_schema:
                        request_messages = [
                            {
                                "role": "system",
                                "content": "Return JSON matching this schema: "
                                + json.dumps(json_schema),
                            },
                            *messages,
                        ]

            try:
                started = time.monotonic()
                result = await self._call_single(
                    provider,
                    model,
                    request_messages,
                    temperature,
                    max_tokens,
                    response_format,
                )
                if require_json:
                    try:
                        parsed = json.loads(result["choices"][0]["message"]["content"])
                        if not isinstance(parsed, dict):
                            raise ValueError("JSON object required")
                        response_value = parsed
                    except (KeyError, IndexError, TypeError, ValueError):
                        logger.warning(
                            "AI bad_output provider=%s model=%s", provider, model
                        )
                        raise LLMError("bad_output") from None
                else:
                    response_value = result
                if db is not None:
                    from app.ai.budget import record_usage

                    usage = result.get("usage") if isinstance(result, dict) else {}
                    usage = usage if isinstance(usage, dict) else {}
                    await record_usage(
                        db,
                        user_id=user_id,
                        purpose=purpose,
                        provider=provider,
                        model=model,
                        prompt_tokens=usage.get("prompt_tokens", 0),
                        completion_tokens=usage.get("completion_tokens", 0),
                        latency_ms=int((time.monotonic() - started) * 1000),
                        outcome="OK",
                    )
                self.last_usage = result.get("usage", {}) if isinstance(result, dict) else {}
                self.last_latency_ms = int((time.monotonic() - started) * 1000)
                return response_value
            except LLMError as e:
                if db is not None:
                    from app.ai.budget import record_usage

                    await record_usage(
                        db,
                        user_id=user_id,
                        purpose=purpose,
                        provider=provider,
                        model=model,
                        latency_ms=int((time.monotonic() - started) * 1000),
                        outcome={
                            "rate_limit": "RATE_LIMITED",
                            "bad_output": "BAD_OUTPUT",
                        }.get(str(e), "ERROR"),
                    )
                last_error = e
                logger.warning(
                    "Provider %s/%s failed: %s", provider, model, type(e).__name__
                )
                if str(e) in {"rate_limit", "upstream", "timeout", "budget"}:
                    continue
                raise

        if last_error:
            raise last_error
        raise LLMError("No valid routes configured")


llm_provider = LLMProvider()
