from datetime import datetime, timezone, timedelta
import logging
from uuid import UUID

from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.repositories.assistant import assistant_repo
from app.ai.nlu.router import route
from app.ai.llm.providers import llm_deadline
from app.schemas.assistant import ChatRequest, ChatResponse
from app.services.assistant_service import chat

logger = logging.getLogger(__name__)


async def process_chat(
    request: ChatRequest, db: AsyncSession, user_id: UUID
) -> ChatResponse:
    is_rate_limited = await assistant_repo.check_rate_limit(
        db, user_id, settings.AI_CHAT_RATE_LIMIT_PER_MIN
    )
    if is_rate_limited:
        raise HTTPException(
            status_code=429,
            detail={
                "code": "RATE_LIMIT",
                "message": "You are sending messages too quickly. Please retry shortly.",
            },
            headers={"Retry-After": "60"},
        )

    initial = route(request.message, has_draft=request.current_draft is not None)
    session_type = (
        "ROADMAP"
        if initial.intent == "CREATE_GOAL"
        else "PLAN_EDIT"
        if initial.intent == "EDIT_DRAFT"
        else "DAILY_PLAN"
    )

    conversation = None
    if request.session_id:
        try:
            session_id = UUID(request.session_id)
        except ValueError:
            raise HTTPException(status_code=422, detail="invalid_session_id")

        value = await assistant_repo.get_session_by_id(db, user_id, session_id)
        if value is None:
            raise HTTPException(status_code=404, detail="session_not_found")
        if value.status in {"COMPLETED", "CANCELLED"}:
            raise HTTPException(status_code=409, detail="session_closed")
        if value.updated_at and datetime.now(
            timezone.utc
        ) - value.updated_at > timedelta(hours=12):
            value.status = "CANCELLED"
            value.closed_at = datetime.now(timezone.utc)
        else:
            conversation = value

    if not conversation:
        conversation = await assistant_repo.create_session(db, user_id, session_type)

    await assistant_repo.add_message(
        db, conversation.id, "USER", request.message.strip()
    )
    await db.commit()

    recent = await assistant_repo.get_recent_messages(db, conversation.id, limit=12)
    history = [
        {"role": item.role.lower(), "content": item.content}
        for item in reversed(recent)
        if item.role in {"USER", "ASSISTANT"}
    ]
    if history and history[-1]["role"] == "user":
        history.pop()

    pending_message = None
    if conversation.pending_intent:
        chronological = list(reversed(recent))
        for index in range(len(chronological) - 1, -1, -1):
            item = chronological[index]
            if item.role == "ASSISTANT" and (item.structured_payload or {}).get(
                "question"
            ):
                pending_message = next(
                    (
                        previous.content
                        for previous in reversed(chronological[:index])
                        if previous.role == "USER"
                    ),
                    None,
                )
                break

    user_settings = await assistant_repo.get_user_settings(db, user_id)
    timezone_name = user_settings.timezone if user_settings else "UTC"

    with llm_deadline(settings.AI_REQUEST_BUDGET_SECONDS):
        response = await chat(
            request,
            timezone=timezone_name,
            db=db,
            user_id=user_id,
            history=history[-4:],
            pending_intent=conversation.pending_intent,
            pending_message=pending_message,
        )

    response.session_id = str(conversation.id)
    logger.info(
        "assistant_response",
        extra={
            "correlation_id": str(conversation.id),
            "intent": response.intent,
            "tier": response.tier,
            "mode": response.degraded or "NORMAL",
            "outcome": "OK",
        },
    )

    payload = response.model_dump(mode="json", exclude={"reply", "session_id"})
    await assistant_repo.add_message(
        db, conversation.id, "ASSISTANT", response.reply, payload
    )

    non_mutating_interlude = response.intent in {
        "GREETING",
        "THANKS",
        "STATUS_TODAY",
        "STATUS_GARDEN",
        "STATUS_STATS",
        "STATUS_GOALS",
        "STATUS_RECURRING",
        "HELP_FEATURE",
        "CHITCHAT",
    }
    if conversation.pending_intent and non_mutating_interlude:
        conversation.status = "AWAITING_CLARIFICATION"
    else:
        conversation.status = "AWAITING_CLARIFICATION" if response.question else "OPEN"
        conversation.pending_intent = response.intent if response.question else None
    conversation.updated_at = datetime.now(timezone.utc)

    await db.commit()
    return response


from app.schemas.assistant import SessionResponse, SessionMessage
from app.schemas.drafts import TodayDraft
from app.services.today_service import today_service


