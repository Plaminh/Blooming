from datetime import date, timedelta

from app.ai.handlers.roadmap import roadmap


def test_roadmap_fallback_creates_equal_chronological_milestones():
    today = date.today()
    target = today + timedelta(days=30)
    result = roadmap(
        f"Create goal Learn Python by {target.isoformat()}", "en", today=today
    )
    dates = [milestone.targetDate for milestone in result.draft.milestones]
    assert dates == [
        today + timedelta(days=10),
        today + timedelta(days=20),
        today + timedelta(days=30),
    ]
    assert dates[-1] == result.draft.targetDate
    assert all(milestone.expectedOutcome for milestone in result.draft.milestones)
    assert [(item.kind, item.text) for item in result.assumptions] == [
        ("FRAMEWORK", "Generated using Blooming's default 3-step roadmap framework.")
    ]
