"""Assemble canonical server-owned drafts from parsed plan details.

A message may name several days ("Thứ 2 học toán, thứ 4 họp"). The earliest
day becomes the draft's plan date and is scheduled now; tasks for later days
travel as ``deferred_tasks`` and are stored for their day on save, so they
come back automatically when that day is planned.
"""

from collections.abc import Sequence
from dataclasses import replace
from datetime import date, datetime, timedelta

from app.ai.calibration import apply_multiplier
from app.ai.context import ChatContext
from app.ai.parser import MIN_SPREAD_CHUNK, ParsedPlan, ParsedTask
from app.ai.router import normalize
from app.schemas.assistant import Assumption
from app.schemas.drafts import (
    AvailabilityWindowDraft,
    DeferredTaskDraft,
    RecurrenceDraft,
    TaskDraft,
    TodayDraft,
)

# Default start of availability on a day that has not begun yet.
FUTURE_DAY_START = "08:00"


def _total_minutes(wins: list[tuple[str, str]]) -> int:
    total = 0
    for s, e in wins:
        try:
            sh, sm = map(int, s.split(":"))
            eh, em = map(int, e.split(":"))
            total += max(0, (eh * 60 + em) - (sh * 60 + sm))
        except (ValueError, AttributeError):
            pass
    return total


def _round5(value: float) -> int:
    return int(round(value / 5) * 5)


def _week_bounds(today: date, which: str) -> tuple[date, date]:
    monday = today - timedelta(days=today.weekday())
    if which == "NEXT_WEEK":
        monday += timedelta(days=7)
    return monday, monday + timedelta(days=6)


