from unittest.mock import ANY, AsyncMock
from uuid import uuid4

import pytest
from app.ai.router import Route
from app.schemas.assistant import ChatRequest, ChatResponse
from app.schemas.drafts import AvailabilityWindowDraft, TaskDraft, TodayDraft
from app.services import assistant_service


@pytest.mark.asyncio
async def test_rule_intent_never_requires_database_or_provider():
    result = await assistant_service.chat(ChatRequest(message="Hello"))
    assert result.intent == "GREETING"
    assert result.tier == "RULES"


@pytest.mark.asyncio
async def test_goal_without_date_asks_one_question():
    result = await assistant_service.chat(
        ChatRequest(message="Create a goal to learn Python")
    )
    assert result.intent == "CREATE_GOAL"
    assert result.question
    assert result.draft is None


@pytest.mark.asyncio
async def test_plan_delegates_with_trusted_context(monkeypatch):
    db = AsyncMock()
    user_id = uuid4()
    context = object()
    build = AsyncMock(return_value=context)
    planner = AsyncMock(return_value=ChatResponse(reply="draft", intent="PLAN_DAY"))
    monkeypatch.setattr(assistant_service, "build_context", build)
    monkeypatch.setattr(assistant_service, "plan_day", planner)
    result = await assistant_service.chat(
        ChatRequest(message="Plan my day: study 30 min"),
        db=db,
        user_id=user_id,
        timezone="Asia/Ho_Chi_Minh",
    )
    assert result.intent == "PLAN_DAY"
    build.assert_awaited_once()
    planner.assert_awaited_once_with("Plan my day: study 30 min", context, "en", history=None, light=False)


@pytest.mark.asyncio
async def test_edit_delegates_current_draft(monkeypatch):
    draft = TodayDraft(
        planDate="2026-09-21",
        windows=[AvailabilityWindowDraft(start="09:00", end="12:00")],
        tasks=[TaskDraft(id="d1", title="Study", durationMin=30)],
    )
    context = object()
    monkeypatch.setattr(
        assistant_service, "build_context", AsyncMock(return_value=context)
    )
    editor = AsyncMock(
        return_value=ChatResponse(reply="updated", intent="EDIT_DRAFT", draft=draft)
    )
    monkeypatch.setattr(assistant_service, "edit", editor)
    await assistant_service.chat(
        ChatRequest(message="change task 1 to 45 min", current_draft=draft),
        db=AsyncMock(),
        user_id=uuid4(),
    )
    editor.assert_awaited_once_with("change task 1 to 45 min", draft, context, history=None)


@pytest.mark.asyncio
async def test_pending_edit_combines_original_request_with_ordinal_answer(monkeypatch):
    draft = _existing_draft()
    context = object()
    monkeypatch.setattr(assistant_service, "build_context", AsyncMock(return_value=context))
    editor = AsyncMock(return_value=ChatResponse(reply="updated", intent="EDIT_DRAFT", draft=draft))
    monkeypatch.setattr(assistant_service, "edit", editor)

    await assistant_service.chat(
        ChatRequest(message="First one.", current_draft=draft),
        db=AsyncMock(), user_id=uuid4(), pending_intent="EDIT_DRAFT",
        pending_message="Change Review notes to 20 minutes.",
    )

    editor.assert_awaited_once_with(
        "Change Review notes to 20 minutes.\nFirst one.",
        draft, context, history=None,
    )


@pytest.mark.asyncio
async def test_explicit_today_plan_replaces_conflicting_draft_and_pending_edit(monkeypatch):
    old_draft = TodayDraft(
        planDate="2026-09-25",
        windows=[AvailabilityWindowDraft(start="09:00", end="12:00")],
        tasks=[
            TaskDraft(
                id="old-1", title="Old fixed task", durationMin=60,
                schedulingType="FIXED", fixedStart="2026-09-25T09:00:00",
                fixedEnd="2026-09-25T10:00:00",
            ),
            TaskDraft(
                id="old-2", title="Conflicting fixed task", durationMin=60,
                schedulingType="FIXED", fixedStart="2026-09-25T09:30:00",
                fixedEnd="2026-09-25T10:30:00",
            ),
        ],
    )
    new_draft = TodayDraft(
        planDate="2026-09-25",
        windows=[AvailabilityWindowDraft(start="19:00", end="21:00")],
        tasks=[TaskDraft(id="new-1", title="Review database systems", durationMin=60)],
    )
    planner = AsyncMock(return_value=ChatResponse(
        reply="Draft ready", intent="PLAN_DAY", draft=new_draft, preview=None,
    ))
    monkeypatch.setattr(assistant_service, "build_context", AsyncMock(return_value=object()))
    monkeypatch.setattr(assistant_service, "plan_day", planner)

    result = await assistant_service.chat(
        ChatRequest(
            message="Today from 7 PM to 9 PM, review database systems for 1 hour.",
            current_draft=old_draft,
        ),
        db=AsyncMock(),
        user_id=uuid4(),
        history=[{"role": "user", "content": "Change the conflicting task."}],
        pending_intent="EDIT_DRAFT",
        pending_message="Change the conflicting task.",
    )

    assert result.intent == "PLAN_DAY"
    assert result.draft == new_draft
    assert result.preview is None
    assert [task.title for task in result.draft.tasks] == ["Review database systems"]
    planner.assert_awaited_once_with(
        "Today from 7 PM to 9 PM, review database systems for 1 hour.",
        ANY,
        "en",
        history=None,
        light=False,
    )


