from datetime import datetime, timedelta, timezone
import logging
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.ai.patches import apply_patch
from app.schemas.patches import ApplyPatchRequest, ApplyPatchResponse
from app.ai.proactive import nudge_gate
from app.ai.providers import llm_deadline
from app.api.deps import CurrentUser, get_db_session
from app.core.config import settings
from app.core.time_utils import safe_timezone
from app.db.models.planning import PlanningMessage, PlanningSession
from app.db.models.users import UserSettings
from app.db.models.users import User
from app.schemas.assistant import (
    ChatRequest,
    ChatResponse,
    SessionMessage,
    SessionResponse,
)
from app.schemas.drafts import TodayDraft
from app.schemas.today import TodayPreviewRequest
from app.services.assistant_service import chat
from app.services.today_service import today_service

router = APIRouter(prefix="/assistant", tags=["assistant"])
logger = logging.getLogger(__name__)


async def _planning_session(
    db: AsyncSession,
    user_id: UUID,
    requested_id: str | None,
    session_type: str = "DAILY_PLAN",
) -> PlanningSession:
    if requested_id:
        try:
            session_id = UUID(requested_id)
        except ValueError:
            raise HTTPException(status_code=422, detail="invalid_session_id") from None
        value = await db.scalar(
            select(PlanningSession).where(
                PlanningSession.id == session_id,
                PlanningSession.user_id == user_id,
            )
        )
        if value is None:
            raise HTTPException(status_code=404, detail="session_not_found")
        if value.status in {"COMPLETED", "CANCELLED"}:
            raise HTTPException(status_code=409, detail="session_closed")
        if value.updated_at and datetime.now(
            timezone.utc
        ) - value.updated_at > timedelta(hours=12):
            value.status = "CANCELLED"
            value.closed_at = datetime.now(timezone.utc)
            requested_id = None
        else:
            return value
    value = PlanningSession(user_id=user_id, session_type=session_type, status="OPEN")
    db.add(value)
    await db.flush()
    return value


