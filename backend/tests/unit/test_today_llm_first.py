"""Comprehensive tests for LLM-first Today planning refactor.

Covers Task Groups:
- Group 2: LLM structured extraction schema & validation
- Group 3: Disallowing application-owned fields
- Group 4: Deterministic TodayDraft assembly & authority
- Group 5: Natural-language robustness with semantic variations
- Group 6: Invalid LLM output and single-turn repair
- Group 7: Provider failure and degraded parser fallback
- Group 8: Clarification fallback (no fake tasks invented)
- Group 9: Scheduler boundary regression (preview = null)
- Group 10: Persistence boundary regression (no domain writes)
"""

from __future__ import annotations

import pytest
from dataclasses import replace
from datetime import datetime
from unittest.mock import AsyncMock, patch, MagicMock
from uuid import uuid4
from zoneinfo import ZoneInfo
from pydantic import ValidationError

from app.ai.budget import BudgetMode
from app.ai.context import ChatContext
from app.ai.handlers import planner
from app.ai.handlers.planner import LLMDayPlan, LLMTask, _parsed_from_llm
from app.ai.providers import LLMError
from app.ai.validators import check_today


@pytest.fixture
def base_context():
    mock_session = AsyncMock()
    mock_session.add = MagicMock()
    mock_session.add_all = MagicMock()
    mock_session.flush = AsyncMock()
    mock_session.commit = AsyncMock()

    return ChatContext(
        db=mock_session,
        user_id=uuid4(),
        now=datetime(2026, 9, 25, 9, 0, tzinfo=ZoneInfo("Asia/Ho_Chi_Minh")),
        timezone=ZoneInfo("Asia/Ho_Chi_Minh"),
        break_minutes=5,
        default_windows=(("08:00", "18:00"),),
        default_date_offset=0,
    )


# ===========================================================================
# Group 2 & 3: LLM Structured Extraction Schema & Application-Owned Fields
# ===========================================================================

def test_schema_valid_tasks_and_windows():
    """Valid tasks, availability windows, fixed times, and deadlines validate cleanly."""
    data = {
        "reply": "Here is your plan for the day.",
        "windows": [("13:00", "17:00")],
        "tasks": [
            {
                "title": "Deep work on architecture",
                "duration_min": 120,
                "priority": "HIGH",
                "importance": "CORE",
                "category": "Work",
                "fixed_start": "13:00",
                "fixed_end": "15:00",
                "deadline": "15:00",
            },
            {
                "title": "Read technical documentation",
                "duration_min": 30,
                "priority": "LOW",
                "importance": "OPTIONAL",
                "category": "Learning",
            },
        ],
        "assumptions": ["Focus block planned in the afternoon."],
    }
    plan = LLMDayPlan.model_validate(data)
    assert len(plan.tasks) == 2
    assert plan.tasks[0].duration_min == 120
    assert plan.tasks[0].fixed_start == "13:00"
    assert plan.tasks[1].importance == "OPTIONAL"
    assert plan.windows == [("13:00", "17:00")]


def test_schema_derives_duration_and_rejects_partial_or_impossible_fixed_intervals():
    meeting = LLMTask(
        title="Meeting", duration_min=None, fixed_start="09:00", fixed_end="10:00"
    )
    assert meeting.duration_min == 60
    assert meeting.duration_is_explicit is True

    with pytest.raises(ValidationError, match="must be supplied together"):
        LLMTask(title="Partial meeting", duration_min=60, fixed_start="09:00")
    with pytest.raises(ValidationError, match="later than fixed_start"):
        LLMTask(
            title="Impossible meeting",
            duration_min=60,
            fixed_start="10:00",
            fixed_end="09:00",
        )


def test_schema_duration_bounds():
    """Duration bounds: ge=5, le=480."""
    with pytest.raises(ValidationError):
        LLMTask(title="Too short", duration_min=4)

    with pytest.raises(ValidationError):
        LLMTask(title="Too long", duration_min=481)

    t = LLMTask(title="Valid min", duration_min=5)
    assert t.duration_min == 5

    t2 = LLMTask(title="Valid max", duration_min=480)
    assert t2.duration_min == 480


