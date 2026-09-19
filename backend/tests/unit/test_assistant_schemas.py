import ast
from pathlib import Path
from uuid import uuid4

import pytest
from pydantic import ValidationError

from app.schemas import assistant
from app.schemas.today import TodayResponse


def test_assistant_draft_models_are_canonical_and_expose_service_fields():
    source = Path(assistant.__file__).read_text(encoding="utf-8")
    definitions = [node.name for node in ast.parse(source).body if isinstance(node, ast.ClassDef)]
    for name in ("AvailabilityWindowDraft", "TaskDraft", "TodayDraft"):
        assert definitions.count(name) == 1

    task = assistant.TaskDraft(id="draft-1", title="Review", durationMin=30)
    for field in (
        "id", "title", "durationMin", "priority", "deadline", "schedulingType",
        "fixedStart", "fixedEnd", "dependencies", "splittable",
    ):
        assert hasattr(task, field)

    with pytest.raises(ValidationError):
        assistant.TaskDraft(title="Review", durationMin=30)
    with pytest.raises(ValidationError):
        assistant.TaskDraft(id="draft-1", title="Review", durationMin=0)


def test_existing_chat_and_today_response_shapes_remain_valid():
    chat = assistant.ChatResponse.model_validate({
        "reply": "Here is your plan.",
        "draft": {
            "type": "today",
            "availability": {"start": "09:00", "end": "12:00", "totalHours": 3},
            "tasks": [{"title": "Write report", "durationMin": 90, "priority": "Core"}],
        },
    })
    assert chat.draft.tasks[0].title == "Write report"

    task_id = uuid4()
    response = TodayResponse(plan_date="2026-09-19", status="ACTIVE", unscheduled_tasks=[task_id])
    assert response.unscheduled_tasks == [task_id]
