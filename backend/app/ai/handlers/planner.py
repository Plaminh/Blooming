"""LLM-first day planning with deterministic normalization and degraded parser fallback."""

import re
from dataclasses import replace
from typing import Literal

from pydantic import BaseModel, Field, ValidationError

from app.ai.budget import BudgetMode, available_routes, get_budget_mode
from app.ai.carryover import carried_tasks
from app.ai.context import ChatContext
from app.ai.drafts import assemble_today, primary_plan_date
from app.ai.parser import ParsedPlan, ParsedTask, extract_day_ref, parse
from app.ai.providers import LLMError, llm_provider
from app.ai.router import normalize
from app.ai.validators import check_today
from app.core.config import settings
from app.schemas.assistant import Assumption, ChatResponse
from app.schemas.drafts import TodayDraft


class LLMTask(BaseModel):
    model_config = {"extra": "ignore"}
    title: str = Field(min_length=1, max_length=200)
    duration_min: int = Field(ge=5, le=480)
    priority: Literal["LOW", "MEDIUM", "HIGH", "URGENT"] = "MEDIUM"
    importance: Literal["CORE", "OPTIONAL"] = "CORE"
    category: Literal["Learning", "Work", "Personal"] | None = None
    fixed_start: str | None = Field(None, pattern=r"^([01]\d|2[0-3]):[0-5]\d$")
    fixed_end: str | None = Field(None, pattern=r"^([01]\d|2[0-3]):[0-5]\d$")
    deadline: str | None = Field(None, pattern=r"^([01]\d|2[0-3]):[0-5]\d$")


class LLMDayPlan(BaseModel):
    model_config = {"extra": "ignore"}
    reply: str = Field(default="", max_length=1000)
    windows: list[tuple[str, str]] = Field(default_factory=list, max_length=4)
    tasks: list[LLMTask] = Field(default_factory=list, max_length=15)
    assumptions: list[str] = Field(default_factory=list, max_length=6)


PURE_PLAN_COMMAND_RE = re.compile(
    r"^\s*(?:hãy\s+|please\s+)?(?:lập\s*lịch|lên\s*kế\s*hoạch|xếp\s*lịch|sắp\s*xếp\s*lịch|plan|schedule)"
    r"(?:\s+(?:cho\s+)?(?:hôm\s*nay|ngày\s*hôm\s*nay|today|my\s*day|my\s*work|work))?\s*[:：.?!]*\s*$",
    re.IGNORECASE,
)


def is_pure_plan_command(message: str) -> bool:
    """True only for explicit 'plan existing work' commands without newly described tasks."""
    return bool(PURE_PLAN_COMMAND_RE.match(message.strip()))


def _parsed_from_llm(value: LLMDayPlan, ctx: ChatContext, message: str) -> ParsedPlan:
    parser_plan = parse(message)
    parser_by_title = {normalize(t.title): t for t in parser_plan.tasks}

    final_tasks = []
    seen = set()

    for l_task in value.tasks:
        norm_title = normalize(l_task.title)
        if not norm_title or norm_title in seen:
            continue
        seen.add(norm_title)

        p_match = parser_by_title.get(norm_title)
        is_user_explicit = (
            p_match is not None and p_match.source == "USER" and p_match.duration_min is not None
        )
        duration = max(5, min(l_task.duration_min, 480))
        final_tasks.append(
            ParsedTask(
                title=l_task.title.strip()[:200],
                duration_min=duration,
                source="USER" if is_user_explicit else "AI",
                importance=l_task.importance,
                priority="HIGH" if l_task.priority == "URGENT" else l_task.priority,
                category=l_task.category,
                fixed_start=l_task.fixed_start,
                fixed_end=l_task.fixed_end,
                deadline=l_task.deadline,
                day=parser_plan.day,
                recurrence=None,
                spread=None,
            )
        )

    return ParsedPlan(
        tasks=tuple(final_tasks),
        windows=tuple(value.windows),
        plan_date_offset=max(ctx.default_date_offset, parser_plan.plan_date_offset),
        confidence=1.0,
        assumptions=tuple(value.assumptions),
        day=parser_plan.day,
    )


