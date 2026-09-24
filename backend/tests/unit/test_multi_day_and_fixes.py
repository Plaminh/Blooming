"""Regression tests for owner-reported chatbot issues.

Covers mis-routed Vietnamese, clock-vs-duration parsing, destructive editor
matches, multi-day plans, recurring tasks and the replan snapshot crash.
All inputs are real sentences that previously produced wrong results.
"""

from datetime import date, datetime, timezone
from unittest.mock import AsyncMock
from uuid import uuid4
from zoneinfo import ZoneInfo

import pytest

from app.ai.context import ChatContext
from app.ai.drafts import assemble_today, primary_plan_date
from app.ai.editor_rules import parse_edit
from app.ai.parser import DayRef, ParsedTask, parse
from app.ai.router import route
from app.schemas.drafts import RecurrenceDraft, TaskDraft, TodayDraft
from app.services.today_service import _snapshot_task_ids

# Thursday 24 September 2026, 08:00 UTC.
NOW = datetime(2026, 9, 24, 8, 0, tzinfo=timezone.utc)
TODAY = NOW.date()


def _ctx(now: datetime = NOW) -> ChatContext:
    return ChatContext(
        db=AsyncMock(),
        user_id=uuid4(),
        now=now,
        timezone=ZoneInfo("UTC"),
        break_minutes=5,
        default_windows=(("09:00", "22:00"),),
        default_date_offset=0,
    )


def _only(message: str) -> ParsedTask:
    tasks = parse(message).tasks
    assert len(tasks) == 1, tasks
    return tasks[0]


# --- Router ---------------------------------------------------------------


@pytest.mark.parametrize(
    "message,intent",
    [
        # "chắn" in "chắc chắn" is not "chán" (bored).
        ("Chắc chắn mai mình học 2 tiếng", "PLAN_DAY"),
        # Drinking water with a friend is not a garden balance question.
        ("Tôi có hẹn uống nước với bạn lúc 5h", "PLAN_DAY"),
        # "tuần này" inside a planning request is not a statistics question.
        ("Lên kế hoạch cả tuần này cho mình", "PLAN_DAY"),
        ("Tuần này học bao nhiêu giờ", "STATUS_STATS"),
        ("Nước còn bao nhiêu?", "STATUS_GARDEN"),
        ("Mỗi ngày học tiếng Anh 30 phút", "PLAN_DAY"),
        # "chạy bộ" (jogging) contains "bộ", not "bỏ" (stop).
        ("Chạy bộ mỗi ngày 30p", "PLAN_DAY"),
        ("Dừng lặp lại học tiếng Anh", "STOP_RECURRING"),
        ("Stop repeating gym", "STOP_RECURRING"),
        ("Việc lặp lại của tôi là gì?", "STATUS_RECURRING"),
        ("Tôi mệt quá", "MOOD"),
    ],
)
def test_vietnamese_routing_regressions(message, intent):
    assert route(message).intent == intent


def test_unaccented_input_still_detects_mood():
    assert route("toi met qua").intent == "MOOD"
    assert route("chac chan mai hoc 2 tieng").intent != "MOOD"


# --- Parser: clock times and durations --------------------------------------


@pytest.mark.parametrize(
    "message,fixed_start",
    [
        ("Họp 9h30", "09:30"),
        ("Họp 9h", "09:00"),
        ("Họp 2h chiều 45p", "14:00"),
        ("Học guitar lúc 7h tối 1h", "19:00"),
        ("Gọi mẹ 9 giờ rưỡi", "09:30"),
    ],
)
def test_bare_clock_times_are_start_times_not_durations(message, fixed_start):
    task = _only(message)
    assert task.fixed_start == fixed_start
    assert task.duration_min is None or task.duration_min <= 60


@pytest.mark.parametrize(
    "message,minutes,title",
    [
        ("Học 2 tiếng rưỡi", 150, "Học"),
        ("Học 1h30", 90, "Học"),
        ("Học trong 8h", 480, "Học"),
        ("Code 2h", 120, "Code"),
    ],
)
def test_durations_still_parse(message, minutes, title):
    task = _only(message)
    assert (task.duration_min, task.title, task.fixed_start) == (minutes, title, None)


def test_titles_keep_words_that_look_like_fillers():
    assert _only("Tuần này ôn thi 10 tiếng").title == "ôn thi"
    assert _only("Mai mình học 2 tiếng").title == "học"
    assert [task.title for task in parse("Theo thứ tự: học 1h, đọc sách 30p").tasks] == [
        "học",
        "đọc sách",
    ]


