import pytest
from app.ai.estimates import estimate
from app.ai.nlu.parser import parse


@pytest.mark.parametrize(
    "text,minutes",
    [
        ("Study 30p", 30),
        ("Study 30 phut", 30),
        ("Học 30 phút", 30),
        ("Học 1h", 60),
        ("Học 1h30", 90),
        ("Học 1.5h", 90),
        ("Học 1,5 giờ", 90),
        ("Học 2 tiếng", 120),
        ("Học nửa tiếng", 30),
        ("Học một tiếng rưỡi", 90),
        ("Study half an hour", 30),
        ("Study 1 hour", 60),
        ("Study 2 hours", 120),
        ("Study 45 minutes", 45),
        ("Study 45m", 45),
        ("Study 90min", 90),
        ("Study 90 mins", 90),
        ("Study 30 minute", 30),
        ("Study 30 min", 30),
        ("study 30p", 30),
        ("30p học", 30),
        ("60p báo cáo", 60),
        ("write report 1h", 60),
        ("meeting 45m", 45),
        ("email 15min", 15),
        ("code 2h", 120),
        ("read 0.5h", 30),
        ("1h30 code", 90),
        ("2h15 code", 135),
        ("15p mail", 15),
        ("Study", 60),
        ("report", 90),
        ("meeting", 45),
        ("email", 15),
        ("gym", 40),
        ("cook", 45),
        ("clean", 30),
        ("đọc sách", 45),
        ("họp", 45),
        ("unknown task", 45),
    ],
)
def test_duration_or_estimate_cases(text, minutes):
    result = parse(text, lenient=True)
    assert len(result.tasks) == 1
    assert result.tasks[0].duration_min == minutes


def test_multi_task_windows_priority_and_date():
    result = parse(
        "Lập lịch ngày mai rảnh từ 9h đến 12h, học 60p và họp 30p nếu còn thời gian"
    )
    assert result.plan_date_offset == 1
    assert result.windows == (("09:00", "12:00"),)
    assert [task.duration_min for task in result.tasks] == [60, 30]
    assert result.tasks[1].importance == "OPTIONAL"
    assert result.tasks[1].priority == "LOW"
    assert result.confidence >= 0.8


def test_fixed_time_and_deadline():
    result = parse("Plan my day: meeting at 14h 45min, report 60min before 17h")
    assert result.tasks[0].fixed_start == "14:00"
    assert result.tasks[0].duration_min == 45
    assert result.tasks[1].deadline == "17:00"


def test_unresolved_task_is_explicit_and_lenient_has_assumption():
    strict = parse("organize the attic")
    assert strict.unresolved == (0,)
    assert strict.tasks[0].duration_min is None
    lenient = parse("organize the attic", lenient=True)
    assert lenient.tasks[0].duration_min == 45
    assert lenient.assumptions


def test_longest_keyword_estimate_wins():
    assert estimate("làm bài tập") == (90, "Learning")
    assert estimate("read email") == (15, "Work")
