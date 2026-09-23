import pytest
from app.ai.parser import parse


def assert_deterministic(text, expected_titles, expected_minutes):
    results = [parse(text) for _ in range(2)]
    snapshots = [
        (
            len(result.tasks),
            [task.title for task in result.tasks],
            [task.duration_min for task in result.tasks],
            list(result.unresolved),
        )
        for result in results
    ]
    expected = (len(expected_titles), expected_titles, expected_minutes, [])
    assert snapshots == [expected, expected]
    return results

@pytest.mark.parametrize("text,expected_titles,expected_minutes", [
    ("Read chapter 3 for 45 min, review flashcards for 30 min", ["Read chapter 3", "review flashcards"], [45, 30]),
    ("Read chapter 3 for 45 min; review flashcards for 30 min", ["Read chapter 3", "review flashcards"], [45, 30]),
    ("Read chapter 3 for 45 min\nReview flashcards for 30 min", ["Read chapter 3", "Review flashcards"], [45, 30]),
    ("Read chapter 3 for 45 min\r\nReview flashcards for 30 min", ["Read chapter 3", "Review flashcards"], [45, 30]),
    ("  Read chapter 3 for 45 min  ,   review flashcards for 30 min  ", ["Read chapter 3", "review flashcards"], [45, 30]),
    ("Read chapter 3, section 2 for 45 min", ["Read chapter 3, section 2"], [45]),
])
def test_ps_001_separators(text, expected_titles, expected_minutes):
    results = assert_deterministic(
        f"Plan my day: {text}", expected_titles, expected_minutes
    )
    assert all(task.source == "USER" for result in results for task in result.tasks)
    assert all(result.confidence >= 0.8 for result in results)

@pytest.mark.parametrize("text,expected_titles,expected_minutes", [
    ("1. Study algorithms for 1h\n2. Practice SQL for 90p", ["Study algorithms", "Practice SQL"], [60, 90]),
    ("1) Study algorithms for 1h\n2) Practice SQL for 90p", ["Study algorithms", "Practice SQL"], [60, 90]),
    ("- Read chapter 3 for 45 min\n- Review flashcards for 30 min", ["Read chapter 3", "Review flashcards"], [45, 30]),
    ("* Read chapter 3 for 45 min\n* Review flashcards for 30 min", ["Read chapter 3", "Review flashcards"], [45, 30]),
])
def test_ps_002_lists(text, expected_titles, expected_minutes):
    assert_deterministic(text, expected_titles, expected_minutes)

@pytest.mark.parametrize("text,expected_minutes", [
    ("Study 1h", 60),
    ("Study 90p", 90),
    ("Study 45 min", 45),
])
def test_ps_003_simple_durations(text, expected_minutes):
    assert_deterministic(text, ["Study"], [expected_minutes])

@pytest.mark.parametrize("text,expected_minutes", [
    ("Study 1h30", 90),
    ("Study one-and-a-half hours", 90),
])
def test_ps_004_compound_word_durations(text, expected_minutes):
    assert_deterministic(text, ["Study"], [expected_minutes])

@pytest.mark.parametrize("text,expected_minutes", [
    ("Study 1.5 hours", 90),
    ("Study 0.5h", 30),
])
def test_ps_005_decimal_hours(text, expected_minutes):
    assert_deterministic(text, ["Study"], [expected_minutes])


def test_ps_006_fixed_start():
    results = assert_deterministic("Study algorithms at 14:00 for 60 min", ["Study algorithms"], [60])
    for result in results:
        task = result.tasks[0]
        assert task.fixed_start == "14:00"
        assert task.fixed_end is None

def test_ps_007_fixed_interval():
    results = assert_deterministic("Practice SQL from 14:00 to 15:30", ["Practice SQL"], [90])
    for result in results:
        task = result.tasks[0]
        assert task.fixed_start == "14:00"
        assert task.fixed_end == "15:30"
        assert len(result.windows) == 0

def test_ps_008_deadline():
    results = assert_deterministic("Finish the report for 60 min before 17:00", ["Finish the report"], [60])
    for result in results:
        task = result.tasks[0]
        assert task.deadline == "17:00"
        assert task.fixed_start is None

def test_ps_009_explicit_availability():
    results = assert_deterministic("I am available from 18:00 to 21:00; study algorithms for 60 min", ["study algorithms"], [60])
    for result in results:
        assert result.windows == (("18:00", "21:00"),)

def test_ps_010_time_budget_only():
    results = assert_deterministic("I only have 2 hours available today", [], [])
    for result in results:
        assert "Normalized budget: 120 minutes" in result.assumptions

def test_ps_015_tomorrow_offset():
    results = assert_deterministic("Tomorrow, study algorithms for 60 min", ["study algorithms"], [60])
    for result in results:
        assert result.plan_date_offset == 1
