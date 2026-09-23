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
