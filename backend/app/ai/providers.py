import asyncio
import json
import logging
import time
from typing import Any, Dict, List, Optional
import httpx

from app.core.config import settings

logger = logging.getLogger(__name__)

class LLMError(Exception):
    def __init__(self, message: str, status_code: int = 500, retry_after: int = 0):
        super().__init__(message)
        self.status_code = status_code
        self.retry_after = retry_after

class RateLimitError(LLMError):
    pass

class CircuitBreakerOpenError(LLMError):
    pass

class CircuitBreaker:
    def __init__(self, failure_threshold: int = 3, cooldown_seconds: float = 60.0):
        self.failure_threshold = failure_threshold
        self.cooldown_seconds = cooldown_seconds
        self.failures = 0
        self.last_failure_time = 0.0
        self.state = "CLOSED"

    def record_failure(self):
        self.failures += 1
        self.last_failure_time = time.time()
        if self.failures >= self.failure_threshold:
            self.state = "OPEN"

    def record_success(self):
        self.failures = 0
        self.state = "CLOSED"

    def is_allowed(self) -> bool:
        if self.state == "CLOSED":
            return True
        if time.time() - self.last_failure_time >= self.cooldown_seconds:
            self.state = "HALF_OPEN"
            return True
        return False

class LLMProvider:
    def __init__(self):
        self.client: httpx.AsyncClient | None = None
        self.circuit_breakers: Dict[str, CircuitBreaker] = {}

    def init_client(self):
        if not self.client:
            self.client = httpx.AsyncClient(timeout=settings.AI_TIMEOUT_SECONDS)

    async def close_client(self):
        if self.client:
            await self.client.aclose()
            self.client = None

    def get_circuit_breaker(self, provider: str) -> CircuitBreaker:
        if provider not in self.circuit_breakers:
            self.circuit_breakers[provider] = CircuitBreaker()
        return self.circuit_breakers[provider]

    def parse_route(self, route_str: str) -> List[tuple[str, str]]:
        routes = []
        for p in route_str.split(","):
            parts = p.split(":", 1)
            if len(parts) == 2:
                routes.append((parts[0], parts[1]))
        return routes

    def _get_base_url_and_headers(self, provider: str) -> tuple[str, dict]:
        if provider == "groq":
            api_key = settings.GROQ_API_KEY.get_secret_value() if settings.GROQ_API_KEY else ""
            return "https://api.groq.com/openai/v1", {"Authorization": f"Bearer {api_key}"}
        elif provider == "ollama":
            return settings.OLLAMA_BASE_URL, {}
        raise ValueError(f"Unknown provider: {provider}")

    async def _call_single(
        self,
        provider: str,
        model: str,
        messages: list[dict],
        temperature: float,
        max_tokens: int,
        response_format: Optional[dict] = None
    ) -> dict:
        cb = self.get_circuit_breaker(provider)
        if not cb.is_allowed():
            raise CircuitBreakerOpenError(f"Circuit breaker open for {provider}")

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
        
        # Use o1 reasoning effort if applicable (only for gpt-oss-120b for example)
        if "o1" in model or "o3" in model:
            payload["reasoning_effort"] = "low"

        start_time = time.time()
        try:
            if not self.client:
                self.init_client()
            
            response = await self.client.post(url, headers=headers, json=payload)
            latency = int((time.time() - start_time) * 1000)
            
            if response.status_code == 429:
                retry_after = int(response.headers.get("Retry-After", 60))
                cb.record_failure()
                logger.warning(f"Rate limited by {provider}, retry_after={retry_after}")
                raise RateLimitError("Rate limited", status_code=429, retry_after=retry_after)
                
            response.raise_for_status()
            
            cb.record_success()
            data = response.json()
            
            # Privacy safe logging
            logger.info(f"AI call success: provider={provider} model={model} latency={latency}ms "
                       f"prompt_tokens={data.get('usage', {}).get('prompt_tokens', 0)} "
                       f"completion_tokens={data.get('usage', {}).get('completion_tokens', 0)}")
            
            return data
            
        except httpx.TimeoutException:
            cb.record_failure()
            logger.error(f"Timeout calling {provider}")
            raise LLMError("Timeout", status_code=504)
        except httpx.HTTPStatusError as e:
            cb.record_failure()
            logger.error(f"HTTP error from {provider}: {e.response.status_code}")
            raise LLMError("Provider HTTP error", status_code=e.response.status_code)
        except Exception as e:
            cb.record_failure()
            if isinstance(e, LLMError):
                raise
            logger.error(f"Unexpected error calling {provider}: {str(e)}")
            raise LLMError("Internal error calling provider")

    async def call(
        self,
        route_str: str,
        messages: list[dict],
        temperature: float = 0.0,
        max_tokens: int = 1000,
        require_json: bool = False,
        json_schema: Optional[dict] = None
    ) -> dict:
        routes = self.parse_route(route_str)
        last_error = None
        
        for provider, model in routes:
            response_format = None
            if require_json:
                if json_schema and any(strict_model in model for strict_model in settings.AI_STRICT_MODELS):
                    response_format = {
                        "type": "json_schema",
                        "json_schema": {
                            "name": "structured_output",
                            "strict": True,
                            "schema": json_schema
                        }
                    }
                else:
                    response_format = {"type": "json_object"}

            try:
                return await self._call_single(
                    provider, model, messages, temperature, max_tokens, response_format
                )
            except LLMError as e:
                last_error = e
                # Only fallback if it's not a rate limit with long wait, or just log and continue
                logger.warning(f"Provider {provider}/{model} failed, falling back. Error: {e}")
                continue

        if last_error:
            raise last_error
        raise LLMError("No valid routes configured")

llm_provider = LLMProvider()