def _spread(task: ParsedTask, first_day: date, today: date) -> list[tuple[ParsedTask, date]]:
    """Split "tuần này ôn thi 10 tiếng" into roughly equal daily sessions."""
    start, end = _week_bounds(today, task.spread or "THIS_WEEK")
    start = max(start, first_day)
    if start > end:  # Late on Sunday: "this week" has no days left.
        start, end = _week_bounds(today, "NEXT_WEEK")
    days = [start + timedelta(days=i) for i in range((end - start).days + 1)]
    total = task.duration_min or 60
    count = max(1, min(len(days), total // MIN_SPREAD_CHUNK))
    # Cumulative rounding keeps every session a multiple of five minutes while
    # the sessions still add up to the requested total.
    bounds = [_round5(total * i / count) for i in range(count + 1)]
    sessions = []
    for index in range(count):
        minutes = min(480, max(5, bounds[index + 1] - bounds[index]))
        title = task.title if count == 1 else f"{task.title} ({index + 1}/{count})"
        sessions.append(
            (
                replace(task, title=title[:200], duration_min=minutes, spread=None, day=None),
                days[index],
            )
        )
    return sessions


def _first_occurrence(task: ParsedTask, day: date) -> date:
    recurrence = task.recurrence
    if recurrence is None or not recurrence.weekdays:
        return day
    for step in range(7):
        candidate = day + timedelta(days=step)
        if candidate.weekday() in recurrence.weekdays:
            return candidate
    return day


def _task_dates(plan: ParsedPlan, ctx: ChatContext) -> list[tuple[ParsedTask, date]]:
    today = ctx.now.date()
    default_day = today + timedelta(days=max(plan.plan_date_offset, ctx.default_date_offset))
    dated: list[tuple[ParsedTask, date]] = []
    for task in plan.tasks:
        day = task.day.resolve(today) if task.day else default_day
        day = max(day, today)
        if task.spread:
            dated.extend(_spread(task, max(day, default_day), today))
            continue
        dated.append((task, _first_occurrence(task, day)))
    return dated


def _default_windows(ctx: ChatContext, plan_date: date) -> list[tuple[str, str]]:
    windows = list(ctx.default_windows)
    if plan_date == ctx.now.date() or not windows:
        return windows
    # Context defaults start at "now" for today; a later day starts fresh.
    return [
        (FUTURE_DAY_START if end > FUTURE_DAY_START else start, end)
        for start, end in windows
    ]


def _recurrence_draft(task: ParsedTask, day: date) -> RecurrenceDraft | None:
    recurrence = task.recurrence
    if recurrence is None:
        return None
    until = None
    if recurrence.until_end_of_week:
        until = day + timedelta(days=6 - day.weekday())
    return RecurrenceDraft(
        freq=recurrence.freq,
        weekdays=list(recurrence.weekdays),
        until=until,
    )


def _task_draft(
    item: ParsedTask,
    task_id: str,
    day: date,
    ctx: ChatContext,
    assumptions: list[Assumption],
) -> TaskDraft:
    raw_duration = item.duration_min or 45
    duration = min(480, max(5, raw_duration))
    calibrated = item.source in {"RULE", "AI"} and item.category in ctx.calibration
    if calibrated:
        duration = apply_multiplier(duration, item.category, ctx.calibration)
    if duration != raw_duration:
        assumptions.append(
            Assumption(
                id=f"a-limit-{task_id}",
                kind="DURATION",
                task_id=task_id,
                text=f"Capped {item.title} at {duration} minutes",
            )
        )
    if item.source in {"RULE", "AI"} or item.duration_min is None:
        assumptions.append(
            Assumption(
                id=f"a-duration-{task_id}",
                kind="DURATION",
                task_id=task_id,
                text=f"Estimated {duration} minutes for {item.title}",
            )
        )
    fixed_start = None
    fixed_end = None
    if item.fixed_start:
        fixed_start = datetime.combine(
            day,
            datetime.strptime(item.fixed_start, "%H:%M").time(),
            tzinfo=ctx.timezone,
        )
        if item.fixed_end:
            fixed_end = datetime.combine(
                day,
                datetime.strptime(item.fixed_end, "%H:%M").time(),
                tzinfo=ctx.timezone,
            )
        else:
            fixed_end = fixed_start + timedelta(minutes=duration)
        if (item.source_task_id or item.recurring_task_id) and (
            fixed_end <= fixed_start or fixed_end.date() != day
        ):
            # A carried task whose window no longer fits the day is flexible.
            fixed_start = fixed_end = None
    deadline = (
        datetime.combine(
            day,
            datetime.strptime(item.deadline, "%H:%M").time(),
            tzinfo=ctx.timezone,
        )
        if item.deadline
        else None
    )
    return TaskDraft(
        id=task_id,
        title=item.title,
        durationMin=duration,
        priority=item.priority,
        importance=item.importance,
        category=item.category,
        estimateSource="HISTORY" if calibrated else item.source,
        breakAfterMin=ctx.break_minutes or None,
        schedulingType="FIXED" if fixed_start else "FLEXIBLE",
        fixedStart=fixed_start,
        fixedEnd=fixed_end,
        deadline=deadline,
        recurrence=_recurrence_draft(item, day),
        recurringTaskId=item.recurring_task_id,
        sourceTaskId=item.source_task_id,
    )


def primary_plan_date(plan: ParsedPlan, ctx: ChatContext) -> date:
    """The day this draft schedules; later named days become deferred tasks."""
    return _layout(plan, ctx)[0]


def _layout(
    plan: ParsedPlan, ctx: ChatContext
) -> tuple[date, list[tuple[str, str]], list[tuple[ParsedTask, date]], list[Assumption]]:
    today = ctx.now.date()
    dated = _task_dates(plan, ctx)
    default_day = today + timedelta(days=max(plan.plan_date_offset, ctx.default_date_offset))
    plan_date = min((day for _, day in dated), default=default_day)
    assumptions: list[Assumption] = []

    windows = list(plan.windows) or _default_windows(ctx, plan_date)
    if not plan.windows and windows:
        assumptions.append(
            Assumption(
                id="a-window",
                kind="WINDOW",
                text=f"Assumed availability {windows[0][0]}–{windows[0][1]}",
            )
        )
    if plan_date == today:
        current_hm = ctx.now.strftime("%H:%M")
        windows = [
            (max(start, current_hm), end) for start, end in windows if end > current_hm
        ]
    # Shift to tomorrow if all windows have expired OR remaining time is < 30 minutes
    if not windows or _total_minutes(windows) < 30:
        had_windows_before = bool(windows)
        tomorrow = today + timedelta(days=1)
        # Only work meant for today moves; later named days keep their date.
        dated = [(task, tomorrow if day == today else day) for task, day in dated]
        plan_date = min((day for _, day in dated), default=tomorrow)
        windows = list(plan.windows) or _default_windows(ctx, plan_date)
        reason = (
            "Moved to tomorrow because remaining time today is very short"
            if had_windows_before
            else "Moved to tomorrow because the window has passed"
        )
        assumptions.append(Assumption(id="a-date", kind="DATE", text=reason))
    return plan_date, windows, dated, assumptions


def assemble_today(
    plan: ParsedPlan,
    ctx: ChatContext,
    carried: Sequence[ParsedTask] = (),
) -> tuple[TodayDraft, list[Assumption]]:
    """Build the draft for the earliest named day.

    ``carried`` holds work that already belongs to that day (deferred tasks and
    recurring occurrences); it is added unless the user named the same task.
    """
    plan_date, windows, dated, layout_assumptions = _layout(plan, ctx)
    assumptions = [
        Assumption(id=f"a-parser-{i}", kind="PARSER", text=text)
        for i, text in enumerate(plan.assumptions)
    ] + layout_assumptions

    today_items = [task for task, day in dated if day == plan_date]
    later_items = [(task, day) for task, day in dated if day != plan_date]
    named = {normalize(task.title) for task in today_items}
    for extra in carried:
        if normalize(extra.title) in named:
            continue
        named.add(normalize(extra.title))
        today_items.append(extra)
        assumptions.append(
            Assumption(
                id=f"a-carried-{len(today_items)}",
                kind="CARRIED",
                text=(
                    f"Added recurring task {extra.title}"
                    if extra.recurring_task_id and not extra.source_task_id
                    else f"Carried over {extra.title} planned for this day"
                ),
            )
        )

    tasks = [
        _task_draft(item, f"d{index}", plan_date, ctx, assumptions)
        for index, item in enumerate(today_items, start=1)
    ]
    deferred = []
    for offset, (item, day) in enumerate(later_items, start=len(tasks) + 1):
        task_id = f"d{offset}"
        deferred.append(
            DeferredTaskDraft(
                task=_task_draft(item, task_id, day, ctx, assumptions),
                targetDate=day,
            )
        )
        assumptions.append(
            Assumption(
                id=f"a-day-{task_id}",
                kind="DATE",
                task_id=task_id,
                text=f"Saved {item.title} for {day.isoformat()}",
            )
        )
    for task in tasks + [item.task for item in deferred]:
        if task.recurrence is not None:
            assumptions.append(
                Assumption(
                    id=f"a-repeat-{task.id}",
                    kind="RECURRENCE",
                    task_id=task.id,
                    text=f"{task.title} repeats: {task.recurrence.label('en')}",
                )
            )

    draft = TodayDraft(
        planDate=plan_date,
        timezone=str(ctx.timezone),
        windows=[
            AvailabilityWindowDraft(start=start, end=end)
            for start, end in windows
            if start < end
        ],
        tasks=tasks,
        deferred_tasks=deferred,
    )
    # The extractor may state the same assumption that deterministic assembly
    # derives from task provenance. Keep the first occurrence and its ordering.
    unique_assumptions: list[Assumption] = []
    seen_assumption_texts: set[str] = set()
    for assumption in assumptions:
        if assumption.text in seen_assumption_texts:
            continue
        seen_assumption_texts.add(assumption.text)
        unique_assumptions.append(assumption)
    return draft, unique_assumptions
