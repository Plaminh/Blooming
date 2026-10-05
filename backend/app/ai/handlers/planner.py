"""LLM-first day planning with deterministic normalization and degraded parser fallback."""

import re
from dataclasses import replace
from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field, ValidationError, model_validator

from app.ai.llm.budget import BudgetMode, available_routes, get_budget_mode
from app.ai.carryover import carried_tasks
from app.ai.context import ChatContext
from app.ai.drafting.drafts import assemble_today, primary_plan_date
from app.ai.nlu.parser import ParsedPlan, ParsedTask, extract_day_ref, parse
from app.ai.llm.providers import LLMError, llm_provider
from app.ai.nlu.router import normalize
from app.ai.drafting.validators import check_today
from app.core.config import settings
from app.schemas.assistant import Assumption, ChatResponse
from app.schemas.drafts import TodayDraft


class LLMTask(BaseModel):
    model_config = {"extra": "ignore"}
    title: str = Field(
        min_length=1,
        max_length=200,
        description="Clean actionable task name only; omit conversational, optionality, and duration wording.",
    )
    duration_min: int | None = Field(
        default=None,
        ge=5,
        le=480,
        description="Task duration in minutes; may be null only when both fixed times provide it.",
    )
    duration_is_explicit: bool | None = Field(
        default=None,
        description="True only when the user explicitly supplied this task's duration.",
    )
    priority: Literal["LOW", "MEDIUM", "HIGH", "URGENT"] = "MEDIUM"
    importance: Literal["CORE", "OPTIONAL"] = Field(
        default="CORE",
        description="OPTIONAL for tasks qualified by optionally, maybe, or if time allows; otherwise CORE.",
    )
    category: Literal["Learning", "Work", "Personal"] | None = None
    fixed_start: str | None = Field(
        None,
        pattern=r"^([01]\d|2[0-3]):[0-5]\d$",
        description="Exact start of this task, only when the user assigns a task-specific interval.",
    )
    fixed_end: str | None = Field(
        None,
        pattern=r"^([01]\d|2[0-3]):[0-5]\d$",
        description="Exact end of this task; must accompany fixed_start, never a deadline.",
    )
    deadline: str | None = Field(
        None,
        pattern=r"^([01]\d|2[0-3]):[0-5]\d$",
        description="Latest completion time from wording such as 'before noon'; not a fixed end.",
    )

    @model_validator(mode="after")
    def validate_fixed_interval(self) -> "LLMTask":
        if (self.fixed_start is None) != (self.fixed_end is None):
            raise ValueError("fixed_start and fixed_end must be supplied together")
        if self.fixed_start is not None and self.fixed_end is not None:
            start = datetime.strptime(self.fixed_start, "%H:%M")
            end = datetime.strptime(self.fixed_end, "%H:%M")
            if end <= start:
                raise ValueError(
                    "fixed_end must be later than fixed_start on the same day"
                )
            interval_minutes = int((end - start).total_seconds() // 60)
            if not 5 <= interval_minutes <= 480:
                raise ValueError(
                    "fixed interval duration must be between 5 and 480 minutes"
                )
            self.duration_min = interval_minutes
            self.duration_is_explicit = True
        if self.duration_min is None:
            raise ValueError("duration_min is required for a flexible task")
        return self


class LLMDayPlan(BaseModel):
    model_config = {"extra": "ignore"}
    reply: str = Field(default="", max_length=1000)
    windows: list[tuple[str, str]] = Field(
        default_factory=list,
        max_length=4,
        description="User's global availability windows as 24-hour HH:MM start/end pairs, never task constraints.",
    )
    tasks: list[LLMTask] = Field(default_factory=list, max_length=15)
    assumptions: list[str] = Field(default_factory=list, max_length=6)


PURE_PLAN_COMMAND_RE = re.compile(
    r"^\s*(?:hãy\s+|please\s+)?(?:lập\s*lịch|lên\s*kế\s*hoạch|xếp\s*lịch|sắp\s*xếp\s*lịch|plan|schedule)"
    r"(?:\s+(?:cho\s+)?(?:hôm\s*nay|ngày\s*hôm\s*nay|today|my\s*day|my\s*work|work))?\s*[:：.?!]*\s*$",
    re.IGNORECASE,
)

DAY_PLAN_SYSTEM_PROMPT = (
    "Extract the user's day-planning meaning into the supplied schema. "
    "Treat statements such as 'I am available/free from X to Y' or 'between X and Y' "
    "as global availability in windows, not as a task's fixed_start/fixed_end. Convert times "
    "to 24-hour HH:MM. A task-specific event such as 'I have a meeting from 9 AM to 10 AM' "
    "is a task named 'Meeting' with fixed_start=09:00 and fixed_end=10:00; include it even "
    "when no separate duration is stated, because its duration comes from the interval. "
    "Wording such as 'finish the report before noon' sets deadline=12:00 and does not set "
    "fixed_start or fixed_end. Global availability, fixed task intervals, and deadlines are distinct. "
    "Use clean imperative task titles: remove conversational lead-ins "
    "such as 'Today I need to', duration phrases, and optionality qualifiers. Mark tasks "
    "introduced by 'optionally', 'maybe', 'if there is time', 'if I have time', or "
    "'if time allows' as OPTIONAL; otherwise use CORE. Preserve each explicit duration in "
    "minutes and set duration_is_explicit=true for it; set false only when the duration was "
    "estimated by the model. Only use fixed_start/fixed_end when the user assigns that time specifically "
    "to one task. Do not schedule flexible tasks inside a global availability window. Do not "
    "invent tasks, availability, or assumptions. Code owns scheduling, dates, IDs, duration "
    "provenance, and totals. Do not claim anything was saved."
)


def is_pure_plan_command(message: str) -> bool:
    """True only for explicit 'plan existing work' commands without newly described tasks."""
    return bool(PURE_PLAN_COMMAND_RE.match(message.strip()))


def _title_tokens(value: str) -> set[str]:
    return set(re.findall(r"[a-z0-9]+", normalize(value)))


def _matching_parser_task(
    title: str, candidates: tuple[ParsedTask, ...]
) -> ParsedTask | None:
    """The parsed task a model title refers to ("Họp" -> "Họp nhóm"), if unique.

    Titles match when one's words contain the other's; the closest match wins
    and a tie matches nothing, so ambiguous tasks borrow no day or repetition.
    """
    wanted = _title_tokens(title)
    scored = []
    for task in candidates:
        tokens = _title_tokens(task.title)
        if wanted and tokens and (tokens <= wanted or wanted <= tokens):
            scored.append((len(tokens & wanted) / len(tokens | wanted), task))
    scored.sort(key=lambda item: item[0], reverse=True)
    if not scored or (len(scored) > 1 and scored[0][0] == scored[1][0]):
        return None
    return scored[0][1]


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

        # New structured responses own provenance. The parser lookup is retained
        # only for older/mock responses that predate duration_is_explicit.
        p_match = parser_by_title.get(norm_title)
        legacy_user_explicit = (
            l_task.duration_is_explicit is None
            and p_match is not None
            and p_match.source == "USER"
            and p_match.duration_min is not None
        )
        assert l_task.duration_min is not None  # Enforced by LLMTask validation.
        duration = max(5, min(l_task.duration_min, 480))
        # The model is never asked for days or repetition; the parser reads them
        # from the user's words ("thứ 2 ...", "mỗi ngày ..."), so take them from
        # the parsed task this one corresponds to.
        evidence = p_match or _matching_parser_task(l_task.title, parser_plan.tasks)
        if evidence is not None and evidence.spread and evidence.duration_min:
            duration = evidence.duration_min  # A weekly total, split on assembly.
        final_tasks.append(
            ParsedTask(
                title=l_task.title.strip()[:200],
                duration_min=duration,
                source="USER"
                if l_task.duration_is_explicit or legacy_user_explicit
                else "AI",
                importance=l_task.importance,
                priority="HIGH" if l_task.priority == "URGENT" else l_task.priority,
                category=l_task.category,
                fixed_start=l_task.fixed_start,
                fixed_end=l_task.fixed_end,
                deadline=l_task.deadline,
                day=(evidence.day if evidence else None) or parser_plan.day,
                recurrence=evidence.recurrence if evidence else None,
                spread=evidence.spread if evidence else None,
            )
        )

    return ParsedPlan(
        tasks=tuple(final_tasks),
        # Preserve an explicit deterministic availability window when the LLM
        # omits it; a supplied LLM window remains authoritative.
        windows=tuple(value.windows or parser_plan.windows),
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
            "content": DAY_PLAN_SYSTEM_PROMPT,
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
        validation_messages = [
            str(error.get("ctx", {}).get("error", error.get("msg", "")))
            for error in first_error.errors(include_url=False)
        ]
        impossible_interval = any(
            "fixed_end must be later" in message or "fixed interval duration" in message
            for message in validation_messages
        )
        if impossible_interval:
            return (
                (ParsedPlan(confidence=0.0), reply)
                if isinstance(reply, str) and reply.strip()
                else None
            )
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
                "content": (
                    "Repair the structured extraction once without dropping any user-mentioned task "
                    "or changing its semantic kind. Keep task-specific intervals fixed, global windows "
                    "global, and 'before' times as deadlines. Validation errors: "
                    f"{first_error.errors(include_url=False)}"
                ),
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
            return _parsed_from_llm(
                value, ctx, original_message or message
            ), reply or value.reply
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
        configured_routes = settings.AI_ROUTE_PLANNER
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
        degraded=degraded_reason
        if provider_failed
        else (mode.value if mode != BudgetMode.NORMAL else None),
        draft=None,
    )
