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


ai_client: httpx.AsyncClient | None = None

def init_ai_client():
    global ai_client
    if ai_client is None:
        ai_client = httpx.AsyncClient(timeout=settings.AI_TIMEOUT_SECONDS)

async def close_ai_client():
    global ai_client
    if ai_client is not None:
        await ai_client.aclose()
        ai_client = None

async def _call_llm(messages: list[dict], model: str) -> dict:
    payload = {
        "model": model,
        "messages": messages,
        "temperature": 0.3,
        "max_completion_tokens": 2048,
    }

    if "gpt-" in model.lower() or "o1-" in model.lower() or "o3-" in model.lower():
        payload["response_format"] = {
            "type": "json_schema",
            "json_schema": {
                "name": "ChatResponse",
                "strict": True,
                "schema": ChatResponse.model_json_schema()
            }
        }
    else:
        payload["response_format"] = {"type": "json_object"}

    if "o1-" in model.lower() or "o3-" in model.lower():
        payload["reasoning_effort"] = "low"
        payload.pop("temperature", None)

    try:
        response = await ai_client.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers={"Authorization": f"Bearer {settings.GROQ_API_KEY.get_secret_value()}"},
            json=payload,
        )
        response.raise_for_status()
        import json as jsonlib
        content = response.json()["choices"][0]["message"]["content"]
        return jsonlib.loads(content)
    except httpx.HTTPStatusError as exc:
        status = exc.response.status_code
        logger.warning("assistant_chat_failed: %s status=%s", type(exc).__name__, status)
        if status == 429:
            raise HTTPException(status_code=429, detail="rate_limit") from None
        raise HTTPException(status_code=502, detail="upstream_error") from None
    except httpx.TimeoutException as exc:
        logger.warning("assistant_chat_failed: %s", type(exc).__name__)
        raise HTTPException(status_code=504, detail="timeout") from None
    except (httpx.RequestError, KeyError, IndexError, TypeError, ValueError) as exc:
        logger.warning("assistant_chat_failed: %s", type(exc).__name__)
        raise HTTPException(status_code=502, detail="bad_output") from None

async def chat(request: ChatRequest, timezone: str = "UTC") -> ChatResponse:
    if not settings.GROQ_API_KEY or not settings.GROQ_API_KEY.get_secret_value().strip():
        raise HTTPException(status_code=503, detail="config")

    if ai_client is None:
        init_ai_client()

    import zoneinfo
    from datetime import datetime
    import uuid
    from app.schemas.drafts import clean_availability_windows

    try:
        tz = zoneinfo.ZoneInfo(timezone)
    except Exception:
        tz = zoneinfo.ZoneInfo("UTC")
    
    now = datetime.now(tz)
    local_time_str = now.strftime("%Y-%m-%d %H:%M:%S")

    system_prompt_with_time = f"{SYSTEM_PROMPT}\nCurrent local time is: {local_time_str}, Timezone: {timezone}"

    messages = [
        {"role": "system", "content": system_prompt_with_time},
        *[turn.model_dump() for turn in request.history[-12:]],
        {"role": "user", "content": request.message.strip()},
    ]
    model = "llama3-70b-8192"

    parsed = await _call_llm(messages, model)
    reply = parsed.get("reply", "").strip()
    if not reply:
        raise HTTPException(status_code=502, detail="bad_output")
    
    draft = parsed.get("draft")
    if not draft:
        logger.info("assistant_chat_success", extra={"model": model})
        return ChatResponse(reply=reply, draft=None)
    
    def apply_deterministic_fields(parsed_draft):
        if parsed_draft.get("type") == "today":
            parsed_draft["timezone"] = timezone
            
    apply_deterministic_fields(draft)
    
    try:
        result = ChatResponse.model_validate(parsed)
        if result.draft:
            if getattr(result.draft, "type", None) == "today":
                if hasattr(result.draft, "windows"):
                    result.draft.windows = clean_availability_windows(result.draft.windows, now)
                elif hasattr(result.draft, "availability"):
                    # Mock or ChatTodayDraft
                    pass
                
                if hasattr(result.draft, "tasks"):
                    for task in result.draft.tasks:
                        if hasattr(task, "id"):
                            task.id = str(uuid.uuid4())
            elif getattr(result.draft, "type", None) == "roadmap":
                for milestone in result.draft.milestones:
                    if hasattr(milestone, "id"):
                        milestone.id = str(uuid.uuid4())
        logger.info("assistant_chat_success", extra={"model": model})
        return result
    except ValidationError as exc:
        logger.warning("assistant_draft_invalid, attempting repair: %s", exc)
        repair_messages = messages + [
            {"role": "assistant", "content": str(parsed)},
            {"role": "user", "content": f"The draft was invalid: {exc.errors()}. Please fix the draft. Maintain the exact same reply text."}
        ]
        try:
            repaired_parsed = await _call_llm(repair_messages, model)
            repaired_draft = repaired_parsed.get("draft")
            if repaired_draft:
                apply_deterministic_fields(repaired_draft)
            result = ChatResponse.model_validate(repaired_parsed)
            if result.draft:
                if getattr(result.draft, "type", None) == "today":
                    if hasattr(result.draft, "windows"):
                        result.draft.windows = clean_availability_windows(result.draft.windows, now)
                    if hasattr(result.draft, "tasks"):
                        for task in result.draft.tasks:
                            if hasattr(task, "id"):
                                task.id = str(uuid.uuid4())
                elif getattr(result.draft, "type", None) == "roadmap":
                    for milestone in result.draft.milestones:
                        if hasattr(milestone, "id"):
                            milestone.id = str(uuid.uuid4())
            logger.info("assistant_chat_success", extra={"model": model})
            return result
        except (HTTPException, ValidationError) as repair_exc:
            logger.warning("assistant_draft_repair_failed: %s", repair_exc)
            clarification = "\n\n(I had some trouble building the schedule. Could you clarify the details?)"
            return ChatResponse(reply=reply + clarification, draft=None)
