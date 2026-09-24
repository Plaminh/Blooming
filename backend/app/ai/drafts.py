"""Assemble canonical server-owned drafts from parsed plan details."""

from datetime import datetime, timedelta

from app.ai.calibration import apply_multiplier
from app.ai.context import ChatContext
from app.ai.parser import ParsedPlan
from app.schemas.assistant import Assumption
from app.schemas.drafts import AvailabilityWindowDraft, TaskDraft, TodayDraft


def assemble_today(
    plan: ParsedPlan, ctx: ChatContext
) -> tuple[TodayDraft, list[Assumption]]:
    offset = max(plan.plan_date_offset, ctx.default_date_offset)
    plan_date = ctx.now.date() + timedelta(days=offset)
    windows = list(plan.windows or ctx.default_windows)
    assumptions = [
        Assumption(id=f"a-parser-{i}", kind="PARSER", text=text)
        for i, text in enumerate(plan.assumptions)
    ]
    if not plan.windows:
        assumptions.append(
            Assumption(
                id="a-window",
                kind="WINDOW",
                text=f"Assumed availability {windows[0][0]}–{windows[0][1]}",
            )
        )
    if offset == 0:
        current_hm = ctx.now.strftime("%H:%M")
        windows = [
            (max(start, current_hm), end) for start, end in windows if end > current_hm
        ]
    # Shift to tomorrow if all windows have expired OR remaining time is < 30 minutes
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

    if not windows or _total_minutes(windows) < 30:
        had_windows_before = bool(windows)
        offset = 1
        plan_date = ctx.now.date() + timedelta(days=1)
        windows = list(plan.windows or ctx.default_windows)
        reason = (
            "Moved to tomorrow because remaining time today is very short"
            if had_windows_before
            else "Moved to tomorrow because the window has passed"
        )
        assumptions.append(
            Assumption(
                id="a-date",
                kind="DATE",
                text=reason,
            )
        )
    tasks = []
    for index, item in enumerate(plan.tasks, start=1):
        task_id = f"d{index}"
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
                plan_date,
                datetime.strptime(item.fixed_start, "%H:%M").time(),
                tzinfo=ctx.timezone,
            )
            item_fixed_end = getattr(item, "fixed_end", None)
            if item_fixed_end:
                fixed_end = datetime.combine(
                    plan_date,
                    datetime.strptime(item_fixed_end, "%H:%M").time(),
                    tzinfo=ctx.timezone,
                )
            else:
                fixed_end = fixed_start + timedelta(minutes=duration)
        deadline = (
            datetime.combine(
                plan_date,
                datetime.strptime(item.deadline, "%H:%M").time(),
                tzinfo=ctx.timezone,
            )
            if item.deadline
            else None
        )
        tasks.append(
            TaskDraft(
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
    )
    return draft, assumptions
