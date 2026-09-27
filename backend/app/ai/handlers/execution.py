"""Zero-token execution helpers: end-of-day review and completing tasks from chat.

Both work only on the persisted plan. Completing a task is an execution
mutation (like "Mark complete" on Today): it never changes plan structure.
"""

import re
from datetime import datetime
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.ai.router import normalize
from app.schemas.assistant import ChatResponse, QuickReply
from app.schemas.today import TodayTaskStatusUpdate
from app.services import statistics_service
from app.services.today_service import today_service

DONE_STATUSES = {"COMPLETED"}
CLOSED_STATUSES = {"COMPLETED", "SKIPPED", "CANCELLED"}
# Words that say *that* something is done, not *which* task it was.
_COMPLETION_WORDS = re.compile(
    r"\b(da|vua|moi|lam|xong|roi|hoan thanh|het|cai|viec|bai|nay|do|nhe|nha|minh|toi|em"
    r"|i|i'm|im|am|have|just|finished|finish|completed|complete|done|with|the|my|task|it)\b"
)


def _task_blocks(today: dict) -> list[dict]:
    """One entry per task in plan order (a split task has several blocks)."""
    seen: dict = {}
    for block in today.get("blocks", []):
        task_id = block.get("task_id")
        if block.get("block_type") != "TASK" or not task_id or task_id in seen:
            continue
        seen[task_id] = block
    return list(seen.values())


def _duration_text(minutes: int, lang: str) -> str:
    hours, rest = divmod(max(0, minutes), 60)
    if lang == "vi":
        return f"{hours} giờ {rest} phút" if hours else f"{rest} phút"
    return f"{hours}h {rest}m" if hours else f"{rest} min"


async def day_review(
    db: AsyncSession, user_id: UUID, now: datetime, lang: str
) -> ChatResponse:
    vi = lang == "vi"
    today = await today_service.get_today(db, user_id, now.date())
    if today["status"] == "NO_PLAN":
        reply = (
            "Hôm nay bạn chưa có kế hoạch nên chưa có gì để tổng kết."
            if vi
            else "There is no plan for today yet, so there is nothing to review."
        )
        return ChatResponse(
            reply=reply, intent="DAY_REVIEW", tier="RULES",
            suggestions=[QuickReply(
                label="Lập lịch hôm nay" if vi else "Plan my day",
                send_text="Lập lịch hôm nay" if vi else "Plan my day",
            )],
        )
    tasks = _task_blocks(today)
    done = [t for t in tasks if t.get("status") in DONE_STATUSES]
    open_tasks = [t for t in tasks if t.get("status") not in CLOSED_STATUSES]
    stats = await statistics_service.get_statistics_summary(db, user_id, now.date(), now.date())
    focus_minutes = stats.study_time_hours * 60 + stats.study_time_minutes
    if vi:
        reply = (
            f"Hôm nay bạn đã xong {len(done)}/{len(tasks)} việc và tập trung "
            f"{_duration_text(focus_minutes, lang)}."
        )
    else:
        reply = (
            f"Today you finished {len(done)} of {len(tasks)} tasks and focused for "
            f"{_duration_text(focus_minutes, lang)}."
        )
    suggestions: list[QuickReply] = []
    if open_tasks:
        names = ", ".join(t["title"] for t in open_tasks[:4]) + ("…" if len(open_tasks) > 4 else "")
        reply += (
            f" Còn {len(open_tasks)} việc chưa xong: {names}."
            if vi
            else f" Still open: {names}."
        )
        suggestions.append(QuickReply(
            label="Dời việc chưa xong sang mai" if vi else "Move unfinished to tomorrow",
            action="CARRY_OVER_UNFINISHED",
        ))
        if now.hour < 21:
            suggestions.append(QuickReply(
                label="Xếp lại phần còn lại" if vi else "Replan the rest of today",
                action="REPLAN_TODAY",
            ))
    elif tasks:
        reply += " Bạn đã hoàn thành mọi việc, tuyệt lắm!" if vi else " Everything is done. Great work!"
    return ChatResponse(reply=reply, intent="DAY_REVIEW", tier="RULES", suggestions=suggestions)


def _named_part(message: str) -> set[str]:
    """Words of the message that could name a task."""
    text = _COMPLETION_WORDS.sub(" ", normalize(message))
    return set(re.findall(r"[a-z0-9]+", text))


def _match(tasks: list[dict], message: str) -> list[dict]:
    wanted = _named_part(message)
    if not wanted:
        return []
    exact = [t for t in tasks if normalize(t["title"]) in normalize(message)]
    if exact:
        return exact
    scored = []
    for task in tasks:
        tokens = set(re.findall(r"[a-z0-9]+", normalize(task["title"])))
        overlap = len(tokens & wanted)
        if overlap:
            scored.append((overlap / len(tokens | wanted), task))
    if not scored:
        return []
    best = max(score for score, _ in scored)
    return [task for score, task in scored if score == best]


async def complete_task(
    db: AsyncSession, user_id: UUID, now: datetime, message: str, lang: str
) -> ChatResponse:
    vi = lang == "vi"
    today = await today_service.get_today(db, user_id, now.date())
    open_tasks = [
        t for t in _task_blocks(today) if t.get("status") not in CLOSED_STATUSES
    ] if today["status"] != "NO_PLAN" else []
    if not open_tasks:
        reply = (
            "Mình không thấy việc nào đang mở trong kế hoạch hôm nay."
            if vi
            else "I can't find any open task in today's plan."
        )
        return ChatResponse(reply=reply, intent="COMPLETE_TASK", tier="RULES")
    matches = _match(open_tasks, message)
    if len(matches) != 1:
        choices = matches or open_tasks
        question = "Bạn vừa xong việc nào?" if vi else "Which task did you finish?"
        return ChatResponse(
            reply=question, question=question, intent="COMPLETE_TASK", tier="RULES",
            suggestions=[
                QuickReply(
                    label=(f"Xong: {t['title']}" if vi else f"Done: {t['title']}")[:80],
                    send_text=(f"Đã xong {t['title']}" if vi else f"Done with {t['title']}"),
                )
                for t in choices[:4]
            ],
        )
    task = matches[0]
    await today_service.update_task_status_from_today(
        db, user_id, task["task_id"], TodayTaskStatusUpdate(status="COMPLETED"), commit=False
    )
    remaining = [t for t in open_tasks if t["task_id"] != task["task_id"]]
    reply = (
        f"Tuyệt! Đã đánh dấu xong \"{task['title']}\" (+1 Leaf)."
        if vi
        else f"Nice! Marked \"{task['title']}\" as done (+1 Leaf)."
    )
    if remaining:
        upcoming = min(remaining, key=lambda t: t["planned_start_at"])
        start = upcoming["planned_start_at"]
        clock = start.strftime("%H:%M") if hasattr(start, "strftime") else str(start)[11:16]
        reply += (
            f" Tiếp theo: {upcoming['title']} lúc {clock}."
            if vi
            else f" Next: {upcoming['title']} at {clock}."
        )
    else:
        reply += " Bạn đã xong hết việc hôm nay!" if vi else " That was the last task today!"
    return ChatResponse(reply=reply, intent="COMPLETE_TASK", tier="RULES")
