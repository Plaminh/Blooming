import ast
from pathlib import Path
from uuid import uuid4

import pytest
from pydantic import ValidationError

from app.schemas import assistant, drafts
from app.schemas.today import TodayResponse


def test_assistant_draft_models_are_canonical_and_expose_service_fields():
    source = Path(drafts.__file__).read_text(encoding="utf-8")
    definitions = [node.name for node in ast.parse(source).body if isinstance(node, ast.ClassDef)]
    for name in ("AvailabilityWindowDraft", "TaskDraft", "TodayDraft"):
        assert definitions.count(name) == 1

    task = drafts.TaskDraft(id="draft-1", title="Review", durationMin=30)
    for field in (
        "id", "title", "durationMin", "priority", "deadline", "schedulingType",
        "fixedStart", "fixedEnd", "dependencies", "splittable",
    ):
        assert hasattr(task, field)

    with pytest.raises(ValidationError):
        drafts.TaskDraft(title="Review", durationMin=30)
    with pytest.raises(ValidationError):
        drafts.TaskDraft(id="draft-1", title="Review", durationMin=0)


def test_existing_chat_and_today_response_shapes_remain_valid():
    chat = assistant.ChatResponse.model_validate({
        "reply": "Here is your plan.",
        "draft": {
            "type": "today",
            "planDate": "2026-09-20",
            "windows": [{"start": "09:00", "end": "12:00"}],
            "tasks": [{"title": "Write report", "durationMin": 90, "id": "t1", "priority": "MEDIUM"}],
        },
    })
    assert chat.draft.tasks[0].title == "Write report"

    task_id = uuid4()
    response = TodayResponse(plan_date="2026-09-19", status="ACTIVE", unscheduled_tasks=[task_id])
    assert response.unscheduled_tasks == [task_id]


def test_chat_contract_keeps_current_draft_and_response_metadata():
    request = assistant.ChatRequest.model_validate(
        {
            "message": "change task 1 to 45 min",
            "current_draft": {
                "type": "today",
                "planDate": "2026-09-20",
                "windows": [{"start": "09:00", "end": "12:00"}],
                "tasks": [{"id": "d1", "title": "Read", "durationMin": 30}],
            },
        }
    )
    assert request.current_draft is not None
    response = assistant.ChatResponse(
        reply="Updated", intent="EDIT_DRAFT", tier="RULES", degraded="LEAN"
    )
    assert response.model_dump()["intent"] == "EDIT_DRAFT"
    assert response.model_dump()["tier"] == "RULES"
    assert response.model_dump()["degraded"] == "LEAN"

def test_availability_window_draft_validation():
    with pytest.raises(ValidationError):
        drafts.AvailabilityWindowDraft(start="10:00", end="09:00")
        
def test_clean_availability_windows():
    from datetime import datetime
    now = datetime(2026, 9, 20, 10, 30)
    windows = [
        drafts.AvailabilityWindowDraft(start="08:00", end="09:00"), # Past
        drafts.AvailabilityWindowDraft(start="09:00", end="12:00"), # Overlapping
        drafts.AvailabilityWindowDraft(start="14:00", end="16:00"), # Future
    ]
    cleaned = drafts.clean_availability_windows(windows, now)
    assert len(cleaned) == 2
    assert cleaned[0].start == "10:30"
    assert cleaned[0].end == "12:00"
    assert cleaned[1].start == "14:00"
    assert cleaned[1].end == "16:00"

def test_roadmap_draft_validation():
    from datetime import date, timedelta
    today = date.today()
    past = today - timedelta(days=1)
    future = today + timedelta(days=10)
    
    # Zero milestones
    with pytest.raises(ValidationError, match="least 1 milestone"):
        drafts.RoadmapDraft(type="roadmap", goalTitle="Goal", targetDate=future, milestones=[])
        
    # Too many milestones
    milestones = [drafts.MilestoneDraft(title=f"M{i}", targetDate=future) for i in range(13)]
    with pytest.raises(ValidationError, match="most 12 milestones"):
        drafts.RoadmapDraft(type="roadmap", goalTitle="Goal", targetDate=future, milestones=milestones)
        
    # Past targets
    with pytest.raises(ValidationError, match="past"):
        drafts.RoadmapDraft(type="roadmap", goalTitle="Goal", targetDate=past, milestones=[
            drafts.MilestoneDraft(title="M1", targetDate=past)
        ])
        
    # Unordered milestones (should be sorted automatically)
    m1 = drafts.MilestoneDraft(title="M1", targetDate=today + timedelta(days=2))
    m2 = drafts.MilestoneDraft(title="M2", targetDate=today + timedelta(days=1))
    roadmap = drafts.RoadmapDraft(type="roadmap", goalTitle="Goal", targetDate=future, milestones=[m1, m2])
    assert roadmap.milestones[0].title == "M2"
    assert roadmap.milestones[1].title == "M1"
    
    # Out of bounds milestones
    m3 = drafts.MilestoneDraft(title="M3", targetDate=future + timedelta(days=1))
    with pytest.raises(ValidationError, match="after roadmap target date"):
        drafts.RoadmapDraft(type="roadmap", goalTitle="Goal", targetDate=future, milestones=[m3])
