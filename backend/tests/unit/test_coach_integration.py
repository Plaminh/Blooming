from datetime import date, datetime
from uuid import uuid4
from zoneinfo import ZoneInfo

from app.schemas.drafts import TodayDraft, TaskDraft, AvailabilityWindowDraft
from app.schemas.patches import PatchOp
from app.ai.drafting.patches import apply_patch
from pydantic import TypeAdapter

patch_adapter = TypeAdapter(PatchOp)
from app.services.today_service import today_service
from app.ai.drafting.validators import check_today
from app.ai.coach.coach import generate_overloaded_suggestions

from dataclasses import dataclass


@dataclass
class MockCtx:
    now: datetime
    timezone: ZoneInfo = ZoneInfo("UTC")


def _tz():
    return ZoneInfo("UTC")


def _draft(tasks, windows=None):
    return TodayDraft(
        planDate=date(2026, 9, 20),
        timezone="UTC",
        windows=windows or [AvailabilityWindowDraft(start="09:00", end="10:00")],
        tasks=tasks,
    )


def _task(
    id_,
    title,
    duration_min,
    importance="CORE",
    priority="MEDIUM",
    estimate_source="USER",
    scheduling_type="FLEXIBLE",
    dependencies=None,
    splittable=False,
):
    return TaskDraft(
        id=id_,
        title=title,
        durationMin=duration_min,
        importance=importance,
        priority=priority,
        estimateSource=estimate_source,
        schedulingType=scheduling_type,
        dependencies=dependencies or [],
        splittable=splittable,
    )


def preview(draft):
    result, reality_check, draft_to_uuid = today_service._normalize_and_schedule(
        draft, _tz(), draft.planDate, uuid4()
    )
    uuid_to_draft = {v: k for k, v in draft_to_uuid.items()}
    result.unscheduled_tasks = [
        uuid_to_draft.get(u, u) for u in result.unscheduled_tasks
    ]
    return result, reality_check


def test_coach_integration_remove_optional():
    draft = _draft(
        windows=[AvailabilityWindowDraft(start="09:00", end="10:00")],
        tasks=[
            _task("t1", "Core task", 30, importance="CORE"),
            _task("t2", "Optional task", 45, importance="OPTIONAL"),
        ],
    )
    result, reality_check = preview(draft)
    assert reality_check == "OVERLOADED"

    ctx = MockCtx(now=datetime(2026, 9, 20, 10, 0))
    unscheduled_ids = [str(u) for u in result.unscheduled_tasks]
    suggestions = generate_overloaded_suggestions(draft, ctx, unscheduled_ids)
    remove_sug = next(
        s for s in suggestions if s["label"].startswith("Remove optional")
    )

    ops = [patch_adapter.validate_python(op) for op in remove_sug["patch"]]
    patched = apply_patch(draft, ops)
    assert not check_today(patched)

    new_result, new_reality = preview(patched)
    assert new_reality in ("COMFORTABLE", "TIGHT")
    assert len(patched.tasks) == 1
    assert patched.tasks[0].id == "t1"


def test_coach_integration_move_tomorrow():
    draft = _draft(
        windows=[AvailabilityWindowDraft(start="09:00", end="10:00")],
        tasks=[
            _task("t1", "Task 1", 45),
            _task("t2", "Task 2", 30, importance="OPTIONAL"),
        ],
    )
    result, reality_check = preview(draft)
    assert reality_check == "OVERLOADED"

    ctx = MockCtx(now=datetime(2026, 9, 20, 10, 0))
    unscheduled_ids = [str(u) for u in result.unscheduled_tasks]
    suggestions = generate_overloaded_suggestions(draft, ctx, unscheduled_ids)
    move_sug = next(s for s in suggestions if s["label"].startswith("Move to tomorrow"))
    ops = [patch_adapter.validate_python(op) for op in move_sug["patch"]]

    patched = apply_patch(draft, ops)
    assert not check_today(patched)

    new_result, new_reality = preview(patched)
    assert new_reality in ("COMFORTABLE", "TIGHT")

    assert len(patched.tasks) == 1
    assert len(patched.deferred_tasks) == 1
    deferred = patched.deferred_tasks[0]
    assert deferred.targetDate == date(2026, 9, 21)


def test_coach_integration_extend_availability():
    draft = _draft(
        windows=[AvailabilityWindowDraft(start="09:00", end="10:00")],
        tasks=[_task("t1", "Task 1", 75)],
    )
    result, reality_check = preview(draft)
    assert reality_check == "OVERLOADED"

    ctx = MockCtx(now=datetime(2026, 9, 20, 10, 0))
    unscheduled_ids = [str(u) for u in result.unscheduled_tasks]
    suggestions = generate_overloaded_suggestions(draft, ctx, unscheduled_ids)
    extend_sug = next(
        s for s in suggestions if s["label"].startswith("Extend availability")
    )
    ops = [patch_adapter.validate_python(op) for op in extend_sug["patch"]]

    patched = apply_patch(draft, ops)
    assert not check_today(patched)

    assert patched.windows[0].start == "09:00"
    assert patched.windows[0].end == "10:30"

    new_result, new_reality = preview(patched)
    assert new_reality in ("COMFORTABLE", "TIGHT")


def test_coach_integration_reduce_duration():
    draft = _draft(
        windows=[AvailabilityWindowDraft(start="09:00", end="10:00")],
        tasks=[
            _task("t1", "Task 1", 75, estimate_source="RULE", importance="OPTIONAL")
        ],
    )
    result, reality_check = preview(draft)
    assert reality_check == "OVERLOADED"

    ctx = MockCtx(now=datetime(2026, 9, 20, 10, 0))
    unscheduled_ids = [str(u) for u in result.unscheduled_tasks]
    suggestions = generate_overloaded_suggestions(draft, ctx, unscheduled_ids)
    reduce_sug = next(s for s in suggestions if s["label"].startswith("Reduce "))
    ops = [patch_adapter.validate_python(op) for op in reduce_sug["patch"]]

    patched = apply_patch(draft, ops)
    assert not check_today(patched)
    assert patched.tasks[0].durationMin == 37
    assert patched.tasks[0].id == "t1"

    new_result, new_reality = preview(patched)
    assert new_reality in ("COMFORTABLE", "TIGHT")


def test_coach_integration_split_long_task():
    draft = _draft(
        windows=[
            AvailabilityWindowDraft(start="09:00", end="10:00"),
            AvailabilityWindowDraft(start="11:00", end="12:00"),
        ],
        tasks=[_task("t1", "Task 1", 120, splittable=False)],
    )
    result, reality_check = preview(draft)
    assert reality_check == "OVERLOADED"

    ctx = MockCtx(now=datetime(2026, 9, 20, 10, 0))
    unscheduled_ids = [str(u) for u in result.unscheduled_tasks]
    suggestions = generate_overloaded_suggestions(draft, ctx, unscheduled_ids)
    split_sug = next(s for s in suggestions if s["label"].startswith("Split "))
    ops = [patch_adapter.validate_python(op) for op in split_sug["patch"]]

    patched = apply_patch(draft, ops)
    assert not check_today(patched)
    assert len(patched.tasks) == 1
    assert patched.tasks[0].splittable == True
    assert patched.tasks[0].durationMin == 120

    new_result, new_reality = preview(patched)
    assert new_reality in ("COMFORTABLE", "TIGHT")