async def _llm_plan(
    message: str,
    ctx: ChatContext,
    mode: BudgetMode,
    routes: str | None = None,
    history: list[dict] | None = None,
    original_message: str | None = None,
) -> tuple[ParsedPlan, str] | None:
    if mode == BudgetMode.RULES_ONLY or routes == "":
        return None
    routes = routes or settings.AI_ROUTE_PLANNER_LITE
    messages = [
        {
            "role": "system",
            "content": "Extract only the user's day planning tasks. Code owns scheduling, dates, IDs, duration provenance and totals. Do not claim anything was saved.",
        },
        *(history or [])[-4:],
        {"role": "user", "content": message},
    ]
    try:
        raw = await llm_provider.call(
            routes,
            messages,
            temperature=0.1,
            max_tokens=1200,
            require_json=True,
            json_schema=LLMDayPlan.model_json_schema(),
            db=ctx.db,
            user_id=ctx.user_id,
            purpose="PLANNER",
        )
    except LLMError:
        return None

    reply = raw.get("reply") if isinstance(raw, dict) else None
    try:
        value = LLMDayPlan.model_validate(raw)
        return _parsed_from_llm(value, ctx, original_message or message), value.reply
    except ValidationError as first_error:
        if mode != BudgetMode.NORMAL:
            return (
                (ParsedPlan(confidence=0.0), reply)
                if isinstance(reply, str) and reply.strip()
                else None
            )
        repair = messages + [
            {"role": "assistant", "content": str(raw)},
            {
                "role": "user",
                "content": f"Repair only the JSON structure once. Validation errors: {first_error.errors(include_url=False)}",
            },
        ]
        try:
            fixed = await llm_provider.call(
                routes,
                repair,
                temperature=0,
                max_tokens=1200,
                require_json=True,
                json_schema=LLMDayPlan.model_json_schema(),
                db=ctx.db,
                user_id=ctx.user_id,
                purpose="PLANNER",
            )
            value = LLMDayPlan.model_validate(fixed)
            return _parsed_from_llm(value, ctx, original_message or message), reply or value.reply
        except (LLMError, ValidationError):
            return (
                (ParsedPlan(confidence=0.0), reply)
                if isinstance(reply, str) and reply.strip()
                else None
            )


def _draft_summary(draft: TodayDraft, lang: str) -> str:
    """One deterministic sentence saying which days the draft covers."""
    vi = lang == "vi"
    day = draft.planDate.strftime("%d/%m")
    parts = [
        f"Mình đã xếp {len(draft.tasks)} việc cho ngày {day}."
        if vi
        else f"I drafted {len(draft.tasks)} task(s) for {day}."
    ]
    if draft.deferred_tasks:
        days = sorted({item.targetDate for item in draft.deferred_tasks})
        labels = ", ".join(value.strftime("%d/%m") for value in days[:5])
        more = "…" if len(days) > 5 else ""
        parts.append(
            f"{len(draft.deferred_tasks)} việc khác được lưu cho ngày {labels}{more}; "
            "khi bạn lập lịch những ngày đó, chúng sẽ tự có trong bản nháp."
            if vi
            else f"{len(draft.deferred_tasks)} more will be saved for {labels}{more} "
            "and added automatically when you plan those days."
        )
    repeating = [
        task
        for task in draft.tasks + [item.task for item in draft.deferred_tasks]
        if task.recurrence is not None
    ]
    if repeating:
        names = ", ".join(
            f"{task.title} ({task.recurrence.label(lang)})"  # type: ignore[union-attr]
            for task in repeating[:3]
        )
        parts.append(
            f"Việc lặp lại: {names}. Sau khi lưu, mình sẽ tự thêm chúng vào những ngày sau."
            if vi
            else f"Repeating: {names}. After you save, I'll add them to future days automatically."
        )
    parts.append(
        "Bạn xem lại rồi bấm tạo timeline nhé."
        if vi
        else "Please review your tasks and constraints, then generate the timeline."
    )
    return " ".join(parts)


async def _preview(
    plan: ParsedPlan,
    ctx: ChatContext,
    lang: str,
    *,
    tier: str,
    reply: str | None = None,
    degraded: str | None = None,
    carried: list[ParsedTask] | None = None,
    include_carried: bool = True,
) -> ChatResponse:
    if carried is None:
        carried = (
            await carried_tasks(
                ctx.db, ctx.user_id, primary_plan_date(plan, ctx), ctx.timezone
            )
            if include_carried
            else []
        )
    draft, assumptions = assemble_today(plan, ctx, carried)
    if not draft.tasks:
        question = (
            "Bạn muốn làm những việc gì hôm nay?"
            if lang == "vi"
            else "Which tasks would you like to plan today?"
        )
        return ChatResponse(
            reply=reply or question,
            question=question,
            intent="PLAN_DAY",
            tier=tier,
            degraded=degraded,
            draft=None,
            assumptions=assumptions,
        )
    if check_today(draft):
        question = (
            "Bạn nói rõ giúp mình các việc cần làm hoặc thời gian rảnh nhé."
            if lang == "vi"
            else "Please clarify the tasks or available time before I schedule them."
        )
        return ChatResponse(
            reply=reply or question,
            question=question,
            intent="PLAN_DAY",
            tier=tier,
            degraded=degraded,
            draft=draft,
            assumptions=assumptions,
        )
    summary = _draft_summary(draft, lang)
    # Do not automatically preview. Let the frontend click "Generate Timeline".
    return ChatResponse(
        reply=f"{reply}\n{summary}" if reply else summary,
        intent="PLAN_DAY",
        tier=tier,
        degraded=degraded,
        draft=draft,
        preview=None,
        assumptions=assumptions,
        suggestions=[],
    )


