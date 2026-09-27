"""Mr. Bloom upgrade: LLM-first planning keeps days and repetition, day review,
completing tasks from chat, draft repetition edits and carry-over."""

from datetime import date, datetime, timezone
from unittest.mock import AsyncMock, patch
from uuid import uuid4
from zoneinfo import ZoneInfo

import pytest

from app.ai.budget import BudgetMode
from app.ai.context import ChatContext
from app.ai.handlers import planner
from app.ai.handlers.planner import LLMDayPlan, LLMTask, _parsed_from_llm
from app.ai.parser import DayRef

# Thursday 24 September 2026, 08:00 UTC.
NOW = datetime(2026, 9, 24, 8, 0, tzinfo=timezone.utc)
TODAY = NOW.date()


def _ctx() -> ChatContext:
    return ChatContext(
        db=AsyncMock(),
        user_id=uuid4(),
        now=NOW,
        timezone=ZoneInfo("UTC"),
        break_minutes=5,
        default_windows=(("09:00", "22:00"),),
        default_date_offset=0,
    )


async def _plan_with_llm(message: str, llm_output: dict):
    with (
        patch.object(planner, "get_budget_mode", AsyncMock(return_value=BudgetMode.NORMAL)),
        patch.object(planner, "available_routes", AsyncMock(return_value="groq:small")),
        patch.object(planner.llm_provider, "call", AsyncMock(return_value=llm_output)),
    ):
        return await planner.plan_day(message, _ctx(), "vi")


# --- LLM-first planning keeps days, repetition and weekly spreading ----------


@pytest.mark.asyncio
async def test_llm_path_keeps_each_tasks_day_from_the_users_words():
    response = await _plan_with_llm(
        "Thứ 2 học toán 1h, thứ 4 họp nhóm 30p",
        {"tasks": [
            {"title": "Học toán", "duration_min": 60, "duration_is_explicit": True},
            {"title": "Họp nhóm", "duration_min": 30, "duration_is_explicit": True},
        ]},
    )
    assert response.tier == "LLM"
    assert response.draft.planDate == date(2026, 9, 28)
    assert [t.title for t in response.draft.tasks] == ["Học toán"]
    assert [(d.task.title, d.targetDate) for d in response.draft.deferred_tasks] == [
        ("Họp nhóm", date(2026, 9, 30))
    ]


@pytest.mark.asyncio
async def test_llm_path_keeps_repetition_the_parser_found():
    response = await _plan_with_llm(
        "Mỗi ngày học tiếng Anh 30 phút",
        {"tasks": [{"title": "Học tiếng Anh", "duration_min": 30, "duration_is_explicit": True}]},
    )
    task = response.draft.tasks[0]
    assert task.recurrence is not None and task.recurrence.freq == "DAILY"


@pytest.mark.asyncio
async def test_llm_fields_fill_in_what_the_parser_could_not_read():
    response = await _plan_with_llm(
        "Every other weekday morning I'd like to stretch, starting next Monday",
        {"tasks": [{
            "title": "Stretch", "duration_min": 15, "duration_is_explicit": False,
            "day": "next_monday", "repeat": "WEEKDAYS",
        }]},
    )
    task = response.draft.tasks[0]
    assert response.draft.planDate == date(2026, 9, 28)
    assert task.recurrence.freq == "WEEKLY" and task.recurrence.weekdays == [0, 1, 2, 3, 4]


@pytest.mark.asyncio
async def test_llm_weekly_budget_is_spread_over_the_week():
    response = await _plan_with_llm(
        "Tuần này ôn thi 10 tiếng",
        {"tasks": [{"title": "Ôn thi", "duration_min": 600, "spread_over": "THIS_WEEK"}]},
    )
    sessions = response.draft.tasks + [d.task for d in response.draft.deferred_tasks]
    assert sum(t.durationMin for t in sessions) == 600
    assert len(sessions) == 4  # Thursday..Sunday


def test_long_duration_is_only_valid_as_a_weekly_spread():
    with pytest.raises(ValueError):
        LLMTask(title="Too long", duration_min=600)
    assert LLMTask(title="Week", duration_min=600, spread_over="NEXT_WEEK").duration_min == 600


def test_unrecognised_model_days_are_ignored():
    value = LLMDayPlan.model_validate({"tasks": [
        {"title": "A", "duration_min": 30, "day": "someday"},
        {"title": "B", "duration_min": 30, "day": "2026-10-05"},
        {"title": "C", "duration_min": 30, "day": "Friday"},
    ]})
    plan = _parsed_from_llm(value, _ctx(), "A, B, C")
    assert plan.tasks[0].day is None
    assert plan.tasks[1].day == DayRef("date", 5, month=10, year=2026)
    assert plan.tasks[2].day == DayRef("weekday", 4)


