from datetime import date

from app.ai.drafting.validators import check_today
from app.schemas.drafts import AvailabilityWindowDraft, TaskDraft, TodayDraft


def test_validation_catches_duplicates_and_cycle():
    draft = TodayDraft(
        planDate=date(2026, 9, 20),
        timezone="UTC",
        windows=[AvailabilityWindowDraft(start="09:00", end="12:00")],
        tasks=[
            TaskDraft(id="a", title="Study", durationMin=60, dependencies=["b"]),
            TaskDraft(id="b", title="study", durationMin=30, dependencies=["a"]),
        ],
    )
    issues = check_today(draft)
    assert "DUPLICATE_TITLE" in issues
    assert "CYCLIC_DEPENDENCY" in issues


def test_validation_rejects_missing_fixed_times():
    draft = TodayDraft(
        planDate=date(2026, 9, 20),
        timezone="UTC",
        windows=[AvailabilityWindowDraft(start="09:00", end="12:00")],
        tasks=[
            TaskDraft(id="a", title="Meeting", durationMin=45, schedulingType="FIXED")
        ],
    )
    assert check_today(draft) == ["INVALID_FIXED_TIME"]