def test_schema_invalid_enums():
    """Invalid priority or importance enums must trigger ValidationError."""
    with pytest.raises(ValidationError):
        LLMTask(title="Test", duration_min=30, priority="CRITICAL")  # type: ignore

    with pytest.raises(ValidationError):
        LLMTask(title="Test", duration_min=30, importance="MUST_DO")  # type: ignore


def test_schema_allows_empty_tasks_for_availability_only():
    """Schema allows empty task list when user specifies availability only."""
    plan = LLMDayPlan.model_validate({
        "reply": "Noted your availability.",
        "windows": [("14:00", "18:00")],
        "tasks": [],
    })
    assert len(plan.tasks) == 0
    assert plan.windows == [("14:00", "18:00")]


def test_schema_disallows_and_ignores_application_owned_fields(base_context):
    """Application-owned fields (task IDs, plan dates, timelines, tokens) in LLM output are ignored."""
    adversarial_payload = {
        "reply": "Adversarial plan",
        "id": "malicious-plan-id",
        "plan_date": "2099-01-01",
        "preview_token": "fake-token",
        "timeline": [{"start": "00:00", "end": "23:59"}],
        "tasks": [
            {
                "id": "custom-uuid-override",
                "title": "Injected task",
                "duration_min": 60,
                "user_id": "00000000-0000-0000-0000-000000000000",
                "created_at": "1970-01-01T00:00:00Z",
            }
        ],
    }
    plan = LLMDayPlan.model_validate(adversarial_payload)
    # Extra fields on the plan model are ignored
    assert not hasattr(plan, "preview_token")
    assert not hasattr(plan, "timeline")

    # In parsed plan and draft assembly, application-owned fields are code-generated
    parsed = _parsed_from_llm(plan, base_context, "Injected task")
    assert len(parsed.tasks) == 1
    # ParsedTask has no malicious id
    assert parsed.tasks[0].source_task_id is None

    # Normalization into draft
    from app.ai.drafts import assemble_today
    draft, _ = assemble_today(parsed, base_context, [])
    # Task ID is deterministically assigned as 'd1', not 'custom-uuid-override'
    assert draft.tasks[0].id == "d1"
    # Plan date is application context date, not 2099-01-01
    assert draft.planDate == base_context.now.date()


# ===========================================================================
# Group 4, 9, 10: Deterministic Assembly, Authority, Scheduler & Persistence
# ===========================================================================

@pytest.mark.asyncio
async def test_today_assembly_deterministic_ids_and_boundaries(base_context):
    """Canonical draft assembly enforces d1/d2 order, preview=None, and zero DB writes."""
    mock_llm = AsyncMock(return_value={
        "reply": "Here is your plan.",
        "tasks": [
            {"title": "Task One", "duration_min": 45, "importance": "CORE", "priority": "HIGH"},
            {"title": "Task Two", "duration_min": 30, "importance": "OPTIONAL", "priority": "MEDIUM"},
            {"title": "Task Three", "duration_min": 60, "importance": "CORE", "priority": "LOW"},
        ],
        "windows": [["09:00", "17:00"]],
        "assumptions": [],
    })

    with patch.object(planner.llm_provider, "call", mock_llm):
        with patch("app.ai.handlers.planner.get_budget_mode", new=AsyncMock(return_value=BudgetMode.NORMAL)):
            with patch("app.ai.handlers.planner.available_routes", new=AsyncMock(return_value="groq:llama")):
                with patch("app.ai.handlers.planner.carried_tasks", new=AsyncMock(return_value=[])):
                    response = await planner.plan_day(
                        "Plan Task One 45m, Task Two 30m, Task Three 60m",
                        base_context,
                        "en",
                    )

    mock_llm.assert_awaited_once()
    assert response.tier == "LLM"
    # Invariant: preview must be None (scheduler is not run during draft creation)
    assert response.preview is None

    draft = response.draft
    assert draft is not None
    assert len(draft.tasks) == 3
    # Invariant: Task IDs are deterministic d1, d2, d3
    assert [t.id for t in draft.tasks] == ["d1", "d2", "d3"]
    # Invariant: trusted plan date is owned by application
    assert draft.planDate == base_context.now.date()
    assert draft.timezone == str(base_context.timezone)

    # Invariant: check_today validation runs
    issues = check_today(draft)
    assert issues == []

    # Invariant: Zero planning domain writes before explicit save
    base_context.db.add.assert_not_called()
    base_context.db.add_all.assert_not_called()
    base_context.db.flush.assert_not_awaited()