def test_ambiguous_title_matches_do_not_borrow_parser_days():
    value = LLMDayPlan.model_validate({"tasks": [{"title": "Học", "duration_min": 30}]})
    plan = _parsed_from_llm(value, _ctx(), "Thứ 2 học toán 1h, thứ 4 học lý 1h")
    assert plan.tasks[0].day is None


# --- Routing of the new intents ---------------------------------------------------

from app.ai.router import route  # noqa: E402


@pytest.mark.parametrize(
    "message,intent,has_draft",
    [
        ("Tổng kết hôm nay giúp mình", "DAY_REVIEW", False),
        ("Hôm nay mình làm được gì rồi?", "DAY_REVIEW", False),
        ("How did I do today?", "DAY_REVIEW", False),
        ("Review lecture notes today", "PLAN_DAY", False),
        ("Mình đã xong bài tập toán", "COMPLETE_TASK", False),
        ("Xong rồi", "COMPLETE_TASK", False),
        ("I finished the report", "COMPLETE_TASK", False),
        ("Báo cáo phải xong trước 5h", "PLAN_DAY", False),
        ("Cho việc 1 lặp lại mỗi ngày", "EDIT_DRAFT", True),
        ("Bỏ lặp lại việc 2", "EDIT_DRAFT", True),
        ("Dừng lặp lại học tiếng Anh", "STOP_RECURRING", False),
        ("Mỗi ngày học tiếng Anh 30 phút", "PLAN_DAY", True),
    ],
)
def test_new_intents_route_without_stealing_old_ones(message, intent, has_draft):
    assert route(message, has_draft=has_draft).intent == intent


# --- Day review and completing tasks from chat ------------------------------------

from app.ai.handlers import execution  # noqa: E402


def _today(*blocks):
    return {
        "status": "ACTIVE",
        "blocks": [
            {
                "block_type": "TASK", "task_id": task_id, "title": title, "status": status,
                "planned_start_at": datetime(2026, 9, 24, hour, 0, tzinfo=timezone.utc),
            }
            for task_id, title, status, hour in blocks
        ],
    }


PLAN = _today(
    ("t1", "Bài tập toán", "COMPLETED", 9),
    ("t2", "Đọc tài liệu vật lý", "PLANNED", 10),
    ("t3", "Viết báo cáo", "PLANNED", 14),
    ("t3", "Viết báo cáo", "PLANNED", 15),  # split task: one entry
)


class _Stats:
    study_time_hours = 1
    study_time_minutes = 20


@pytest.mark.asyncio
async def test_day_review_counts_work_and_offers_to_move_the_rest(monkeypatch):
    monkeypatch.setattr(execution.today_service, "get_today", AsyncMock(return_value=PLAN))
    monkeypatch.setattr(
        execution.statistics_service, "get_statistics_summary", AsyncMock(return_value=_Stats())
    )
    response = await execution.day_review(AsyncMock(), uuid4(), NOW, "vi")
    assert "xong 1/3 việc" in response.reply and "1 giờ 20 phút" in response.reply
    assert "Đọc tài liệu vật lý, Viết báo cáo" in response.reply
    assert [s.action for s in response.suggestions] == ["CARRY_OVER_UNFINISHED", "REPLAN_TODAY"]


@pytest.mark.asyncio
async def test_day_review_without_a_plan_offers_planning(monkeypatch):
    monkeypatch.setattr(
        execution.today_service, "get_today", AsyncMock(return_value={"status": "NO_PLAN"})
    )
    response = await execution.day_review(AsyncMock(), uuid4(), NOW, "en")
    assert "no plan" in response.reply
    assert response.suggestions[0].send_text == "Plan my day"


@pytest.mark.asyncio
async def test_completing_a_named_task_marks_it_done(monkeypatch):
    monkeypatch.setattr(execution.today_service, "get_today", AsyncMock(return_value=PLAN))
    update = AsyncMock()
    monkeypatch.setattr(execution.today_service, "update_task_status_from_today", update)
    response = await execution.complete_task(AsyncMock(), uuid4(), NOW, "Mình đã xong báo cáo rồi", "vi")
    assert update.await_args.args[2] == "t3"
    assert update.await_args.args[3].status == "COMPLETED"
    assert update.await_args.kwargs["commit"] is False
    assert "Viết báo cáo" in response.reply and "Tiếp theo: Đọc tài liệu vật lý lúc 10:00" in response.reply