# --- Parser: days ------------------------------------------------------------


@pytest.mark.parametrize(
    "message,expected",
    [
        ("Ngày kia học 2h", date(2026, 9, 26)),
        ("Mai mình học 2 tiếng", date(2026, 9, 25)),
        ("Chắc chắn mai mình học 2 tiếng", date(2026, 9, 25)),
        ("Thứ 6 tuần sau đi gym 1h", date(2026, 10, 2)),
        ("Ngày 25/10 nộp báo cáo 2h", date(2026, 10, 25)),
        ("Tomorrow, study algorithms for 60 min", date(2026, 9, 25)),
    ],
)
def test_named_days_resolve_against_local_today(message, expected):
    task = _only(message)
    assert task.day is not None
    assert task.day.resolve(TODAY) == expected


def test_each_segment_keeps_its_own_day():
    tasks = parse("Thứ 2 học toán 1h, thứ 4 họp 30p").tasks
    assert [(t.title, t.day.resolve(TODAY)) for t in tasks] == [
        ("học toán", date(2026, 9, 28)),
        ("họp", date(2026, 9, 30)),
    ]


def test_one_named_day_applies_to_the_whole_message():
    tasks = parse("Học 1h và làm bài 30p ngày mai").tasks
    assert {t.day.resolve(TODAY) for t in tasks} == {date(2026, 9, 25)}


def test_thu_tu_as_in_order_is_not_wednesday():
    assert all(task.day is None for task in parse("Theo thứ tự: học 1h, đọc sách 30p").tasks)


# --- Parser: repetition and weekly budgets ---------------------------------------


def test_daily_recurrence_is_detected_and_removed_from_title():
    task = _only("Mỗi ngày học tiếng Anh 30 phút")
    assert (task.title, task.duration_min) == ("học tiếng Anh", 30)
    assert task.recurrence is not None and task.recurrence.freq == "DAILY"


def test_weekly_recurrence_on_listed_weekdays():
    task = _only("Mỗi thứ 2 và thứ 4 học guitar 1h lúc 7h tối")
    assert task.recurrence.freq == "WEEKLY"
    assert task.recurrence.weekdays == (0, 2)
    assert task.fixed_start == "19:00"
    english = _only("Every Monday and Wednesday gym 1h")
    assert english.recurrence.weekdays == (0, 2)


def test_weekdays_and_this_week_limits():
    assert _only("Các ngày trong tuần đọc sách 20p").recurrence.weekdays == (0, 1, 2, 3, 4)
    limited = _only("Mỗi ngày trong tuần này tập thể dục 30p")
    assert limited.recurrence.freq == "DAILY" and limited.recurrence.until_end_of_week


def test_weekly_budget_is_marked_for_spreading():
    assert _only("Tuần này ôn thi 10 tiếng").spread == "THIS_WEEK"
    assert _only("Tuần sau ôn thi 6 tiếng").spread == "NEXT_WEEK"


# --- Draft assembly across days -------------------------------------------------


def test_later_days_become_deferred_tasks_of_the_earliest_day():
    draft, assumptions = assemble_today(parse("Thứ 2 học toán 1h, thứ 4 họp 30p"), _ctx())
    assert draft.planDate == date(2026, 9, 28)
    assert [t.title for t in draft.tasks] == ["học toán"]
    assert [(d.task.title, d.targetDate) for d in draft.deferred_tasks] == [
        ("họp", date(2026, 9, 30))
    ]
    ids = [t.id for t in draft.tasks] + [d.task.id for d in draft.deferred_tasks]
    assert len(ids) == len(set(ids))
    assert any(a.kind == "DATE" and "2026-09-30" in a.text for a in assumptions)


def test_undated_tasks_stay_today_when_another_day_is_named():
    draft, _ = assemble_today(parse("Học 1h, thứ 6 đi gym 1h"), _ctx())
    assert draft.planDate == TODAY
    assert [t.title for t in draft.tasks] == ["Học"]
    assert [d.targetDate for d in draft.deferred_tasks] == [date(2026, 9, 25)]


def test_future_day_windows_start_in_the_morning_not_now():
    late = datetime(2026, 9, 24, 15, 0, tzinfo=timezone.utc)
    ctx = _ctx(late)
    ctx = ChatContext(**{**ctx.__dict__, "default_windows": (("15:00", "22:00"),)})
    draft, _ = assemble_today(parse("Ngày mai học 2h"), ctx)
    assert draft.planDate == date(2026, 9, 25)
    assert draft.windows[0].start == "08:00"