@pytest.mark.asyncio
async def test_today_01_exact_request_uses_llm_semantics_without_parser_corruption(base_context):
    """TODAY-01 stays on the LLM path and preserves its semantic extraction."""
    message = (
        "Today I need to study algorithms for 1 hour, write the report for 45 minutes, "
        "and optionally read a book for 30 minutes. I am available from 1 PM to 5 PM."
    )
    mock_llm = AsyncMock(return_value={
        "reply": "I drafted the three requested tasks.",
        "windows": [["13:00", "17:00"]],
        "tasks": [
            {"title": "Study algorithms", "duration_min": 60, "duration_is_explicit": True, "importance": "CORE"},
            {"title": "Write the report", "duration_min": 45, "duration_is_explicit": True, "importance": "CORE"},
            {"title": "Read a book", "duration_min": 30, "duration_is_explicit": True, "importance": "OPTIONAL"},
        ],
        "assumptions": [],
    })

    with patch.object(planner.llm_provider, "call", mock_llm):
        with patch("app.ai.handlers.planner.get_budget_mode", new=AsyncMock(return_value=BudgetMode.NORMAL)):
            with patch("app.ai.handlers.planner.available_routes", new=AsyncMock(return_value="groq:model")):
                with patch("app.ai.handlers.planner.carried_tasks", new=AsyncMock(return_value=[])):
                    response = await planner.plan_day(message, base_context, "en")

    mock_llm.assert_awaited_once()
    assert response.tier == "LLM"
    assert response.degraded is None
    assert response.preview is None
    assert response.draft is not None
    assert [(window.start, window.end) for window in response.draft.windows] == [("13:00", "17:00")]
    assert [
        (task.id, task.title, task.durationMin, task.importance, task.fixedStart, task.fixedEnd)
        for task in response.draft.tasks
    ] == [
        ("d1", "Study algorithms", 60, "CORE", None, None),
        ("d2", "Write the report", 45, "CORE", None, None),
        ("d3", "Read a book", 30, "OPTIONAL", None, None),
    ]
    assert response.assumptions == []
    assert check_today(response.draft) == []
    base_context.db.add.assert_not_called()
    base_context.db.add_all.assert_not_called()
    base_context.db.flush.assert_not_awaited()


@pytest.mark.asyncio
async def test_parse_02_preserves_fixed_meeting_through_today_draft(base_context):
    """A task-specific interval remains distinct from availability and a deadline."""
    base_context = replace(
        base_context,
        now=datetime(2026, 9, 25, 7, 0, tzinfo=ZoneInfo("Asia/Ho_Chi_Minh")),
    )
    message = (
        "Today I am available from 8 AM to 1 PM.\n"
        "I have a meeting from 9 AM to 10 AM.\n"
        "Finish the report for 60 minutes before noon.\n"
        "Study algorithms for 45 minutes."
    )
    mock_llm = AsyncMock(return_value={
        "reply": "I extracted your availability and three tasks.",
        "windows": [["08:00", "13:00"]],
        "tasks": [
            {
                "title": "Meeting", "duration_min": None,
                "fixed_start": "09:00", "fixed_end": "10:00",
            },
            {
                "title": "Finish the report", "duration_min": 60,
                "duration_is_explicit": True, "deadline": "12:00",
            },
            {
                "title": "Study algorithms", "duration_min": 45,
                "duration_is_explicit": True,
            },
        ],
        "assumptions": [],
    })

    with patch.object(planner.llm_provider, "call", mock_llm):
        with patch("app.ai.handlers.planner.get_budget_mode", new=AsyncMock(return_value=BudgetMode.NORMAL)):
            with patch("app.ai.handlers.planner.available_routes", new=AsyncMock(return_value="groq:model")):
                with patch("app.ai.handlers.planner.carried_tasks", new=AsyncMock(return_value=[])):
                    response = await planner.plan_day(message, base_context, "en")

    mock_llm.assert_awaited_once()
    assert response.tier == "LLM"
    assert response.degraded is None
    assert response.preview is None
    assert response.draft is not None
    assert [(window.start, window.end) for window in response.draft.windows] == [("08:00", "13:00")]
    assert len(response.draft.tasks) == 3
    meeting, report, study = response.draft.tasks
    assert (meeting.title, meeting.durationMin, meeting.schedulingType) == ("Meeting", 60, "FIXED")
    assert meeting.fixedStart.strftime("%H:%M") == "09:00"
    assert meeting.fixedEnd.strftime("%H:%M") == "10:00"
    assert report.title == "Finish the report"
    assert report.deadline.strftime("%H:%M") == "12:00"
    assert (study.title, study.durationMin) == ("Study algorithms", 45)
    assert not any("Moved to tomorrow" in item.text for item in response.assumptions)
    assert check_today(response.draft) == []


