import json
import logging
from typing import Dict, Any
import httpx
from app.core.config import settings
from app.models.ai_schemas import AIRequestContext, TodayAIInterpretation, RoadmapAIInterpretation
from app.services.ai_provider import AIProvider, AIProviderException, ProviderErrorCategory

logger = logging.getLogger(__name__)

class GeminiProvider(AIProvider):
    async def invoke(self, request_context: AIRequestContext) -> Dict[str, Any]:
        if not settings.GEMINI_API_KEY:
            raise AIProviderException(ProviderErrorCategory.CONFIGURATION_ERROR, "GEMINI_API_KEY is not configured.")
        
        api_key = settings.GEMINI_API_KEY.get_secret_value()
        
        if settings.AI_GATEWAY_URL:
            url = f"{settings.AI_GATEWAY_URL.rstrip('/')}/google-ai-studio/v1/models/{settings.GEMINI_MODEL}:generateContent"
        else:
            url = f"https://generativelanguage.googleapis.com/v1beta/models/{settings.GEMINI_MODEL}:generateContent"
        
        headers = {
            "Content-Type": "application/json",
            "x-goog-api-key": api_key
        }
        if settings.CF_AIG_TOKEN and settings.AI_GATEWAY_URL:
            headers["cf-aig-authorization"] = f"Bearer {settings.CF_AIG_TOKEN.get_secret_value()}"

        if request_context.context_type == "today_planning":
            schema = TodayAIInterpretation.model_json_schema()
        else:
            schema = RoadmapAIInterpretation.model_json_schema()


        system_instruction = (
            f"You are the Blooming AI planning assistant.\n"
            f"Current deterministic time: {request_context.current_time.isoformat()} "
            f"in timezone {request_context.timezone}.\n"
            f"Interpret relative dates/times against this current time.\n"
            f"If information is missing to make a sensible draft, return status='NEEDS_CLARIFICATION' and ask questions.\n"
            f"Do not hallucinate duration, deadline, dependency, or milestone dates.\n"
            f"Provide output matching the strictly required JSON schema.\n"
        )
        
        payload = {
            "systemInstruction": {
                "parts": [{"text": system_instruction}]
            },
            "contents": [
                {"role": "user", "parts": [{"text": request_context.user_input}]}
            ],
            "generationConfig": {
                "responseMimeType": "application/json",
                "responseJsonSchema": schema
            }
        }
        
        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(url, headers=headers, json=payload, timeout=8.0)
            except httpx.TimeoutException:
                raise AIProviderException(ProviderErrorCategory.TIMEOUT, "TIMEOUT")
            except httpx.RequestError as e:
                raise AIProviderException(ProviderErrorCategory.NETWORK_ERROR, "Network error")
                
            if response.status_code == 401 or response.status_code == 403:
                raise AIProviderException(ProviderErrorCategory.AUTH_ERROR, "Authentication failed")
            elif response.status_code == 429:
                raise AIProviderException(ProviderErrorCategory.RATE_LIMIT, "Rate limited")
            elif response.status_code >= 500:
                raise AIProviderException(ProviderErrorCategory.PROVIDER_5XX, f"Provider error: {response.status_code}")
            elif response.status_code >= 400:
                raise AIProviderException(ProviderErrorCategory.PROVIDER_4XX, f"Provider bad request: {response.status_code}")
                
            try:
                response.raise_for_status()
            except Exception as e:
                raise AIProviderException(ProviderErrorCategory.PROVIDER_5XX, f"Provider error: {response.status_code}")
                
            data = response.json()
            try:
                content = data["candidates"][0]["content"]["parts"][0]["text"]
                return json.loads(content)
            except Exception as e:
                raise AIProviderException(ProviderErrorCategory.MALFORMED_RESPONSE, f"Failed to parse response")
