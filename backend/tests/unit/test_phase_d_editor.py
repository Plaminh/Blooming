import pytest
from datetime import date, timedelta
from uuid import uuid4

from app.schemas.drafts import TaskDraft, TodayDraft
from app.schemas.patches import PatchOp
from app.ai.patches import apply_patch
from pydantic import TypeAdapter


def create_test_draft():
    return TodayDraft(
        planDate=date.today(),
        windows=[{"start": "09:00", "end": "17:00"}],
        tasks=[
            TaskDraft(id="d1", title="Read book", durationMin=30, importance="CORE"),
            TaskDraft(
                id="d2", title="Write report", durationMin=60, importance="OPTIONAL"
            ),
            TaskDraft(id="d3", title="Check email", durationMin=45, importance="CORE"),
        ],
    )


def test_ED_011_unknown_id_rejected():
    draft = create_test_draft()
    with pytest.raises(ValueError, match="Task not found"):
        apply_patch(
            draft,
            [
                TypeAdapter(PatchOp).validate_python(
                    {"op": "update_task", "task_id": "unknown", "duration_min": 60}
                )
            ],
        )


def test_ED_012_original_draft_unchanged_after_successful_patch():
    draft = create_test_draft()
    original_dump = draft.model_dump()
    result = apply_patch(
        draft,
        [TypeAdapter(PatchOp).validate_python({"op": "remove_task", "task_id": "d1"})],
    )
    assert result != draft
    assert draft.model_dump() == original_dump


def test_ED_013_original_draft_unchanged_after_failed_patch():
    draft = create_test_draft()
    original_dump = draft.model_dump()
    with pytest.raises(ValueError):
        apply_patch(
            draft,
            [
                TypeAdapter(PatchOp).validate_python(
                    {"op": "update_task", "task_id": "d1", "duration_min": 9999}
                )
            ],
        )
    assert draft.model_dump() == original_dump


def test_ED_014_multi_op_atomic():
    draft = create_test_draft()
    with pytest.raises(ValueError, match="Task not found"):
        apply_patch(
            draft,
            [
                TypeAdapter(PatchOp).validate_python(
                    {"op": "remove_task", "task_id": "d1"}
                ),
                TypeAdapter(PatchOp).validate_python(
                    {"op": "update_task", "task_id": "unknown", "duration_min": 60}
                ),
            ],
        )
    assert len(draft.tasks) == 3


def test_ED_015_existing_ids_stable():
    draft = create_test_draft()
    result = apply_patch(
        draft,
        [
            TypeAdapter(PatchOp).validate_python(
                {"op": "update_task", "task_id": "d1", "title": "New Title"}
            )
        ],
    )
    assert result.tasks[0].id == "d1"
    assert result.tasks[0].title == "New Title"


def test_split_duration_sum_preserved():
    draft = create_test_draft()
    result = apply_patch(
        draft,
        [
            TypeAdapter(PatchOp).validate_python(
                {"op": "split_task", "task_id": "d2", "split_minutes": 20}
            )
        ],
    )
    t1 = next(t for t in result.tasks if t.id == "d2")
    t2 = next(t for t in result.tasks if t.id == "d2-2")
    assert t1.durationMin + t2.durationMin == 60


from app.ai.editor_rules import parse_edit


def test_ED_003_duplicate_title_causes_clarification():
    draft = create_test_draft()
    draft.tasks[2].title = "Write report"
    # "Write report" appears twice
    with pytest.raises(ValueError, match="Which task did you mean?"):
        parse_edit("delete write report", draft)


def test_ED_004_unique_normalized_title_resolves_deterministically():
    draft = create_test_draft()
    ops = parse_edit("delete read book", draft)
    assert ops is not None
    assert ops[0].op == "remove_task"
    assert getattr(ops[0], "task_id") == "d1"


def test_ED_005_unique_article_difference_combines_duration_and_importance():
    draft = create_test_draft()
    ops = parse_edit("Change Read a book to 20 minutes and mark it optional.", draft)
    assert ops is not None
    assert len(ops) == 1
    assert ops[0].task_id == "d1"
    assert ops[0].duration_min == 20
    assert ops[0].importance == "OPTIONAL"


def test_ED_006_article_near_match_requires_unique_candidate():
    draft = create_test_draft()
    draft.tasks.append(
        TaskDraft(id="d4", title="Read Project Book", durationMin=40)
    )
    with pytest.raises(ValueError, match="Which task did you mean"):
        parse_edit("Change Read a book to 20 minutes and mark it optional.", draft)


def test_ED_007_exact_title_still_wins_over_near_candidate():
    draft = create_test_draft()
    draft.tasks.append(
        TaskDraft(id="d4", title="Read Project Book", durationMin=40)
    )
    ops = parse_edit("Change Read Book to 20 minutes", draft)
    assert ops is not None
    assert ops[0].task_id == "d1"


@pytest.mark.asyncio
async def test_ED_deterministic_edit_makes_zero_llm_calls(monkeypatch):
    from datetime import datetime, timezone
    from types import SimpleNamespace
    from unittest.mock import AsyncMock
    from zoneinfo import ZoneInfo

    from app.ai.budget import BudgetMode
    from app.ai.handlers.editor import edit
    from app.ai.providers import llm_provider

    provider_call = AsyncMock()
    monkeypatch.setattr(llm_provider, "call", provider_call)
    monkeypatch.setattr(
        "app.ai.handlers.editor.get_budget_mode",
        AsyncMock(return_value=BudgetMode.NORMAL),
    )
    ctx = SimpleNamespace(
        db=AsyncMock(),
        user_id=uuid4(),
        now=datetime.now(timezone.utc),
        timezone=ZoneInfo("UTC"),
    )

    result = await edit("change task 1 to 45 minutes", create_test_draft(), ctx)

    assert result.draft.tasks[0].durationMin == 45
    assert result.preview is None
    provider_call.assert_not_awaited()


def test_scale_durations_deterministic():
    draft = create_test_draft()
    ops = parse_edit("scale by 1.5", draft)
    assert ops is not None
    assert ops[0].op == "scale_durations"
    assert getattr(ops[0], "factor") == 1.5