# ===========================================================================
# Group 5: Natural-Language Robustness Tests (Semantic Variations)
# ===========================================================================

@pytest.mark.asyncio
@pytest.mark.parametrize(
    "phrase,expected_title,expected_duration,expected_importance",
    [
        ("I can work between 1 PM and 5 PM. Read docs for 20 mins if there is time.", "Read docs", 20, "OPTIONAL"),
        ("Maybe read docs for 20 minutes if possible", "read docs", 20, "OPTIONAL"),
        ("Optional technical reading 20m", "technical reading", 20, "OPTIONAL"),
        ("45 minutes of writing code", "writing code", 45, "CORE"),
        ("Take an hour to debug authentication", "debug authentication", 60, "CORE"),
        ("Hey Mr. Bloom, let's get kanji practice done for 30m", "kanji practice", 30, "CORE"),
    ],
)
async def test_natural_language_robustness_variations(
    base_context, phrase, expected_title, expected_duration, expected_importance
):
    """Multiple semantically equivalent paraphrases parse into canonical TodayDraft without parser regex additions."""
    mock_llm = AsyncMock(return_value={
        "reply": "Extracted your plan.",
        "tasks": [
            {
                "title": expected_title,
                "duration_min": expected_duration,
                "importance": expected_importance,
                "priority": "MEDIUM",
            }
        ],
        "windows": [["09:00", "17:00"]],
        "assumptions": [],
    })

    with patch.object(planner.llm_provider, "call", mock_llm):
        with patch("app.ai.handlers.planner.get_budget_mode", new=AsyncMock(return_value=BudgetMode.NORMAL)):
            with patch("app.ai.handlers.planner.available_routes", new=AsyncMock(return_value="groq:llama")):
                with patch("app.ai.handlers.planner.carried_tasks", new=AsyncMock(return_value=[])):
                    response = await planner.plan_day(phrase, base_context, "en")

    mock_llm.assert_awaited_once()
    assert response.tier == "LLM"
    assert response.draft is not None
    assert len(response.draft.tasks) == 1
    task = response.draft.tasks[0]
    assert task.title == expected_title
    assert task.durationMin == expected_duration
    assert task.importance == expected_importance


# ===========================================================================
# Group 6: Invalid LLM Output and Repair
# ===========================================================================