async def get_session_response(
    db: AsyncSession, user_id: UUID, value
) -> SessionResponse:
    messages = sorted(value.messages, key=lambda item: (item.created_at, str(item.id)))
    safe_messages: list[SessionMessage] = []
    for item in messages:
        if item.role not in {"USER", "ASSISTANT"}:
            continue
        payload = dict(item.structured_payload) if item.structured_payload else None
        if payload and payload.get("preview") and payload.get("draft"):
            try:
                draft = TodayDraft.model_validate(payload["draft"])
                token = str(payload["preview"].get("preview_token", ""))
                claims = today_service._preview_token_claims(
                    user_id, draft.model_dump_json(), token
                )
                plan = await today_service._get_plan_for_preview_validation(
                    db, user_id, draft.planDate
                )
                current_version = await today_service._plan_version(
                    db, plan.id if plan is not None else None
                )
                if claims is None or claims["plan_version"] != current_version:
                    payload.pop("preview", None)
            except (TypeError, ValueError):
                payload.pop("preview", None)
        safe_messages.append(
            SessionMessage(
                role=item.role.lower(),
                content=item.content,
                structured_payload=payload,
                created_at=item.created_at,
            )
        )
    return SessionResponse(
        session_id=str(value.id),
        status=value.status,
        messages=safe_messages,
    )


async def get_latest_session(db: AsyncSession, user_id: UUID) -> SessionResponse:
    value = await assistant_repo.get_latest_session(db, user_id)
    if value is None:
        raise HTTPException(status_code=404, detail="session_not_found")
    return await get_session_response(db, user_id, value)


async def get_session(
    db: AsyncSession, user_id: UUID, session_id: UUID
) -> SessionResponse:
    value = await assistant_repo.get_session(db, session_id, user_id)
    if value is None:
        raise HTTPException(status_code=404, detail="session_not_found")
    return await get_session_response(db, user_id, value)


from app.schemas.patches import ApplyPatchRequest, ApplyPatchResponse
from app.ai.drafting.patches import apply_patch
from app.schemas.today import TodayPreviewRequest


async def process_apply_patch(
    request: ApplyPatchRequest, db: AsyncSession, user_id: UUID
) -> ApplyPatchResponse:
    try:
        draft = apply_patch(request.draft, request.ops)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from None
    preview = None
    if isinstance(draft, TodayDraft):
        preview_value = await today_service.preview_today_draft(
            db,
            user_id,
            TodayPreviewRequest(draft=draft),
        )
        preview = preview_value.model_dump(mode="json")
    return ApplyPatchResponse(draft=draft, preview=preview)


async def process_action(name: str, db: AsyncSession, user_id: UUID):
    if name == "REPLAN_TODAY":
        result = await today_service.replan_today(db, user_id, commit=False)
        await db.commit()
        return result
    if name != "SKIP_OPTIONAL_TODAY":
        raise HTTPException(status_code=404, detail="unknown_action")
    today = await today_service.get_today(db, user_id)
    task_ids = [
        block["task_id"]
        for block in today.get("blocks", [])
        if block.get("task_id")
        and block.get("status") not in {"COMPLETED", "SKIPPED", "CANCELLED"}
    ]
    if task_ids:
        tasks = await assistant_repo.get_optional_tasks(db, user_id, task_ids)
        from app.schemas.today import TodayTaskStatusUpdate

        for task in tasks:
            await today_service.update_task_status_from_today(
                db,
                user_id,
                task.id,
                TodayTaskStatusUpdate(status="SKIPPED"),
                commit=False,
            )
    result = await today_service.replan_today(db, user_id, commit=False)
    await db.commit()
    return result


from app.core.time_utils import safe_timezone
from app.ai.coach.proactive import nudge_gate


async def process_event(body: dict, db: AsyncSession, user_id: UUID):
    event_id = str(body.get("event_id", ""))[:100]
    event_name = str(body.get("event_name", ""))
    if not event_id or event_name not in {
        "NEED_MORE_TIME",
        "SKIP",
        "BEHIND_SCHEDULE",
        "MORNING_NO_PLAN",
    }:
        raise HTTPException(status_code=422, detail="invalid_event")
    user_settings = await assistant_repo.get_user_settings(db, user_id)
    tz = safe_timezone(user_settings.timezone if user_settings else "UTC")
    local_now = datetime.now(timezone.utc).astimezone(tz)
    consecutive_count = None
    if event_name in {"NEED_MORE_TIME", "SKIP"}:
        if not event_id.startswith("focus-"):
            raise HTTPException(status_code=422, detail="invalid_focus_event")
        try:
            run_id = UUID(event_id[6:])
        except ValueError:
            raise HTTPException(status_code=422, detail="invalid_focus_event") from None
        outcomes = await assistant_repo.get_recent_focus_outcomes(db, user_id, limit=2)
        if (
            not outcomes
            or outcomes[0].id != run_id
            or outcomes[0].outcome != event_name
        ):
            raise HTTPException(status_code=422, detail="invalid_focus_event")
        consecutive_count = sum(item.outcome == event_name for item in outcomes)
    if event_name == "MORNING_NO_PLAN":
        today = await today_service.get_today(db, user_id, local_now.date())
        if today["status"] != "NO_PLAN":
            return {"nudge": None}
    nudge = nudge_gate.evaluate(
        user_id=user_id,
        event_id=event_id,
        event_name=event_name,
        local_now=local_now,
        quiet_start=user_settings.quiet_hours_start if user_settings else None,
        quiet_end=user_settings.quiet_hours_end if user_settings else None,
        quiet_enabled=bool(user_settings and user_settings.quiet_hours_enabled),
        consecutive_count=consecutive_count,
    )
    return {"nudge": nudge}
