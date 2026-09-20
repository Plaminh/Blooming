from datetime import date
from uuid import uuid4
from zoneinfo import ZoneInfo

from app.schemas.drafts import AvailabilityWindowDraft, TaskDraft, TodayDraft
from app.services.today_service import today_service


def test_break_after_minutes_reaches_scheduler():
    draft = TodayDraft(
        planDate=date(2026, 9, 20),
        timezone="UTC",
        windows=[AvailabilityWindowDraft(start="09:00", end="12:00")],
        tasks=[TaskDraft(id="work", title="Work", durationMin=60, breakAfterMin=10)],
    )
    result, _, _ = today_service._normalize_and_schedule(
        draft,
        ZoneInfo("UTC"),
        draft.planDate,
        uuid4(),
    )
    breaks = [block for block in result.blocks if block.block_type == "BREAK"]
    assert any(
        (block.end_at - block.start_at).total_seconds() == 600 for block in breaks
    )