@router.post("/chat", response_model=ChatResponse)
async def assistant_chat(
    request: ChatRequest,
    current_user: CurrentUser,
    session: AsyncSession = Depends(get_db_session),
) -> ChatResponse:
    # Serialize and count persisted user messages so the limit is shared by
    # every API worker rather than existing only in one process's memory.
    now = datetime.now(timezone.utc)
    await session.execute(
        select(User.id).where(User.id == current_user.id).with_for_update()
    )
    recent_count = await session.scalar(
        select(func.count(PlanningMessage.id))
        .join(
            PlanningSession, PlanningSession.id == PlanningMessage.planning_session_id
        )
        .where(
            PlanningSession.user_id == current_user.id,
            PlanningMessage.role == "USER",
            PlanningMessage.created_at > now - timedelta(seconds=60),
        )
    )
    if int(recent_count or 0) >= settings.AI_CHAT_RATE_LIMIT_PER_MIN:
        raise HTTPException(
            status_code=429,
            detail={
                "code": "RATE_LIMIT",
                "message": "You are sending messages too quickly. Please retry shortly.",
            },
            headers={"Retry-After": "60"},
        )
    from app.ai.router import route

    initial = route(request.message, has_draft=request.current_draft is not None)
    session_type = (
        "ROADMAP"
        if initial.intent == "CREATE_GOAL"
        else "PLAN_EDIT"
        if initial.intent == "EDIT_DRAFT"
        else "DAILY_PLAN"
    )
    conversation = await _planning_session(
        session, current_user.id, request.session_id, session_type
    )
    session.add(
        PlanningMessage(
            planning_session_id=conversation.id,
            role="USER",
            content=request.message.strip(),
        )
    )
    await session.commit()  # Persist input before any provider wait.
    recent = (
        await session.scalars(
            select(PlanningMessage)
            .where(PlanningMessage.planning_session_id == conversation.id)
            .order_by(PlanningMessage.created_at.desc(), PlanningMessage.id.desc())
            .limit(12)
        )
    ).all()
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
    user_settings = await session.scalar(
        select(UserSettings).where(UserSettings.user_id == current_user.id)
    )
    timezone_name = user_settings.timezone if user_settings else "UTC"
    with llm_deadline(settings.AI_REQUEST_BUDGET_SECONDS):
        response = await chat(
            request,
            timezone=timezone_name,
            db=session,
            user_id=current_user.id,
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
    session.add(
        PlanningMessage(
            planning_session_id=conversation.id,
            role="ASSISTANT",
            content=response.reply,
            structured_payload=payload,
        )
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
    await session.commit()
    return response


async def _session_response(
    value: PlanningSession, db: AsyncSession, user_id: UUID
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
                role=item.role.lower(),  # type: ignore[arg-type]
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


@router.get("/sessions/latest", response_model=SessionResponse)
async def get_latest_assistant_session(
    current_user: CurrentUser,
    session: AsyncSession = Depends(get_db_session),
) -> SessionResponse:
    value = await session.scalar(
        select(PlanningSession)
        .options(selectinload(PlanningSession.messages))
        .where(
            PlanningSession.user_id == current_user.id,
            PlanningSession.status.in_({"OPEN", "AWAITING_CLARIFICATION"}),
            PlanningSession.updated_at
            >= datetime.now(timezone.utc) - timedelta(hours=12),
        )
        .order_by(PlanningSession.updated_at.desc(), PlanningSession.created_at.desc())
        .limit(1)
    )
    if value is None:
        raise HTTPException(status_code=404, detail="session_not_found")
    return await _session_response(value, session, current_user.id)


@router.get("/sessions/{session_id}", response_model=SessionResponse)
async def get_assistant_session(
    session_id: UUID,
    current_user: CurrentUser,
    session: AsyncSession = Depends(get_db_session),
) -> SessionResponse:
    value = await session.scalar(
        select(PlanningSession)
        .options(selectinload(PlanningSession.messages))
        .where(
            PlanningSession.id == session_id,
            PlanningSession.user_id == current_user.id,
        )
    )
    if value is None:
        raise HTTPException(status_code=404, detail="session_not_found")
    return await _session_response(value, session, current_user.id)


@router.post("/apply-patch", response_model=ApplyPatchResponse)
async def apply_draft_patch(
    request: ApplyPatchRequest,
    current_user: CurrentUser,
    session: AsyncSession = Depends(get_db_session),
) -> ApplyPatchResponse:
    try:
        draft = apply_patch(request.draft, request.ops)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from None
    preview = None
    if isinstance(draft, TodayDraft):
        preview_value = await today_service.preview_today_draft(
            session,
            current_user.id,
            TodayPreviewRequest(draft=draft),
        )
        preview = preview_value.model_dump(mode="json")
    return ApplyPatchResponse(draft=draft, preview=preview)


@router.post("/actions/{name}")
async def assistant_action(
    name: str,
    current_user: CurrentUser,
    session: AsyncSession = Depends(get_db_session),
):
    if name == "REPLAN_TODAY":
        result = await today_service.replan_today(
            session, current_user.id, commit=False
        )
        await session.commit()
        return result
    if name != "SKIP_OPTIONAL_TODAY":
        raise HTTPException(status_code=404, detail="unknown_action")
    today = await today_service.get_today(session, current_user.id)
    task_ids = [
        block["task_id"]
        for block in today.get("blocks", [])
        if block.get("task_id")
        and block.get("status") not in {"COMPLETED", "SKIPPED", "CANCELLED"}
    ]
    if task_ids:
        from app.db.models.tasks import Task

        tasks = (
            await session.scalars(
                select(Task).where(
                    Task.id.in_(task_ids),
                    Task.user_id == current_user.id,
                    Task.importance == "OPTIONAL",
                )
            )
        ).all()
        from app.schemas.today import TodayTaskStatusUpdate

        for task in tasks:
            await today_service.update_task_status_from_today(
                session,
                current_user.id,
                task.id,
                TodayTaskStatusUpdate(status="SKIPPED"),
                commit=False,
            )
    result = await today_service.replan_today(session, current_user.id, commit=False)
    await session.commit()
    return result


@router.post("/events")
async def assistant_event(
    body: dict,
    current_user: CurrentUser,
    session: AsyncSession = Depends(get_db_session),
):
    event_id = str(body.get("event_id", ""))[:100]
    event_name = str(body.get("event_name", ""))
    if not event_id or event_name not in {
        "NEED_MORE_TIME",
        "SKIP",
        "BEHIND_SCHEDULE",
        "MORNING_NO_PLAN",
    }:
        raise HTTPException(status_code=422, detail="invalid_event")
    user_settings = await session.scalar(
        select(UserSettings).where(UserSettings.user_id == current_user.id)
    )
    tz = safe_timezone(user_settings.timezone if user_settings else "UTC")
    local_now = datetime.now(timezone.utc).astimezone(tz)
    consecutive_count = None
    if event_name in {"NEED_MORE_TIME", "SKIP"}:
        from app.db.models.focus import FocusRun

        if not event_id.startswith("focus-"):
            raise HTTPException(status_code=422, detail="invalid_focus_event")
        try:
            run_id = UUID(event_id[6:])
        except ValueError:
            raise HTTPException(status_code=422, detail="invalid_focus_event") from None
        outcomes = (
            await session.execute(
                select(FocusRun.id, FocusRun.outcome)
                .where(FocusRun.user_id == current_user.id, FocusRun.status == "ENDED")
                .order_by(FocusRun.ended_at.desc(), FocusRun.id.desc())
                .limit(2)
            )
        ).all()
        if (
            not outcomes
            or outcomes[0].id != run_id
            or outcomes[0].outcome != event_name
        ):
            raise HTTPException(status_code=422, detail="invalid_focus_event")
        consecutive_count = sum(item.outcome == event_name for item in outcomes)
    if event_name == "MORNING_NO_PLAN":
        today = await today_service.get_today(
            session, current_user.id, local_now.date()
        )
        if today["status"] != "NO_PLAN":
            return {"nudge": None}
    nudge = nudge_gate.evaluate(
        user_id=current_user.id,
        event_id=event_id,
        event_name=event_name,
        local_now=local_now,
        quiet_start=user_settings.quiet_hours_start if user_settings else None,
        quiet_end=user_settings.quiet_hours_end if user_settings else None,
        quiet_enabled=bool(user_settings and user_settings.quiet_hours_enabled),
        consecutive_count=consecutive_count,
    )
    return {"nudge": nudge}
