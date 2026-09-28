"""Authoritative assistant orchestration entry point."""

from datetime import datetime
from dataclasses import replace
from uuid import UUID
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from sqlalchemy.ext.asyncio import AsyncSession

from app.ai.context import build_context
from app.ai.handlers.editor import edit
from app.ai.handlers.mood import tired_response
from app.ai.handlers.planner import plan_day
from app.ai.handlers.roadmap import roadmap
from app.ai.handlers.rules import handle as handle_rule
from app.ai.nlu.router import (
    Intent,
    Route,
    classify_low_confidence,
    detect_lang,
    is_explicit_goal_request,
    is_self_contained_day_plan,
    route,
)
from app.ai.nlu.router import normalize
from typing import cast
from app.db.models.tasks import Task
from app.ai.nlu.parser import ParsedPlan, ParsedTask
from sqlalchemy import or_, select
from app.services.today_service import today_service
from app.schemas.assistant import ChatRequest, ChatResponse
from app.schemas.drafts import TodayDraft


def _starts_fresh_day_plan(message: str, selected: Route) -> bool:
    """Return whether a complete, explicit day plan supersedes pending state.

    A pending clarification is useful for terse answers ("the first one", a
    date, etc.), but must not absorb a new request that independently names a
    day and supplies scheduling detail.
    """
    if selected.intent != "PLAN_DAY" or selected.confidence < 0.7:
        return False
    return is_self_contained_day_plan(message)


def _starts_fresh_goal(message: str, selected: Route) -> bool:
    return (
        selected.intent == "CREATE_GOAL"
        and selected.confidence >= 0.7
        and is_explicit_goal_request(message)
    )


async def chat(
    request: ChatRequest,
    timezone: str = "UTC",
    db: AsyncSession | None = None,
    user_id: UUID | None = None,
    history: list[dict] | None = None,
    pending_intent: str | None = None,
    pending_message: str | None = None,
) -> ChatResponse:
    try:
        tz = ZoneInfo(timezone)
    except ZoneInfoNotFoundError:
        tz = ZoneInfo("UTC")
    now = datetime.now(tz)
    if pending_intent and normalize(request.message) in {
        "cancel",
        "cancel that",
        "never mind",
        "nevermind",
        "huy",
        "thoi",
    }:
        return ChatResponse(
            reply="Đã hủy câu hỏi đang chờ."
            if detect_lang(request.message) == "vi"
            else "Okay, I cancelled that clarification.",
            intent=cast(Intent, pending_intent),
            tier="RULES",
        )
    selected = route(
        request.message,
        has_draft=request.current_draft is not None,
        awaiting_answer=bool(pending_intent),
    )
    if (
        pending_intent in {"PLAN_DAY", "CREATE_GOAL", "EDIT_DRAFT"}
        and selected.confidence < 0.7
    ):
        selected = route(request.message, has_draft=request.current_draft is not None)
        selected = Route(cast(Intent, pending_intent), 0.8, "rules", selected.flags)
    elif db is not None and user_id is not None:
        selected = await classify_low_confidence(
            request.message, selected, db, user_id, history
        )
    fresh_intent = _starts_fresh_day_plan(
        request.message, selected
    ) or _starts_fresh_goal(request.message, selected)
    effective_message = request.message
    effective_history = history
    if (
        not fresh_intent
        and pending_intent in {"PLAN_DAY", "CREATE_GOAL", "EDIT_DRAFT"}
        and pending_message
    ):
        effective_message = f"{pending_message}\n{request.message}"
    elif fresh_intent:
        # Old clarification turns are context for the old request, not this one.
        effective_history = None
    lang = detect_lang(request.message)
    if selected.intent in {"PLAN_DAY", "EDIT_DRAFT"}:
        if db is None or user_id is None:
            raise ValueError("Authenticated database context required")
        context = await build_context(db, user_id, now)
        if selected.intent == "PLAN_DAY":
            return await plan_day(
                effective_message,
                context,
                lang,
                history=effective_history,
                light="tired" in selected.flags,
            )
        if isinstance(request.current_draft, TodayDraft):
            return await edit(
                effective_message,
                request.current_draft,
                context,
                history=effective_history,
            )
    if selected.intent == "CREATE_GOAL":
        return roadmap(effective_message, lang, today=now.date())
    if selected.intent == "MOOD":
        if db is None or user_id is None:
            return tired_response(lang, has_plan=False)
        today = await today_service.get_today(db, user_id, now.date())
        if today["status"] != "NO_PLAN":
            return tired_response(lang, has_plan=True)
        pending = (
            await db.scalars(
                select(Task)
                .where(
                    Task.user_id == user_id,
                    Task.status.in_({"PENDING", "DRAFT"}),
                    # Work saved for a later day is not today's to lighten.
                    or_(Task.planned_date.is_(None), Task.planned_date <= now.date()),
                )
                .order_by(Task.created_at.desc())
                .limit(2)
            )
        ).all()
        if pending:
            from app.ai.handlers.planner import _preview

            context = replace(await build_context(db, user_id, now), calibration={})
            light = ParsedPlan(
                tasks=tuple(
                    ParsedTask(
                        title=item.title,
                        duration_min=min(25, item.estimated_duration_minutes),
                        source="RULE",
                        importance="OPTIONAL",
                        category=item.category,
                    )
                    for item in pending
                ),
                confidence=1.0,
            )
            result = await _preview(
                light, context, lang, tier="RULES", include_carried=False
            )
            result.intent = "MOOD"
            return result
        return tired_response(lang, has_plan=False)
    return await handle_rule(
        selected,
        request.message,
        db=db,
        user_id=user_id,
        now=now,
        lang=lang,
    )