async def plan_day(
    message: str,
    ctx: ChatContext,
    lang: str,
    *,
    history: list[dict] | None = None,
    original_message: str | None = None,
    light: bool = False,
) -> ChatResponse:
    if light:
        ctx = replace(ctx, calibration={})

    # Only bypass LLM for pure 'plan my day' commands that genuinely describe no new work
    if is_pure_plan_command(message):
        day, offset = extract_day_ref(message)
        dummy_plan = ParsedPlan(day=day, plan_date_offset=offset)
        carried = await carried_tasks(
            ctx.db, ctx.user_id, primary_plan_date(dummy_plan, ctx), ctx.timezone
        )
        if carried:
            return await _preview(dummy_plan, ctx, lang, tier="RULES", carried=carried)

    mode = await get_budget_mode(ctx.db, ctx.user_id, "PLANNER", now=ctx.now)
    configured_routes = settings.AI_ROUTE_PLANNER_LITE
    if mode == BudgetMode.NORMAL:
        configured_routes = f"{configured_routes},{settings.AI_ROUTE_PLANNER}"
    routes = await available_routes(ctx.db, configured_routes, now=ctx.now)
    if not routes:
        mode = BudgetMode.RULES_ONLY

    # End read transactions before waiting on an external provider.
    await ctx.db.commit()
    llm_result = await _llm_plan(
        message, ctx, mode, routes, history, original_message=original_message
    )
    llm_reply = llm_result[1] if llm_result else None
    llm_plan = llm_result[0] if llm_result else None
    llm_success = llm_plan is not None and llm_plan.confidence > 0.0

    if llm_success and llm_plan is not None:
        if light:
            llm_plan = replace(
                llm_plan,
                tasks=tuple(
                    replace(
                        task,
                        importance="OPTIONAL",
                        duration_min=min(task.duration_min or 25, 25)
                        if task.source != "USER"
                        else task.duration_min,
                    )
                    for task in llm_plan.tasks
                ),
            )
        if llm_plan.tasks:
            return await _preview(
                llm_plan,
                ctx,
                lang,
                tier="LLM",
                reply=llm_reply,
                degraded=mode.value if mode != BudgetMode.NORMAL else None,
            )

        # Valid LLM extraction with 0 tasks (e.g. windows only, assumptions only, or empty {})
        # Check if there is legitimate carried work to schedule
        carried = await carried_tasks(
            ctx.db, ctx.user_id, primary_plan_date(llm_plan, ctx), ctx.timezone
        )
        if carried:
            return await _preview(
                llm_plan,
                ctx,
                lang,
                tier="LLM",
                reply=llm_reply,
                degraded=mode.value if mode != BudgetMode.NORMAL else None,
                carried=carried,
            )
        # No usable tasks and no carried tasks -> do NOT generate an invalid/empty TodayDraft
        question = (
            "Bạn muốn làm những việc gì hôm nay?"
            if lang == "vi"
            else "Which tasks would you like to plan today?"
        )
        return ChatResponse(
            reply=llm_reply or question,
            question=question,
            intent="PLAN_DAY",
            tier="LLM",
            degraded=mode.value if mode != BudgetMode.NORMAL else None,
            draft=None,
            assumptions=[
                Assumption(id=f"a-llm-{i}", kind="PARSER", text=a)
                for i, a in enumerate(llm_plan.assumptions)
            ],
        )

    # Provider failed or budget is RULES_ONLY -> fallback to deterministic parser
    provider_failed = mode != BudgetMode.RULES_ONLY and bool(routes)
    degraded_reason = "LLM_FAILED" if provider_failed else "RULES_ONLY"

    lenient_parsed = parse(message, lenient=True)
    if light:
        lenient_parsed = replace(
            lenient_parsed,
            tasks=tuple(
                replace(
                    task,
                    importance="OPTIONAL",
                    duration_min=min(task.duration_min or 25, 25)
                    if task.source != "USER"
                    else task.duration_min,
                )
                for task in lenient_parsed.tasks
            ),
        )

    if lenient_parsed.tasks:
        return await _preview(
            lenient_parsed,
            ctx,
            lang,
            tier="PARSER",
            degraded=degraded_reason,
            reply=llm_reply,
        )

    # Parser fallback has 0 tasks: check carried tasks
    carried = await carried_tasks(
        ctx.db, ctx.user_id, primary_plan_date(lenient_parsed, ctx), ctx.timezone
    )
    if carried:
        return await _preview(
            lenient_parsed,
            ctx,
            lang,
            tier="PARSER",
            degraded=degraded_reason,
            reply=llm_reply,
            carried=carried,
        )

    # Clarification fallback: neither LLM nor deterministic fallback could produce a valid draft
    question = (
        "Bạn muốn làm những việc gì hôm nay?"
        if lang == "vi"
        else "Which tasks would you like to plan today?"
    )
    return ChatResponse(
        reply=llm_reply or question,
        question=question,
        intent="PLAN_DAY",
        tier="PARSER",
        degraded=degraded_reason if provider_failed else (mode.value if mode != BudgetMode.NORMAL else None),
        draft=None,
    )