def test_weekly_budget_is_spread_evenly_over_the_rest_of_the_week():
    draft, _ = assemble_today(parse("Tuần này ôn thi 10 tiếng"), _ctx())
    sessions = draft.tasks + [d.task for d in draft.deferred_tasks]
    days = [draft.planDate] + [d.targetDate for d in draft.deferred_tasks]
    assert sum(t.durationMin for t in sessions) == 600
    assert days == [date(2026, 9, 24 + i) for i in range(4)]  # Thursday..Sunday
    assert all(t.durationMin % 5 == 0 for t in sessions)
    assert sessions[0].title == "ôn thi (1/4)"


def test_recurrence_travels_to_the_draft_with_its_first_occurrence():
    draft, _ = assemble_today(parse("Mỗi thứ 2 học guitar 1h"), _ctx())
    assert draft.planDate == date(2026, 9, 28)
    recurrence = draft.tasks[0].recurrence
    assert recurrence == RecurrenceDraft(freq="WEEKLY", weekdays=[0])
    limited, _ = assemble_today(parse("Mỗi ngày trong tuần này tập thể dục 30p"), _ctx())
    assert limited.tasks[0].recurrence.until == date(2026, 9, 27)


def test_carried_work_joins_the_day_without_duplicating_named_tasks():
    carried = [
        ParsedTask(title="Viết báo cáo", duration_min=60, source="USER", source_task_id=str(uuid4())),
        ParsedTask(title="Học", duration_min=30, source="USER", recurring_task_id=str(uuid4())),
    ]
    draft, assumptions = assemble_today(parse("Học 1h"), _ctx(), carried)
    assert [(t.title, t.durationMin) for t in draft.tasks] == [("Học", 60), ("Viết báo cáo", 60)]
    assert draft.tasks[1].sourceTaskId == carried[0].source_task_id
    assert any(a.kind == "CARRIED" for a in assumptions)


def test_primary_date_matches_the_assembled_draft():
    for message in ("Thứ 2 học toán 1h, thứ 4 họp 30p", "Học 1h", "Ngày kia học 2h"):
        plan = parse(message)
        assert primary_plan_date(plan, _ctx()) == assemble_today(plan, _ctx())[0].planDate


def test_recurrence_label_and_occurrence():
    rule = RecurrenceDraft(freq="WEEKLY", weekdays=[4, 0, 4])
    assert rule.weekdays == [0, 4]
    assert rule.label("vi") == "Hàng tuần T2, T6"
    assert rule.occurs_on(date(2026, 9, 28), start=TODAY)
    assert not rule.occurs_on(date(2026, 9, 29), start=TODAY)
    assert not rule.occurs_on(date(2026, 9, 21), start=TODAY)


def test_day_ref_date_rolls_to_next_year_when_passed():
    assert DayRef("date", 5, month=1).resolve(TODAY) == date(2027, 1, 5)
    assert DayRef("date", 31, month=2).resolve(TODAY) == TODAY  # invalid date


# --- Editor ------------------------------------------------------------------


def _draft() -> TodayDraft:
    return TodayDraft(
        planDate=date(2030, 1, 1),
        timezone="UTC",
        tasks=[
            TaskDraft(id="d1", title="Đọc email", durationMin=15),
            TaskDraft(id="d2", title="Học toán", durationMin=60),
        ],
    )


def test_receiving_emails_does_not_rescale_the_draft():
    ops = parse_edit("nhận thêm 2 email mới", _draft())
    assert not ops or all(op.op != "scale_durations" for op in ops)


@pytest.mark.parametrize("message", ["nhân 2", "nhân lên 1.5", "scale by 1.5", "nhan 2"])
def test_explicit_scale_commands_still_work(message):
    ops = parse_edit(message, _draft())
    assert ops and ops[0].op == "scale_durations"


# --- Replan snapshot ---------------------------------------------------------


def test_replan_reads_both_snapshot_shapes():
    first, second = uuid4(), uuid4()
    replan_snapshot = {"unscheduled_tasks": [str(first)]}
    save_snapshot = {
        "unscheduled_tasks": [{"draft_task_id": "d2", "task_id": None}],
        "task_draft_map": {str(second): "d2"},
    }
    assert _snapshot_task_ids(replan_snapshot) == {first}
    assert _snapshot_task_ids(save_snapshot) == {second}
    assert _snapshot_task_ids({"unscheduled_tasks": ["not-a-uuid", 5]}) == set()


