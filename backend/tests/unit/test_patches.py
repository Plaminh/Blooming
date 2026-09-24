from copy import deepcopy
from datetime import date, timedelta
from zoneinfo import ZoneInfo

import pytest
from app.schemas.patches import PatchOp
from pydantic import TypeAdapter
from app.ai.patches import apply_patch
from app.ai.editor_rules import parse_edit
from app.schemas.drafts import TaskDraft, TodayDraft


def draft():
    return TodayDraft(
        planDate="2026-09-21",
        windows=[{"start": "09:00", "end": "12:00"}],
        tasks=[
            TaskDraft(id="d1", title="Read", durationMin=30),
            TaskDraft(id="d2", title="Write", durationMin=45, dependencies=["d1"]),
        ],
    )


def test_patch_is_pure_and_updates_only_target():
    original = draft()
    snapshot = deepcopy(original)
    result = apply_patch(
        original, [TypeAdapter(PatchOp).validate_python(dict(op="update_task", task_id="d1", duration_min=60))]
    )
    assert original == snapshot
    assert result.tasks[0].durationMin == 60
    assert result.tasks[0].estimateSource == "USER"
    assert result.tasks[1] == original.tasks[1]


def test_patch_rejects_removing_dependency():
    with pytest.raises(ValueError, match="required"):
        apply_patch(draft(), [TypeAdapter(PatchOp).validate_python(dict(op="remove_task", task_id="d1"))])


def test_patch_rejects_unknown_task():
    with pytest.raises(ValueError, match="not found"):
        apply_patch(draft(), [TypeAdapter(PatchOp).validate_python(dict(op="remove_task", task_id="missing"))])


def test_editor_matches_a_unique_task_title_and_extended_fields():
    ops = parse_edit("make Write high priority", draft())
    assert ops == [TypeAdapter(PatchOp).validate_python(dict(op="update_task", task_id="d2", priority="HIGH"))]
    result = apply_patch(
        draft(),
        [
            TypeAdapter(PatchOp).validate_python(dict(op="update_task", task_id="d2",
                category="Work",
                break_after_min=10,
            ))
        ],
    )
    assert result.tasks[1].category == "Work"
    assert result.tasks[1].breakAfterMin == 10


def test_add_scale_split_windows_and_date_are_validated_without_mutating_source():
    original = draft()
    target_date = date.today() + timedelta(days=2)
    changed = apply_patch(original, [
        TypeAdapter(PatchOp).validate_python(dict(op="add_task", task=TaskDraft(id="d3", title="Rest", durationMin=20))),
        TypeAdapter(PatchOp).validate_python(dict(op="scale_durations", task_id="d3", factor=1.5)),
        TypeAdapter(PatchOp).validate_python(dict(op="split_task", task_id="d2", split_minutes=20)),
        TypeAdapter(PatchOp).validate_python(dict(op="set_windows", windows=[{"start": "10:00", "end": "15:00"}])),
        TypeAdapter(PatchOp).validate_python(dict(op="set_plan_date", plan_date=target_date)),
    ])
    assert len(original.tasks) == 2
    assert changed.planDate == target_date
    assert changed.windows[0].start == "10:00"
    assert changed.tasks[2].id == "d2-2"
    assert changed.tasks[2].dependencies == ["d2"]
    assert changed.tasks[3].durationMin == 30
    with pytest.raises(ValueError, match="Task ID"):
        apply_patch(changed, [TypeAdapter(PatchOp).validate_python(dict(op="add_task", task=TaskDraft(id="d3", title="Other", durationMin=10)))])


def test_time_patch_uses_draft_timezone_and_keeps_deadline_flexible():
    original = draft().model_copy(update={"timezone": "Asia/Ho_Chi_Minh"})
    changed = apply_patch(original, [TypeAdapter(PatchOp).validate_python(dict(op="update_task", task_id="d1", deadline="18:00", scheduling_type="FLEXIBLE"
    ))])
    assert changed.tasks[0].deadline is not None
    assert changed.tasks[0].deadline.hour == 18
    assert changed.tasks[0].deadline.tzinfo == ZoneInfo("Asia/Ho_Chi_Minh")
    assert changed.tasks[0].schedulingType == "FLEXIBLE"


@pytest.mark.parametrize("field", ["fixed_start", "fixed_end", "deadline"])
def test_time_patch_rejects_invalid_values(field):
    with pytest.raises(ValueError):
        TypeAdapter(PatchOp).validate_python(dict(op="update_task", task_id="d1", **{field: "25:99"}))


def test_time_patch_rejects_unknown_timezone():
    original = draft().model_copy(update={"timezone": "Not/A_Timezone"})
    with pytest.raises(ValueError, match="Unknown draft timezone"):
        apply_patch(original, [TypeAdapter(PatchOp).validate_python(dict(op="update_task", task_id="d1", fixed_start="14:00"))])