@pytest.mark.asyncio
async def test_invalid_llm_output_triggers_repair_and_recovers(base_context):
    """Malformed output on first turn triggers a single targeted repair that recovers cleanly."""
    call_count = 0

    async def mock_call(routes, messages, *args, **kwargs):
        nonlocal call_count
        call_count += 1
        if call_count == 1:
            # First turn returns invalid duration (<5)
            return {
                "reply": "Drafting plan",
                "tasks": [{"title": "Quick task", "duration_min": 1, "importance": "CORE"}],
                "windows": [],
                "assumptions": [],
            }
        else:
            # Second turn (repair) returns fixed valid duration
            return {
                "reply": "Repaired plan",
                "tasks": [{"title": "Quick task", "duration_min": 15, "importance": "CORE"}],
                "windows": [],
                "assumptions": [],
            }

    mock_provider = AsyncMock(side_effect=mock_call)

    with patch.object(planner.llm_provider, "call", mock_provider):
        with patch("app.ai.handlers.planner.get_budget_mode", new=AsyncMock(return_value=BudgetMode.NORMAL)):
            with patch("app.ai.handlers.planner.available_routes", new=AsyncMock(return_value="groq:llama")):
                with patch("app.ai.handlers.planner.carried_tasks", new=AsyncMock(return_value=[])):
                    response = await planner.plan_day("Quick task", base_context, "en")

    assert call_count == 2
    assert response.tier == "LLM"
    assert response.draft is not None
    assert response.draft.tasks[0].durationMin == 15


@pytest.mark.asyncio
async def test_invalid_llm_output_failed_repair_falls_back_without_invalid_draft(base_context):
    """When both original extraction and repair fail, system falls back safely without exposing invalid draft."""
    mock_provider = AsyncMock(return_value={
        "reply": "Attempted plan",
        "tasks": [{"title": "Broken task", "duration_min": -50, "importance": "INVALID"}],
    })

    with patch.object(planner.llm_provider, "call", mock_provider):
        with patch("app.ai.handlers.planner.get_budget_mode", new=AsyncMock(return_value=BudgetMode.NORMAL)):
            with patch("app.ai.handlers.planner.available_routes", new=AsyncMock(return_value="groq:llama")):
                with patch("app.ai.handlers.planner.carried_tasks", new=AsyncMock(return_value=[])):
                    response = await planner.plan_day("Study 60 min", base_context, "en")

    # Repair failed -> fallback parser took over
    assert response.tier == "PARSER"
    assert response.degraded == "LLM_FAILED"
    # Fallback parser produced valid 60m task from "Study 60 min"
    assert response.draft is not None
    assert response.draft.tasks[0].durationMin == 60


# ===========================================================================
# Group 7: Provider Failure and Degraded Parser Fallback
# ===========================================================================

@pytest.mark.asyncio
@pytest.mark.parametrize(
    "error_instance",
    [
        LLMError("Provider timeout"),
        LLMError("503 Service Unavailable"),
        LLMError("429 Rate limit exceeded"),
    ],
)
async def test_provider_failures_fall_back_to_degraded_parser(base_context, error_instance):
    """Provider exceptions degrade cleanly to the deterministic parser with tier=PARSER, degraded=LLM_FAILED."""
    failing_llm = AsyncMock(side_effect=error_instance)

    with patch.object(planner.llm_provider, "call", failing_llm):
        with patch("app.ai.handlers.planner.get_budget_mode", new=AsyncMock(return_value=BudgetMode.NORMAL)):
            with patch("app.ai.handlers.planner.available_routes", new=AsyncMock(return_value="groq:llama")):
                with patch("app.ai.handlers.planner.carried_tasks", new=AsyncMock(return_value=[])):
                    response = await planner.plan_day("StudyKanji 45m and review 15m", base_context, "en")

    failing_llm.assert_awaited_once()
    assert response.tier == "PARSER"
    assert response.degraded == "LLM_FAILED"
    assert response.draft is not None
    assert len(response.draft.tasks) >= 1


@pytest.mark.asyncio
async def test_budget_rules_only_skips_llm_and_sets_rules_only(base_context):
    """RULES_ONLY budget mode skips the LLM and runs parser fallback with degraded=RULES_ONLY."""
    spy_llm = AsyncMock()

    with patch.object(planner.llm_provider, "call", spy_llm):
        with patch("app.ai.handlers.planner.get_budget_mode", new=AsyncMock(return_value=BudgetMode.RULES_ONLY)):
            with patch("app.ai.handlers.planner.available_routes", new=AsyncMock(return_value="")):
                with patch("app.ai.handlers.planner.carried_tasks", new=AsyncMock(return_value=[])):
                    response = await planner.plan_day("Study kanji 45m", base_context, "en")

    spy_llm.assert_not_called()
    assert response.tier == "PARSER"
    assert response.degraded == "RULES_ONLY"
    assert response.draft is not None


