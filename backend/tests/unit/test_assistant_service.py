from unittest.mock import AsyncMock
from uuid import uuid4

import pytest
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
