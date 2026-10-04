import pytest
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


@pytest.mark.parametrize(
    "message,intent",
    [
        ("Tôi muốn học xong IELTS 7.0 trước 2026-12-29", "CREATE_GOAL"),
        ("Mục tiêu của tôi là chạy 10km trước 31/12/2026", "CREATE_GOAL"),
        ("Tôi muốn học toán 1h", "PLAN_DAY"),
        ("Mục tiêu của tôi", "STATUS_GOALS"),
    ],
)
def test_vietnamese_goal_with_deadline_starts_a_roadmap(message, intent):
    from app.ai.nlu.router import route

    assert route(message).intent == intent


def test_vietnamese_roadmap_reads_naturally():
    from app.ai.handlers.roadmap import roadmap

    response = roadmap("Tôi muốn học xong IELTS 7.0 trước 2026-12-29", "vi", today=date(2026, 9, 30))
    assert response.draft.goalTitle == "học xong IELTS 7.0"
    assert response.draft.milestones[0].title == "Xác định phạm vi: học xong IELTS 7.0"
    assert response.reply.startswith("Mình đã tạo lộ trình nháp")