# ===========================================================================
# Group 8: Clarification Fallback (No Fake Tasks Invented)
# ===========================================================================

@pytest.mark.asyncio
async def test_clarification_fallback_when_neither_produces_draft(base_context):
    """When neither LLM nor parser can produce a valid draft, ask one clarification question without fake tasks."""
    failing_llm = AsyncMock(side_effect=LLMError("LLM offline"))

    with patch.object(planner.llm_provider, "call", failing_llm):
        with patch("app.ai.handlers.planner.get_budget_mode", new=AsyncMock(return_value=BudgetMode.NORMAL)):
            with patch("app.ai.handlers.planner.available_routes", new=AsyncMock(return_value="groq:llama")):
                with patch("app.ai.handlers.planner.carried_tasks", new=AsyncMock(return_value=[])):
                    # Ambiguous / unresolvable input that deterministic parser cannot turn into tasks
                    response = await planner.plan_day("??? ...", base_context, "en")

    assert response.tier == "PARSER"
    assert response.degraded == "LLM_FAILED"
    assert response.question is not None
    assert "Which tasks would you like to plan today?" in response.question
    # Invariant: No fake 45-minute task invented solely to avoid clarification
    assert response.draft is None
    assert response.intent == "PLAN_DAY"


@pytest.mark.asyncio
async def test_parse_04_llm_estimate_creates_transparent_non_persisted_draft(base_context):
    extraction = {
        "reply": "I estimated the missing duration for your review.",
        "tasks": [{
            "title": "Organize Zarkon materials",
            "duration_min": 45,
            "duration_is_explicit": False,
            "importance": "CORE",
            "priority": "MEDIUM",
            "category": "Work",
        }],
        "windows": [],
        "assumptions": [
            "Estimated 45 minutes for Organize Zarkon materials",
            "Kept a distinct planning assumption",
        ],
    }

    with patch.object(planner.llm_provider, "call", AsyncMock(return_value=extraction)) as llm_call:
        with patch("app.ai.handlers.planner.get_budget_mode", new=AsyncMock(return_value=BudgetMode.NORMAL)):
            with patch("app.ai.handlers.planner.available_routes", new=AsyncMock(return_value="groq:planner")):
                response = await planner.plan_day(
                    "Organize Zarkon materials.", base_context, "en"
                )

    assert response.intent == "PLAN_DAY"
    assert response.tier == "LLM"
    assert response.draft is not None
    assert len(response.draft.tasks) == 1
    task = response.draft.tasks[0]
    assert (task.title, task.durationMin, task.estimateSource) == (
        "Organize Zarkon materials", 45, "AI"
    )
    assert task.fixedStart is None
    assert task.fixedEnd is None
    assert task.deadline is None
    assumption_texts = [item.text for item in response.assumptions]
    assert assumption_texts.count(
        "Estimated 45 minutes for Organize Zarkon materials"
    ) == 1
    assert assumption_texts.index(
        "Estimated 45 minutes for Organize Zarkon materials"
    ) < assumption_texts.index("Kept a distinct planning assumption")
    assert llm_call.await_args.kwargs["purpose"] == "PLANNER"
    base_context.db.add.assert_not_called()
    base_context.db.add_all.assert_not_called()
    base_context.db.flush.assert_not_awaited()


# ===========================================================================
# Group 11: Authoritative LLM, Carried Work Bypass Safety & Edge Conditions
# ===========================================================================

