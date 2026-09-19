import logging

import httpx
from fastapi import HTTPException
from pydantic import ValidationError

from app.core.config import settings
from app.schemas.assistant import ChatRequest, ChatResponse

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """You are Mr. Bloom, a concise and supportive planning assistant.
Reply in the user's language. Return only a JSON object with keys reply and draft.
The draft must be null unless the user asks to plan tasks for a day or create a long-term goal.
For a day plan, use draft {type:'today', availability:{start:'HH:MM',end:'HH:MM',totalHours:number},tasks:[{title,durationMin,priority:'Core'|'Optional'}]}.
Use only tasks the user mentioned. If availability or tasks are missing, ask for them and set draft to null. Do not invent tasks.
For a goal, use draft {type:'roadmap',goalTitle,goalDescription,targetDate:'YYYY-MM-DD',milestones:[{title,targetDate:'YYYY-MM-DD'}]}.
If a target date is missing, ask for it and set draft to null. Do not invent dates.
Keep the reply brief and never claim to have saved a draft or changed the user's schedule."""


async def chat(request: ChatRequest) -> ChatResponse:
    if not settings.GROQ_API_KEY or not settings.GROQ_API_KEY.get_secret_value().strip():
        raise HTTPException(status_code=503, detail="AI chat is not configured.")

    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        *[turn.model_dump() for turn in request.history[-12:]],
        {"role": "user", "content": request.message.strip()},
    ]
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                "https://api.groq.com/openai/v1/chat/completions",
                headers={"Authorization": f"Bearer {settings.GROQ_API_KEY.get_secret_value()}"},
                json={
                    "model": settings.GROQ_MODEL,
                    "messages": messages,
                    "response_format": {"type": "json_object"},
                    "temperature": 0.3,
                },
            )
            response.raise_for_status()
        content = response.json()["choices"][0]["message"]["content"]
        result = ChatResponse.model_validate_json(content)
        if not result.reply.strip():
            raise ValueError("empty reply")
        return result
    except (httpx.HTTPError, KeyError, IndexError, TypeError, ValueError, ValidationError) as exc:
        logger.warning("assistant_chat_failed: %s", type(exc).__name__)
        raise HTTPException(status_code=502, detail="Mr. Bloom is unavailable. Please try again.") from None