# --- Chat rules for repeating and waiting work --------------------------------


def _template(title: str, frequency: str = "DAILY", mask: int = 0):
    from app.db.models.tasks import RecurringTask

    return RecurringTask(
        id=uuid4(), title=title, estimated_duration_minutes=30, frequency=frequency,
        weekday_mask=mask, start_date=TODAY, until_date=None, is_active=True,
    )


@pytest.mark.asyncio
async def test_listing_and_stopping_recurring_tasks(monkeypatch):
    from app.ai.handlers import rules
    from app.services import recurring_service

    templates = [_template("Học tiếng Anh"), _template("Gym", "WEEKLY", 0b101)]
    stopped = []
    monkeypatch.setattr(recurring_service, "list_active", AsyncMock(return_value=templates))

    async def set_active(_db, _user, template_id, is_active):
        stopped.append((template_id, is_active))

    monkeypatch.setattr(recurring_service, "set_active", set_active)
    common = dict(db=AsyncMock(), user_id=uuid4(), now=NOW, lang="vi")

    listed = await rules.handle(route("Việc lặp lại của tôi là gì?"), "Việc lặp lại của tôi là gì?", **common)
    assert "Học tiếng Anh (Mỗi ngày" in listed.reply and "Gym (Hàng tuần T2, T4" in listed.reply

    done = await rules.handle(route("Dừng lặp lại gym"), "Dừng lặp lại gym", **common)
    assert stopped == [(templates[1].id, False)]
    assert "Gym" in done.reply and done.question is None

    unclear = await rules.handle(route("Dừng việc lặp lại"), "Dừng việc lặp lại", **common)
    assert unclear.question and len(unclear.suggestions) == 2
    assert len(stopped) == 1  # nothing stopped without a named task


@pytest.mark.asyncio
async def test_status_today_mentions_waiting_work(monkeypatch):
    from app.ai.handlers import rules

    monkeypatch.setattr(
        rules.today_service,
        "get_today",
        AsyncMock(return_value={"status": "NO_PLAN", "pending_tasks": [{"title": "Viết báo cáo"}]}),
    )
    response = await rules.handle(
        route("Hôm nay có gì?"), "Hôm nay có gì?", db=AsyncMock(), user_id=uuid4(), now=NOW, lang="vi"
    )
    assert "1 việc đang chờ: Viết báo cáo" in response.reply


@pytest.mark.asyncio
async def test_plan_request_without_tasks_drafts_the_waiting_work(monkeypatch):
    from app.ai.handlers import planner

    carried = [ParsedTask(title="Viết báo cáo", duration_min=60, source="USER", source_task_id=str(uuid4()))]
    monkeypatch.setattr(planner, "carried_tasks", AsyncMock(return_value=carried))
    provider = AsyncMock()
    monkeypatch.setattr(planner.llm_provider, "call", provider)

    response = await planner.plan_day("Lập lịch hôm nay", _ctx(), "vi")

    provider.assert_not_awaited()
    assert [task.title for task in response.draft.tasks] == ["Viết báo cáo"]
    assert response.draft.tasks[0].sourceTaskId == carried[0].source_task_id
    assert "Mình đã xếp 1 việc" in response.reply


@pytest.mark.asyncio
async def test_multi_day_reply_explains_where_tasks_went():
    from app.ai.handlers import planner

    response = await planner.plan_day("Thứ 2 học toán 1h, thứ 4 họp 30p", _ctx(), "vi")
    assert response.tier == "PARSER"
    assert "1 việc khác được lưu cho ngày 30/09" in response.reply


def test_a_task_saved_for_a_later_day_can_be_removed_from_the_draft():
    from pydantic import TypeAdapter

    from app.ai.patches import apply_patch
    from app.schemas.patches import PatchOp

    draft, _ = assemble_today(parse("Thứ 2 học toán 1h, thứ 4 họp 30p"), _ctx())
    deferred_id = draft.deferred_tasks[0].task.id
    op = TypeAdapter(PatchOp).validate_python({"op": "remove_deferred_task", "task_id": deferred_id})
    changed = apply_patch(draft, [op])
    assert changed.deferred_tasks == [] and len(changed.tasks) == 1
    assert len(draft.deferred_tasks) == 1  # the source draft is not mutated
    with pytest.raises(ValueError):
        apply_patch(changed, [op])