@pytest.mark.asyncio
async def test_llm_semantics_authoritative_over_conflicting_parser_semantics(base_context):
    """Successful LLM extraction is authoritative and not overridden by conflicting parser semantics."""
    mock_llm = AsyncMock(return_value={
        "reply": "Extracted plan",
        "tasks": [
            {
                "title": "Task A",
                "duration_min": 75,
                "importance": "OPTIONAL",
                "priority": "LOW",
                "category": "Learning",
            }
        ],
        "windows": [("10:00", "16:00")],
        "assumptions": ["LLM assumption only"],
    })

    with patch.object(planner.llm_provider, "call", mock_llm):
        with patch("app.ai.handlers.planner.get_budget_mode", new=AsyncMock(return_value=BudgetMode.NORMAL)):
            with patch("app.ai.handlers.planner.available_routes", new=AsyncMock(return_value="groq:llama")):
                with patch("app.ai.handlers.planner.carried_tasks", new=AsyncMock(return_value=[])):
                    response = await planner.plan_day("Task A 60m", base_context, "en")

    assert response.tier == "LLM"
    assert response.draft is not None
    assert len(response.draft.tasks) == 1
    task = response.draft.tasks[0]
    # The parser's 60m must NOT overwrite the LLM's 75m
    assert task.durationMin == 75
    # The parser's CORE must NOT overwrite the LLM's OPTIONAL
    assert task.importance == "OPTIONAL"
    assert task.priority == "LOW"
    assert task.category == "Learning"
    assert all("Normalized budget" not in a.text for a in response.assumptions)


@pytest.mark.asyncio
async def test_unrecognized_new_task_not_bypassed_by_carried_work(base_context):
    """Unrecognized natural language task does not trigger pre-LLM carried task bypass."""
    from app.ai.parser import ParsedTask
    carried_work = [ParsedTask(title="Previous Unfinished Task", duration_min=45, source="AI")]

    message = "Do some deep architectural refactoring and analysis"
    mock_llm = AsyncMock(return_value={
        "reply": "Drafted your refactoring session.",
        "tasks": [
            {
                "title": "deep architectural refactoring",
                "duration_min": 90,
                "importance": "CORE",
                "priority": "HIGH",
            }
        ],
        "windows": [],
        "assumptions": [],
    })

    with patch.object(planner.llm_provider, "call", mock_llm):
        with patch("app.ai.handlers.planner.get_budget_mode", new=AsyncMock(return_value=BudgetMode.NORMAL)):
            with patch("app.ai.handlers.planner.available_routes", new=AsyncMock(return_value="groq:llama")):
                with patch("app.ai.handlers.planner.carried_tasks", new=AsyncMock(return_value=carried_work)):
                    response = await planner.plan_day(message, base_context, "en")

    mock_llm.assert_awaited_once()
    assert response.tier == "LLM"
    assert response.draft is not None
    titles = [t.title for t in response.draft.tasks]
    assert "deep architectural refactoring" in titles
    assert "Previous Unfinished Task" in titles


@pytest.mark.asyncio
async def test_window_only_llm_output_returns_no_draft_and_asks_clarification(base_context):
    """LLM returning windows but zero tasks does not create an empty TodayDraft when no carried tasks exist."""
    mock_llm = AsyncMock(return_value={
        "reply": "I see you have time in the afternoon.",
        "tasks": [],
        "windows": [("14:00", "18:00")],
        "assumptions": [],
    })

    with patch.object(planner.llm_provider, "call", mock_llm):
        with patch("app.ai.handlers.planner.get_budget_mode", new=AsyncMock(return_value=BudgetMode.NORMAL)):
            with patch("app.ai.handlers.planner.available_routes", new=AsyncMock(return_value="groq:llama")):
                with patch("app.ai.handlers.planner.carried_tasks", new=AsyncMock(return_value=[])):
                    response = await planner.plan_day("I am free from 2pm to 6pm", base_context, "en")

    assert response.tier == "LLM"
    assert response.draft is None
    assert response.question is not None
    assert "Which tasks would you like to plan today?" in response.question


