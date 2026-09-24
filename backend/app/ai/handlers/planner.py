"""Parser first day planning with a budgeted LLM cascade and one repair."""

from dataclasses import replace
from typing import Literal

from fastapi import HTTPException
from pydantic import BaseModel, Field, ValidationError

from app.ai.budget import BudgetMode, available_routes, get_budget_mode
from app.ai.context import ChatContext
from app.ai.drafts import assemble_today
from app.ai.parser import ParsedPlan, ParsedTask, parse
from app.schemas.patches import PatchOp
from app.ai.providers import LLMError, llm_provider
from app.ai.router import normalize
from app.ai.validators import check_today
from app.core.config import settings
from app.schemas.assistant import ChatResponse, QuickReply
from app.schemas.today import TodayPreviewRequest
from app.services.today_service import today_service


class LLMTask(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    duration_min: int = Field(ge=5, le=480)
    priority: Literal["LOW", "MEDIUM", "HIGH", "URGENT"] = "MEDIUM"
    importance: Literal["CORE", "OPTIONAL"] = "CORE"
    category: Literal["Learning", "Work", "Personal"] | None = None
    fixed_start: str | None = Field(None, pattern=r"^([01]\d|2[0-3]):[0-5]\d$")
    deadline: str | None = Field(None, pattern=r"^([01]\d|2[0-3]):[0-5]\d$")


class LLMDayPlan(BaseModel):
    reply: str = Field(min_length=1, max_length=1000)
    windows: list[tuple[str, str]] = Field(default_factory=list, max_length=4)
    tasks: list[LLMTask] = Field(min_length=1, max_length=15)
    assumptions: list[str] = Field(default_factory=list, max_length=6)


def _parsed_from_llm(value: LLMDayPlan, ctx: ChatContext, message: str) -> ParsedPlan:
    parser_plan = parse(message)
    parser_tasks = {normalize(t.title): t for t in parser_plan.tasks}
    llm_tasks = {normalize(t.title): t for t in value.tasks}
    
    final_tasks = []
    seen = set()
    
    # 1. Start with parser tasks to preserve deterministic order
    for p_task in parser_plan.tasks:
        norm_title = normalize(p_task.title)
        if norm_title in seen:
            continue
        seen.add(norm_title)
        
        # Merge LLM info if available
        if norm_title in llm_tasks:
            l_task = llm_tasks[norm_title]
            
            # Preserve USER explicit duration/source.
            is_user_explicit = p_task.source == "USER" and p_task.duration_min is not None
            final_source = "USER" if is_user_explicit else p_task.source
            final_duration = p_task.duration_min if is_user_explicit else (l_task.duration_min or p_task.duration_min)
            
            final_tasks.append(ParsedTask(
                title=p_task.title,
                duration_min=final_duration,
                source=final_source,
                importance=l_task.importance,
                priority="HIGH" if l_task.priority == "URGENT" else l_task.priority,
                category=l_task.category or p_task.category,
                fixed_start=l_task.fixed_start or p_task.fixed_start,
                deadline=l_task.deadline or p_task.deadline
            ))
        else:
            # LLM omitted it, restore it completely
            final_tasks.append(p_task)
            
    # 2. Append LLM-only tasks
    for l_task in value.tasks:
        norm_title = normalize(l_task.title)
        if norm_title not in seen:
            seen.add(norm_title)
            final_tasks.append(ParsedTask(
                title=l_task.title,
                duration_min=l_task.duration_min,
                source="AI",
                importance=l_task.importance,
                priority="HIGH" if l_task.priority == "URGENT" else l_task.priority,
                category=l_task.category,
                fixed_start=l_task.fixed_start,
                deadline=l_task.deadline
            ))

    return ParsedPlan(
        tasks=tuple(final_tasks), 
        windows=tuple(value.windows) if value.windows else parser_plan.windows, 
        plan_date_offset=max(ctx.default_date_offset, parser_plan.plan_date_offset),
        confidence=1.0, 
        assumptions=tuple(value.assumptions)
    )


async def _llm_plan(
    message: str,
    ctx: ChatContext,
    mode: BudgetMode,
    routes: str | None = None,
    history: list[dict] | None = None,
) -> tuple[ParsedPlan, str] | None:
    if mode == BudgetMode.RULES_ONLY or routes == "":
        return None
    routes = routes or settings.AI_ROUTE_PLANNER_LITE
    messages = [
        {"role": "system", "content": "Extract only the user's day planning tasks. Code owns scheduling, dates, IDs, duration provenance and totals. Do not claim anything was saved."},
        *(history or [])[-4:],
        {"role": "user", "content": message},
    ]
    try:
        raw = await llm_provider.call(
            routes, messages, temperature=0.1, max_tokens=1200,
            require_json=True, json_schema=LLMDayPlan.model_json_schema(),
            db=ctx.db, user_id=ctx.user_id, purpose="PLANNER",
        )
    except LLMError:
        return ParsedPlan(), ""
    reply = raw.get("reply") if isinstance(raw, dict) else None
    try:
        value = LLMDayPlan.model_validate(raw)
        return _parsed_from_llm(value, ctx, message), value.reply
    except ValidationError as first_error:
        if mode != BudgetMode.NORMAL:
            return (ParsedPlan(), reply) if isinstance(reply, str) and reply.strip() else None
        repair = messages + [
            {"role": "assistant", "content": str(raw)},
            {"role": "user", "content": f"Repair only the JSON structure once. Validation errors: {first_error.errors(include_url=False)}"},
        ]
        try:
            fixed = await llm_provider.call(
                routes, repair, temperature=0, max_tokens=1200,
                require_json=True, json_schema=LLMDayPlan.model_json_schema(),
                db=ctx.db, user_id=ctx.user_id, purpose="PLANNER",
            )
            value = LLMDayPlan.model_validate(fixed)
            return _parsed_from_llm(value, ctx, message), reply or value.reply
        except (LLMError, ValidationError):
            return (ParsedPlan(), reply) if isinstance(reply, str) and reply.strip() else None


async def _preview(plan: ParsedPlan, ctx: ChatContext, lang: str, *, tier: str,
                   reply: str | None = None, degraded: str | None = None) -> ChatResponse:
    draft, assumptions = assemble_today(plan, ctx)
    if check_today(draft):
        question = "Please clarify the tasks or available time before I schedule them."
        return ChatResponse(
            reply=reply or question, question=question, intent="PLAN_DAY", tier=tier, degraded=degraded,
            draft=draft, assumptions=assumptions
        )
    # Do not automatically preview. Let the frontend click "Generate Timeline".
    return ChatResponse(
        reply=reply or "I've created a draft. Please review your tasks and constraints, then generate the timeline.",
        intent="PLAN_DAY",
        tier=tier,
        degraded=degraded,
        draft=draft,
        preview=None,
        assumptions=assumptions,
        suggestions=[],
    )


async def plan_day(message: str, ctx: ChatContext, lang: str, *,
                   history: list[dict] | None = None, light: bool = False) -> ChatResponse:
    if light:
        ctx = replace(ctx, calibration={})
    parsed = parse(message)
    if light:
        parsed = replace(parsed, tasks=tuple(replace(task, importance="OPTIONAL",
            duration_min=min(task.duration_min or 25, 25) if task.source != "USER" else task.duration_min)
            for task in parsed.tasks))
    if (parsed.tasks or parsed.windows or parsed.assumptions or parsed.plan_date_offset > 0) and parsed.confidence >= 0.8 and not parsed.unresolved:
        return await _preview(parsed, ctx, lang, tier="PARSER")
    mode = await get_budget_mode(ctx.db, ctx.user_id, "PLANNER", now=ctx.now)
    configured_routes = settings.AI_ROUTE_PLANNER_LITE
    if mode == BudgetMode.NORMAL:
        configured_routes = f"{configured_routes},{settings.AI_ROUTE_PLANNER}"
    routes = await available_routes(ctx.db, configured_routes, now=ctx.now)
    if not routes:
        mode = BudgetMode.RULES_ONLY
    # End read transactions before waiting on an external provider.
    await ctx.db.commit()
    llm_result = await _llm_plan(message, ctx, mode, routes, history)
    if llm_result and llm_result[0].tasks:
        llm_plan = llm_result[0]
        if light:
            llm_plan = replace(llm_plan, tasks=tuple(replace(task, importance="OPTIONAL",
                duration_min=min(task.duration_min or 25, 25) if task.source != "USER" else task.duration_min)
                for task in llm_plan.tasks))
        return await _preview(llm_plan, ctx, lang, tier="LLM", reply=llm_result[1],
                              degraded=mode.value if mode != BudgetMode.NORMAL else None)
    if parsed.tasks or parsed.windows or parsed.assumptions or parsed.plan_date_offset > 0:
        return await _preview(parse(message, lenient=True), ctx, lang, tier="PARSER", degraded="RULES_ONLY")
    reply = llm_result[1] if llm_result else None
    question = "Bạn muốn làm những việc gì hôm nay?" if lang == "vi" else "Which tasks would you like to plan today?"
    provider_failed = llm_result is not None and not llm_result[0].tasks and not llm_result[1]
    return ChatResponse(reply=reply or question, question=question, intent="PLAN_DAY", tier="PARSER",
                        degraded="RULES_ONLY" if provider_failed else mode.value if mode != BudgetMode.NORMAL else None)
