"""Deterministic roadmap fallback for explicit target dates."""

import re
from datetime import date, timedelta

from app.ai.handlers.clarify import missing_goal_target_date
from app.schemas.assistant import ChatResponse, QuickReply
from app.schemas.drafts import MilestoneDraft, RoadmapDraft


def roadmap(message: str, lang: str, *, today: date) -> ChatResponse:
    match = re.search(r"\b(20\d{2}-\d{2}-\d{2})\b", message)
    target: date | None
    if match:
        target = date.fromisoformat(match.group(1))
    else:
        match = re.search(r"\b(\d{1,2})/(\d{1,2})/(20\d{2})\b", message)
        target = date(int(match.group(3)), int(match.group(2)), int(match.group(1))) if match else None
    if target is None or target < today:
        return missing_goal_target_date(lang)
    title = re.sub(r"\b(?:20\d{2}-\d{2}-\d{2}|\d{1,2}/\d{1,2}/20\d{2})\b", "", message)
    title = re.sub(r"(?i)\b(i want to|create|goal|roadmap|target|by|mục tiêu|tạo|đến ngày)\b", " ", title)
    title = re.sub(r"\s+", " ", title).strip(" .,:-") or ("Mục tiêu mới" if lang == "vi" else "New goal")
    total_days = max(0, (target - today).days)
    milestone_count = min(3, max(1, total_days))
    labels = (
        ["Complete"]
        if milestone_count == 1
        else ["Define scope", "Build momentum", "Complete"][-milestone_count:]
    )
    milestones = []
    for index in range(1, milestone_count + 1):
        offset = round(total_days * index / milestone_count)
        milestone_date = today + timedelta(days=offset)
        label = labels[index - 1]
        milestones.append(
            MilestoneDraft(
                id=f"m{index}",
                title=f"{label}: {title}"[:200],
                targetDate=milestone_date,
                expectedOutcome=f"{label} milestone completed",
            )
        )
    draft = RoadmapDraft(
        type="roadmap",
        goalTitle=title[:200],
        targetDate=target,
        milestones=milestones,
    )
    return ChatResponse(
        reply="I created a roadmap draft. Review it before saving.",
        intent="CREATE_GOAL", tier="RULES", draft=draft,
        suggestions=[QuickReply(label="Save to goals", action="SAVE_ROADMAP")],
    )