@pytest.mark.asyncio
async def test_assumption_only_llm_output_returns_no_draft_and_asks_clarification(base_context):
    """LLM returning assumptions but zero tasks does not create an empty TodayDraft when no carried tasks exist."""
    mock_llm = AsyncMock(return_value={
        "reply": "Understood your budget constraint.",
        "tasks": [],
        "windows": [],
        "assumptions": ["User has a 2 hour limit today."],
    })

    with patch.object(planner.llm_provider, "call", mock_llm):
        with patch("app.ai.handlers.planner.get_budget_mode", new=AsyncMock(return_value=BudgetMode.NORMAL)):
            with patch("app.ai.handlers.planner.available_routes", new=AsyncMock(return_value="groq:llama")):
                with patch("app.ai.handlers.planner.carried_tasks", new=AsyncMock(return_value=[])):
                    response = await planner.plan_day("I only have 2 hours", base_context, "en")

    assert response.tier == "LLM"
    assert response.draft is None
    assert response.question is not None
    assert len(response.assumptions) == 1
    assert "User has a 2 hour limit today." in response.assumptions[0].text


@pytest.mark.asyncio
async def test_empty_llm_output_returns_no_draft_and_asks_clarification(base_context):
    """LLM returning empty dictionary `{}` does not create an empty TodayDraft."""
    mock_llm = AsyncMock(return_value={})

    with patch.object(planner.llm_provider, "call", mock_llm):
        with patch("app.ai.handlers.planner.get_budget_mode", new=AsyncMock(return_value=BudgetMode.NORMAL)):
            with patch("app.ai.handlers.planner.available_routes", new=AsyncMock(return_value="groq:llama")):
                with patch("app.ai.handlers.planner.carried_tasks", new=AsyncMock(return_value=[])):
                    response = await planner.plan_day("Hello Mr Bloom", base_context, "en")

    assert response.tier == "LLM"
    assert response.draft is None
    assert response.question is not None


@pytest.mark.asyncio
async def test_invalid_fixed_interval_not_silently_converted_to_flexible(base_context):
    """An impossible fixed interval (e.g. 15:30 to 14:00) is preserved as FIXED and triggers clarification."""
    mock_llm = AsyncMock(return_value={
        "reply": "Extracted task with fixed window.",
        "tasks": [
            {
                "title": "Practice SQL",
                "duration_min": 90,
                "importance": "CORE",
                "priority": "MEDIUM",
                "fixed_start": "15:30",
                "fixed_end": "14:00",
            }
        ],
        "windows": [],
        "assumptions": [],
    })

    with patch.object(planner.llm_provider, "call", mock_llm):
        with patch("app.ai.handlers.planner.get_budget_mode", new=AsyncMock(return_value=BudgetMode.NORMAL)):
            with patch("app.ai.handlers.planner.available_routes", new=AsyncMock(return_value="groq:llama")):
                with patch("app.ai.handlers.planner.carried_tasks", new=AsyncMock(return_value=[])):
                    response = await planner.plan_day("Practice SQL from 15:30 to 14:00 for 90m", base_context, "en")

    mock_llm.assert_awaited_once()  # A semantically impossible interval is not auto-reinterpreted.
    assert response.tier == "PARSER"
    assert response.degraded == "LLM_FAILED"
    assert response.draft is not None
    task = response.draft.tasks[0]
    assert task.schedulingType == "FIXED"
    assert task.fixedStart is not None
    assert task.fixedEnd is not None
    assert task.fixedEnd <= task.fixedStart
    assert response.question is not None
    assert response.preview is None


@pytest.mark.asyncio
async def test_pure_plan_command_with_carried_tasks_uses_rules_tier(base_context):
    """Pure plan command with existing carried work drafts immediately using RULES tier without calling LLM."""
    from app.ai.parser import ParsedTask
    carried_work = [ParsedTask(title="Scheduled Yesterday", duration_min=45, source="AI")]

    spy_llm = AsyncMock()

    with patch.object(planner.llm_provider, "call", spy_llm):
        with patch("app.ai.handlers.planner.carried_tasks", new=AsyncMock(return_value=carried_work)):
            response = await planner.plan_day("Lập lịch hôm nay", base_context, "vi")

    spy_llm.assert_not_called()
    assert response.tier == "RULES"
    assert response.draft is not None
    assert len(response.draft.tasks) == 1
    assert response.draft.tasks[0].title == "Scheduled Yesterday"