@pytest.mark.asyncio
async def test_unclear_completion_asks_instead_of_guessing(monkeypatch):
    monkeypatch.setattr(execution.today_service, "get_today", AsyncMock(return_value=PLAN))
    update = AsyncMock()
    monkeypatch.setattr(execution.today_service, "update_task_status_from_today", update)
    response = await execution.complete_task(AsyncMock(), uuid4(), NOW, "Xong rồi", "vi")
    update.assert_not_awaited()
    assert response.question
    assert [s.send_text for s in response.suggestions] == [
        "Đã xong Đọc tài liệu vật lý", "Đã xong Viết báo cáo"
    ]


@pytest.mark.asyncio
async def test_completion_with_nothing_open(monkeypatch):
    monkeypatch.setattr(
        execution.today_service, "get_today", AsyncMock(return_value={"status": "NO_PLAN"})
    )
    response = await execution.complete_task(AsyncMock(), uuid4(), NOW, "I finished it", "en")
    assert "can't find" in response.reply


# --- Repetition edits on a draft ---------------------------------------------------

from app.ai.editor_rules import parse_edit  # noqa: E402
from app.ai.patches import apply_patch  # noqa: E402
from app.schemas.drafts import TaskDraft, TodayDraft  # noqa: E402


def _draft():
    return TodayDraft(
        planDate=date(2026, 9, 24), timezone="UTC",
        windows=[{"start": "09:00", "end": "17:00"}],
        tasks=[
            TaskDraft(id="d1", title="Học tiếng Anh", durationMin=30),
            TaskDraft(id="d2", title="Chạy bộ", durationMin=30),
        ],
    )


@pytest.mark.parametrize(
    "message,task_id,freq,weekdays",
    [
        ("Cho việc 1 lặp lại mỗi ngày", "d1", "DAILY", []),
        ("Việc 2 lặp lại thứ 2 và thứ 4", "d2", "WEEKLY", [0, 2]),
        ("make task 2 repeat every Monday and Friday", "d2", "WEEKLY", [0, 4]),
        ("Học tiếng Anh lặp lại các ngày trong tuần", "d1", "WEEKLY", [0, 1, 2, 3, 4]),
    ],
)
def test_draft_repetition_edits(message, task_id, freq, weekdays):
    ops = parse_edit(message, _draft())
    assert ops[0].op == "set_recurrence" and ops[0].task_id == task_id
    changed = apply_patch(_draft(), ops)
    rule = next(t for t in changed.tasks if t.id == task_id).recurrence
    assert (rule.freq, rule.weekdays) == (freq, weekdays)


def test_stopping_repetition_keeps_the_task():
    repeating = apply_patch(_draft(), parse_edit("Cho việc 1 lặp lại mỗi ngày", _draft()))
    ops = parse_edit("Bỏ lặp lại việc 1", repeating)
    assert ops[0].op == "set_recurrence" and ops[0].recurrence is None
    changed = apply_patch(repeating, ops)
    assert [t.title for t in changed.tasks] == ["Học tiếng Anh", "Chạy bộ"]
    assert changed.tasks[0].recurrence is None


def test_repetition_without_a_frequency_asks():
    with pytest.raises(ValueError, match="mỗi ngày hay"):
        parse_edit("Cho việc 1 lặp lại nhé", _draft())


# --- Discoverability --------------------------------------------------------------

from app.ai.handlers import rules  # noqa: E402


@pytest.mark.asyncio
async def test_evening_greeting_offers_a_day_review():
    evening = datetime(2026, 9, 24, 19, 0, tzinfo=timezone.utc)
    response = await rules.handle(route("Chào"), "Chào", db=None, user_id=None, now=evening, lang="vi")
    assert response.suggestions[0].send_text == "Tổng kết hôm nay"
    morning = await rules.handle(route("Chào"), "Chào", db=None, user_id=None, now=NOW, lang="vi")
    assert all(s.send_text != "Tổng kết hôm nay" for s in morning.suggestions)


@pytest.mark.asyncio
async def test_help_mentions_the_new_abilities():
    response = await rules.handle(
        route("What can you do?"), "What can you do?", db=None, user_id=None, now=NOW, lang="en"
    )
    assert "repeating tasks" in response.reply and "review your day" in response.reply