def _existing_draft() -> TodayDraft:
    return TodayDraft(
        planDate="2026-09-21",
        windows=[AvailabilityWindowDraft(start="09:00", end="12:00")],
        tasks=[TaskDraft(id="d1", title="Study", durationMin=30)],
    )


@pytest.mark.asyncio
@pytest.mark.parametrize(
    ("message", "current_draft", "expected_intent"),
    [
        ("What can you help me plan?", None, "HELP_FEATURE"),
        ("What can you do?", None, "HELP_FEATURE"),
        ("Thanks", _existing_draft(), "THANKS"),
        ("What can you help me plan?", _existing_draft(), "HELP_FEATURE"),
    ],
)
async def test_conversation_does_not_create_or_mutate_draft(
    monkeypatch, message, current_draft, expected_intent
):
    build_context = AsyncMock()
    planner = AsyncMock()
    editor = AsyncMock()
    monkeypatch.setattr(assistant_service, "build_context", build_context)
    monkeypatch.setattr(assistant_service, "plan_day", planner)
    monkeypatch.setattr(assistant_service, "edit", editor)

    original = current_draft.model_dump() if current_draft else None
    result = await assistant_service.chat(
        ChatRequest(message=message, current_draft=current_draft)
    )

    assert result.intent == expected_intent
    assert result.draft is None
    if current_draft:
        assert current_draft.model_dump() == original
    build_context.assert_not_awaited()
    planner.assert_not_awaited()
    editor.assert_not_awaited()


@pytest.mark.asyncio
async def test_real_planning_request_still_creates_today_draft(monkeypatch):
    draft = _existing_draft()
    planner = AsyncMock(
        return_value=ChatResponse(reply="draft", intent="PLAN_DAY", draft=draft)
    )
    monkeypatch.setattr(
        assistant_service, "build_context", AsyncMock(return_value=object())
    )
    monkeypatch.setattr(assistant_service, "plan_day", planner)

    result = await assistant_service.chat(
        ChatRequest(message="Plan reading for 30 minutes today"),
        db=AsyncMock(),
        user_id=uuid4(),
    )

    assert result.intent == "PLAN_DAY"
    assert result.draft == draft
    planner.assert_awaited_once()


@pytest.mark.asyncio
async def test_parse_04_short_task_reaches_planner_and_keeps_estimate_provenance(monkeypatch):
    draft = TodayDraft(
        planDate="2026-09-25",
        windows=[AvailabilityWindowDraft(start="09:00", end="17:00")],
        tasks=[
            TaskDraft(
                id="d1",
                title="Organize Zarkon materials",
                durationMin=45,
                estimateSource="AI",
            )
        ],
    )
    classify = AsyncMock(return_value=Route("PLAN_DAY", 0.75, "llm"))
    planner = AsyncMock(
        return_value=ChatResponse(
            reply="Draft ready",
            intent="PLAN_DAY",
            draft=draft,
            assumptions=[{
                "id": "a-duration-d1",
                "kind": "DURATION",
                "task_id": "d1",
                "text": "Estimated 45 minutes for Organize Zarkon materials",
            }],
        )
    )
    monkeypatch.setattr(assistant_service, "classify_low_confidence", classify)
    monkeypatch.setattr(assistant_service, "build_context", AsyncMock(return_value=object()))
    monkeypatch.setattr(assistant_service, "plan_day", planner)

    result = await assistant_service.chat(
        ChatRequest(message="Organize Zarkon materials."),
        db=AsyncMock(),
        user_id=uuid4(),
    )

    classify.assert_awaited_once()
    planner.assert_awaited_once()
    assert result.intent == "PLAN_DAY"
    assert result.draft is not None
    assert result.draft.tasks[0].title == "Organize Zarkon materials"
    assert result.draft.tasks[0].durationMin == 45
    assert result.draft.tasks[0].estimateSource == "AI"
    assert result.draft.tasks[0].fixedStart is None
    assert result.draft.tasks[0].deadline is None
    assert result.assumptions[0].text.startswith("Estimated 45 minutes")
    planner.assert_awaited_once_with(
        "Organize Zarkon materials.",
        ANY,
        "en",
        history=None,
        light=False,
    )
