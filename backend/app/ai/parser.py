"""Zero-token task extraction for explicit Vietnamese and English plans.

Besides tasks and durations, the parser recognises which day each task is for
("mai", "ngày kia", "thứ 2", "25/9", "tuần sau"), repeating work ("mỗi ngày",
"hàng tuần", "mỗi thứ 2, 4"), and weekly budgets to spread ("tuần này ôn thi
10 tiếng"). Days stay relative here; ``DayRef.resolve`` turns them into dates
using the user's trusted local "today".
"""

import re
import unicodedata
from dataclasses import dataclass, replace
from datetime import date, timedelta
from typing import Literal

from app.ai.estimates import estimate
from app.ai.router import normalize

HOUR = r"(?:h|g|giờ|gio|tiếng|tieng|hours?|hrs?)"
MINUTE = r"(?:p|m|phút|phut|mins?|minutes?)"
HOUR_MINUTE_RE = re.compile(r"(?<!\w)(\d{1,2})\s*h\s*(\d{1,2})(?!\w)", re.IGNORECASE)
HOUR_RE = re.compile(rf"(?<!\w)(\d+(?:[.,]\d+)?)\s*{HOUR}\b", re.IGNORECASE)
MINUTE_RE = re.compile(rf"(?<!\w)(\d+)\s*{MINUTE}\b", re.IGNORECASE)
TIME_RE = r"(?:2[0-3]|[01]?\d)(?::[0-5]\d|h[0-5]?\d|h)?(?![\d/])"
# A clock time may carry a period of day. Unaccented "sang"/"toi" are left out
# on purpose: they usually mean "go over" and "I", not "morning"/"evening".
PERIOD_RE = r"(?:\s*(sáng|trưa|chiều|tối|đêm|chieu|trua|dem|am|pm)(?!\w))?"
DURATION_UNIT_AHEAD = (
    r"(?!\s*(?:tiếng|tieng|phút|phut|p\b|mins?\b|minutes?|hours?|hrs?))"
)
WINDOW_RE = re.compile(
    rf"(?:rảnh\s+)?(?:từ|tu|from)\s+({TIME_RE}){PERIOD_RE}\s+(?:đến|den|to|tới|toi)\s+({TIME_RE}){PERIOD_RE}",
    re.IGNORECASE,
)
FIXED_RE = re.compile(
    rf"(?:lúc|luc|vào|vao|at)\s+({TIME_RE}){DURATION_UNIT_AHEAD}{PERIOD_RE}",
    re.IGNORECASE,
)
DEADLINE_RE = re.compile(
    rf"(?:trước|truoc|before|deadline)\s+({TIME_RE}){PERIOD_RE}", re.IGNORECASE
)
# A bare "9h30", "9h", "9 giờ rưỡi" or "2h chiều" names a clock time, not a
# duration, when it has a period of day or an hour nobody works non-stop.
CLOCK_TOKEN_RE = re.compile(
    r"(?<![\w/:.,])(\d{1,2})\s*(?:h|g|giờ|gio)\s*(\d{2}|rưỡi|ruoi)?"
    r"(?:\s*(sáng|trưa|chiều|tối|đêm|chieu|trua|dem|am|pm))?(?!\w)",
    re.IGNORECASE,
)
CLOCK_MIN_BARE_HOUR = 6
DURATION_CONTEXT_RE = re.compile(r"(?:trong|for|mất|mat|khoảng|khoang)\s*$", re.IGNORECASE)
HALF_HOUR_RE = re.compile(
    r"(?<!\w)(\d+)\s*(?:tiếng|tieng|giờ|gio|h)\s*(?:rưỡi|ruoi)(?!\w)", re.IGNORECASE
)
HARD_SPLIT_RE = re.compile(
    r"\s*(?:;|\n|\s+và\s+|\s+and\s+|\s+rồi\s+|\s+then\s+)\s*", re.IGNORECASE
)
PREFIX_RE = re.compile(
    r"^\s*(?:plan my (?:day|week)|schedule my (?:day|week)|today(?=\s*[:：])|lập lịch|lên kế hoạch|xếp lịch|sắp xếp lịch|plan|hãy|please)\s*[:：-]?\s*",
    re.IGNORECASE,
)
BUDGET_RE = re.compile(
    r"\b(?:i only have|i have|tôi chỉ có|mình chỉ có|chỉ có)\s+(.+?)\s+(?:available|rảnh|để làm|today|hôm nay)\b",
    re.IGNORECASE,
)

_VARIANTS = {
    "a": "aàáảãạăằắẳẵặâầấẩẫậ",
    "e": "eèéẻẽẹêềếểễệ",
    "i": "iìíỉĩị",
    "o": "oòóỏõọôồốổỗộơờớởỡợ",
    "u": "uùúủũụưừứửữự",
    "y": "yỳýỷỹỵ",
    "d": "dđ",
}


def vi(pattern: str) -> re.Pattern[str]:
    """Compile an ASCII pattern so each vowel/d also matches its accented forms.

    One readable pattern such as ``thu (hai|ba)`` then matches "thứ hai",
    "thu hai" and "THỨ BA" in the original text, so a match can be cut out of
    the user's words without losing positions to normalisation.
    """
    out: list[str] = []
    in_class = False
    index = 0
    while index < len(pattern):
        char = pattern[index]
        if char == "\\":
            out.append(pattern[index : index + 2])
            index += 2
            continue
        if char == "[" and not in_class:
            in_class = True
        elif char == "]" and in_class:
            in_class = False
        variants = _VARIANTS.get(char)
        if variants:
            out.append(variants if in_class else f"[{variants}]")
        else:
            out.append(char)
        index += 1
    return re.compile("".join(out), re.IGNORECASE)


WEEKDAY_TOKEN = r"(?:[2-7]|hai|ba|tu|nam|sau|bay)"
_VI_WEEKDAYS = {"2": 0, "hai": 0, "3": 1, "ba": 1, "4": 2, "tu": 2,
                "5": 3, "nam": 3, "6": 4, "sau": 4, "7": 5, "bay": 5,
                "cn": 6, "chu nhat": 6}
_EN_WEEKDAYS = {"monday": 0, "tuesday": 1, "wednesday": 2, "thursday": 3,
                "friday": 4, "saturday": 5, "sunday": 6}
EN_WEEKDAY = r"(?:monday|tuesday|wednesday|thursday|friday|saturday|sunday)"

# "thứ 2, 4 và 6" / "thứ 2 và thứ 4" -> "thứ 2/4/6" so "và" does not split them.
VI_WEEKDAY_LIST_RE = vi(
    rf"\bthu\s*({WEEKDAY_TOKEN}|chu nhat)\b((?:\s*(?:,|/|&|\bva\b|\band\b)\s*(?:thu\s*)?(?:{WEEKDAY_TOKEN}|chu nhat)\b)+)"
)
VI_LIST_ITEM_RE = vi(rf"({WEEKDAY_TOKEN}|chu nhat)\b")
EN_WEEKDAY_LIST_RE = re.compile(
    rf"\b({EN_WEEKDAY})s?((?:\s*(?:,|/|&|\band\b)\s*{EN_WEEKDAY}s?\b)+)", re.IGNORECASE
)
VI_WEEKDAY_RE = vi(
    rf"\b(?:vao\s+)?(?:(?:cac|moi)\s+)?(?:thu\s*({WEEKDAY_TOKEN}(?:/(?:{WEEKDAY_TOKEN}|cn|chu nhat))*)|(chu nhat|cn))\b"
    r"(\s+tuan\s+(?:sau|toi)\b)?"
)
EN_WEEKDAY_RE = re.compile(
    rf"\b(?:on\s+)?(next\s+)?({EN_WEEKDAY}s?(?:/{EN_WEEKDAY}s?)*)\b", re.IGNORECASE
)
DATE_RE = re.compile(
    r"(?:\b(?:ngày|ngay|on)\s+)?(?<![\d/])(\d{1,2})/(\d{1,2})(?:/(20\d{2}))?(?![\d/])",
    re.IGNORECASE,
)
TODAY_RE = vi(r"\b(hom nay|today|tonight)\b")
TOMORROW_RE = vi(
    r"\b(ngay mai|tomorrow|(?:sang|trua|chieu) mai|(?:minh|tui) mai|mai (?=(?:minh|tui)\s))"
    r"|^\s*mai\b(?!\s*(?:mot|sau)\b)"
)
TOMORROW_EVENING_RE = re.compile(r"\b(?:tối mai|tôi mai\b|mai (?=tôi\s))", re.IGNORECASE)
DAY_AFTER_RE = vi(r"\b(ngay kia|ngay mot|day after tomorrow)\b")
DAILY_RE = vi(r"\b(moi ngay|hang ngay|ngay nao cung|every ?day|daily|each day)\b")
WEEKDAYS_ONLY_RE = vi(r"\b(cac ngay trong tuan|ngay thuong|weekdays|every weekday)\b")
WEEKEND_RE = vi(r"\b((?:moi|hang)\s+cuoi tuan|every weekend|weekends)\b")
WEEKLY_RE = vi(r"\b(hang tuan|moi tuan|weekly|every week|each week)\b")
EVERY_PREFIX_RE = vi(
    rf"\b(moi|every|each)\s+(?=(?:thu\s*{WEEKDAY_TOKEN}|chu nhat|{EN_WEEKDAY}))"
)
THIS_WEEK_RE = vi(r"\b(trong\s+)?(tuan nay|this week|ca tuan|suot tuan|all week|whole week)\b")
NEXT_WEEK_RE = vi(r"\b(trong\s+)?(tuan sau|tuan toi|next week)\b")
# English fillers stay ASCII-only: through vi() "on" would also eat "ôn" (review).
LEADING_FILLER_RE = re.compile(
    r"^(?:\s*(?:[,:\-]|vào\b|vao\b|on\b|ngày\b|ngay\b|lúc\b|luc\b|trong\b|in\b"
    r"|theo thứ tự\b|lần lượt\b|in order\b|chắc chắn\b|chắc là\b|có lẽ\b|maybe\b|probably\b))+",
    re.IGNORECASE,
)
# A leading "mình"/"tôi" left after cutting "Mai" from "Mai mình học" is not
# part of the task. Unaccented "toi" is skipped: it may be "tới" (go to).
LEADING_PRONOUN_RE = re.compile(r"^\s*(?:mình|tôi|tui|tớ|minh)\s+(?=\S)", re.IGNORECASE)
TRAILING_FILLER_RE = re.compile(
    r"(?:\s*(?:[,:\-]|vào|vao|\bon|ngày|ngay|lúc|luc|trong|\bin|của))+\s*$", re.IGNORECASE
)
MIN_SPREAD_CHUNK = 30


def _apply_period(hour: int, period: str | None) -> int:
    if not period:
        return hour
    period = normalize(period)
    if period in {"chieu", "toi", "dem", "pm"} and hour < 12:
        return hour + 12
    if period == "trua" and hour <= 3:
        return hour + 12
    if period == "am" and hour == 12:
        return 0
    return hour


def _clock(raw: str, period: str | None = None) -> str:
    raw = normalize(raw).replace("h", ":")
    if ":" not in raw:
        raw += ":00"
    elif raw.endswith(":"):
        raw += "00"
    hour_text, minute_text = raw.split(":", 1)
    hour = _apply_period(int(hour_text), period)
    return f"{hour:02d}:{int(minute_text):02d}"


@dataclass(frozen=True)
class DayRef:
    """A day relative to the user's local today."""

    kind: Literal["offset", "weekday", "date"]
    value: int
    month: int = 0
    year: int = 0
    next_week: bool = False

    def resolve(self, today: date) -> date:
        if self.kind == "offset":
            return today + timedelta(days=self.value)
        if self.kind == "weekday":
            if self.next_week:
                monday = today - timedelta(days=today.weekday()) + timedelta(days=7)
                return monday + timedelta(days=self.value)
            return today + timedelta(days=(self.value - today.weekday()) % 7)
        try:
            resolved = date(self.year or today.year, self.month, self.value)
        except ValueError:
            return today
        if not self.year and resolved < today:
            try:
                resolved = resolved.replace(year=resolved.year + 1)
            except ValueError:
                return today
        return resolved


@dataclass(frozen=True)
class ParsedRecurrence:
    freq: Literal["DAILY", "WEEKLY"]
    weekdays: tuple[int, ...] = ()
    # "mỗi ngày trong tuần này" repeats only until this week's Sunday.
    until_end_of_week: bool = False


@dataclass(frozen=True)
class ParsedTask:
    title: str
    duration_min: int | None
    source: Literal["USER", "RULE", "AI"]
    importance: Literal["CORE", "OPTIONAL"] = "CORE"
    priority: Literal["LOW", "MEDIUM", "HIGH"] = "MEDIUM"
    category: str | None = None
    fixed_start: str | None = None
    fixed_end: str | None = None
    deadline: str | None = None
    day: DayRef | None = None
    recurrence: ParsedRecurrence | None = None
    # Split the duration evenly over the rest of this week or over next week.
    spread: Literal["THIS_WEEK", "NEXT_WEEK"] | None = None
    # An existing unscheduled task or recurring template this came from.
    source_task_id: str | None = None
    recurring_task_id: str | None = None


@dataclass(frozen=True)
class ParsedPlan:
    tasks: tuple[ParsedTask, ...] = ()
    windows: tuple[tuple[str, str], ...] = ()
    plan_date_offset: int = 0
    unresolved: tuple[int, ...] = ()
    confidence: float = 0.0
    assumptions: tuple[str, ...] = ()
    # The one day named for the whole message, if any; per-task days win.
    day: DayRef | None = None


def _duration(segment: str) -> tuple[int | None, str]:
    text = segment
    total = 0
    found = False
    word_duration = re.search(
        r"\b(?:one-and-a-half hours?|an hour and a half|một tiếng rưỡi|mot tieng ruoi)\b",
        text,
        re.IGNORECASE,
    )
    if word_duration:
        total = 90
        text = text[: word_duration.start()] + " " + text[word_duration.end() :]
        found = True
    for match in reversed(list(HOUR_MINUTE_RE.finditer(text))):
        total += int(match.group(1)) * 60 + int(match.group(2))
        text = text[: match.start()] + " " + text[match.end() :]
        found = True
    for match in reversed(list(HOUR_RE.finditer(text))):
        total += round(float(match.group(1).replace(",", ".")) * 60)
        text = text[: match.start()] + " " + text[match.end() :]
        found = True
    for match in reversed(list(MINUTE_RE.finditer(text))):
        total += int(match.group(1))
        text = text[: match.start()] + " " + text[match.end() :]
        found = True
    if not found and re.search(
        r"\b(nửa tiếng|nua tieng|half an hour)\b", text, re.IGNORECASE
    ):
        total = 30
        text = re.sub(
            r"\b(nửa tiếng|nua tieng|half an hour)\b", " ", text, flags=re.IGNORECASE
        )
        found = True
    if found:
        text = re.sub(r"\s+\b(?:for|trong)\b\s*$", "", text, flags=re.IGNORECASE)
    return (total if found else None), text


def _cut(text: str, match: re.Match[str]) -> str:
    return text[: match.start()] + " " + text[match.end() :]


def _clock_token(segment: str) -> tuple[str | None, str]:
    """Take the first bare clock time ("họp 9h30", "2h chiều") out of a segment."""
    for match in CLOCK_TOKEN_RE.finditer(segment):
        hour = int(match.group(1))
        minute_raw, period = match.group(2), match.group(3)
        if hour > 23:
            continue
        if DURATION_CONTEXT_RE.search(segment[: match.start()]):
            continue
        if period is None and hour < CLOCK_MIN_BARE_HOUR:
            continue
        if minute_raw is None:
            minute = 0
        elif normalize(minute_raw) == "ruoi":
            minute = 30
        else:
            minute = int(minute_raw)
            if minute > 59:
                continue
        hour = _apply_period(hour, period)
        if hour > 23:
            continue
        return f"{hour:02d}:{minute:02d}", _cut(segment, match)
    return None, segment


def _collapse_weekday_lists(text: str) -> str:
    def vi_list(match: re.Match[str]) -> str:
        items = [match.group(1)] + VI_LIST_ITEM_RE.findall(match.group(2))
        return "thứ " + "/".join(normalize(item) for item in items)

    def en_list(match: re.Match[str]) -> str:
        items = re.findall(EN_WEEKDAY, match.group(0), re.IGNORECASE)
        return "/".join(item.lower() for item in items)

    text = VI_WEEKDAY_LIST_RE.sub(vi_list, text)
    return EN_WEEKDAY_LIST_RE.sub(en_list, text)


def _weekday_values(raw: str) -> tuple[int, ...]:
    values = []
    for item in raw.split("/"):
        key = normalize(item).removesuffix("s")
        if key in _EN_WEEKDAYS:
            values.append(_EN_WEEKDAYS[key])
        elif key in _VI_WEEKDAYS:
            values.append(_VI_WEEKDAYS[key])
    return tuple(dict.fromkeys(values))


def _is_trailing(segment: str, match: re.Match[str]) -> bool:
    return not segment[match.end() :].strip(" .,!?;:")


def _take_day(segment: str) -> tuple[DayRef | None, tuple[int, ...], str, bool]:
    """Remove one day reference.

    Returns it, every weekday named, the rest of the segment, and whether the
    day closed the segment ("... ngày mai"), which lets it cover earlier tasks.
    """
    found = _find_day(segment)
    if found is None:
        return None, (), segment, False
    ref, weekdays, match = found
    return ref, weekdays, _cut(segment, match), _is_trailing(segment, match)


def _find_day(
    segment: str,
) -> tuple[DayRef, tuple[int, ...], re.Match[str]] | None:
    for pattern, offset in (
        (DAY_AFTER_RE, 2),
        (TOMORROW_EVENING_RE, 1),
        (TOMORROW_RE, 1),
        (TODAY_RE, 0),
    ):
        match = pattern.search(segment)
        if match:
            return DayRef("offset", offset), (), match
    for match in VI_WEEKDAY_RE.finditer(segment):
        # The accent-insensitive "thu tu" also matches "thứ tự" (order).
        if "tự" in match.group(0).casefold():
            continue
        weekdays = _weekday_values(match.group(1) or match.group(2) or "")
        if weekdays:
            ref = DayRef("weekday", weekdays[0], next_week=bool(match.group(3)))
            return ref, weekdays, match
    match = EN_WEEKDAY_RE.search(segment)
    if match:
        weekdays = _weekday_values(match.group(2))
        if weekdays:
            ref = DayRef("weekday", weekdays[0], next_week=bool(match.group(1)))
            return ref, weekdays, match
    match = DATE_RE.search(segment)
    if match:
        day, month = int(match.group(1)), int(match.group(2))
        if 1 <= day <= 31 and 1 <= month <= 12:
            year = int(match.group(3)) if match.group(3) else 0
            return DayRef("date", day, month=month, year=year), (), match
    return None


def _take_recurrence(
    segment: str,
) -> tuple[Literal["DAILY", "WEEKLY"] | None, tuple[int, ...], str]:
    for pattern, freq, weekdays in (
        (WEEKDAYS_ONLY_RE, "WEEKLY", (0, 1, 2, 3, 4)),
        (WEEKEND_RE, "WEEKLY", (5, 6)),
        (DAILY_RE, "DAILY", ()),
        (WEEKLY_RE, "WEEKLY", ()),
    ):
        match = pattern.search(segment)
        if match:
            return freq, weekdays, _cut(segment, match)  # type: ignore[return-value]
    match = EVERY_PREFIX_RE.search(segment)
    if match:
        return "WEEKLY", (), _cut(segment, match)
    return None, (), segment


def _clean_title(title: str) -> str:
    title = LEADING_FILLER_RE.sub("", title)
    title = LEADING_PRONOUN_RE.sub("", title)
    title = TRAILING_FILLER_RE.sub("", title)
    return re.sub(r"\s+", " ", title).strip(" .:-,?!\t\n")


def smart_split(text: str) -> list[str]:
    """Split task separators without treating descriptive commas as boundaries."""
    parts: list[str] = []
    for chunk in HARD_SPLIT_RE.split(text):
        start = 0
        for match in re.finditer(r",", chunk):
            remainder = chunk[match.end() :]
            if (
                _duration(chunk[start : match.start()])[0] is not None
                and _duration(remainder)[0] is not None
            ):
                parts.append(chunk[start : match.start()])
                start = match.end()
        parts.append(chunk[start:])
    return parts


def extract_day_ref(message: str) -> tuple[DayRef | None, int]:
    """Isolate calendar date/day resolution from full task parsing."""
    text = unicodedata.normalize("NFC", message.strip())
    text = PREFIX_RE.sub("", text)
    text = _collapse_weekday_lists(text)

    named_days: list[DayRef] = []
    trailing_day: DayRef | None = None
    first_has_day = False

    segments = smart_split(text)
    for position, raw in enumerate(segments):
        segment = re.sub(r"^\s*(?:[-*•]|\d+[.)])\s*", "", raw).strip(" .:-")
        segment = PREFIX_RE.sub("", segment)
        if not segment:
            continue
        day, _, _, trailing = _take_day(segment)
        if day is not None:
            named_days.append(day)
            if position == 0:
                first_has_day = True
            if trailing and position == len(segments) - 1:
                trailing_day = day

    distinct_days = list(dict.fromkeys(named_days))
    message_day = (
        distinct_days[0]
        if len(distinct_days) == 1 and (trailing_day is not None or first_has_day or len(segments) == 1)
        else (distinct_days[0] if len(distinct_days) == 1 else None)
    )
    offset = (
        message_day.value
        if message_day is not None and message_day.kind == "offset"
        else 0
    )
    return message_day, offset


def parse(message: str, *, lenient: bool = False) -> ParsedPlan:
    text = unicodedata.normalize("NFC", message.strip())
    text = PREFIX_RE.sub("", text)
    text = _collapse_weekday_lists(text)

    assumptions = []
    for match in reversed(list(BUDGET_RE.finditer(text))):
        budget_dur, _ = _duration(match.group(1))
        if budget_dur:
            assumptions.append(f"Normalized budget: {budget_dur} minutes")
        text = text[: match.start()] + " " + text[match.end() :]

    windows: list[tuple[str, str]] = []
    tasks: list[ParsedTask] = []
    task_days: list[DayRef | None] = []
    unresolved = []
    named_days: list[DayRef] = []
    trailing_day: DayRef | None = None
    current_day: DayRef | None = None
    segments = smart_split(text)

    for position, raw in enumerate(segments):
        segment = re.sub(r"^\s*(?:[-*•]|\d+[.)])\s*", "", raw).strip(" .:-")
        segment = PREFIX_RE.sub("", segment)
        if not segment:
            continue

        # Repetition first: "mỗi thứ 2" must not leave a stray "mỗi".
        freq, fixed_weekdays, segment = _take_recurrence(segment)
        day, named_weekdays, segment, trailing = _take_day(segment)
        spread: Literal["THIS_WEEK", "NEXT_WEEK"] | None = None
        this_week = THIS_WEEK_RE.search(segment)
        next_week = NEXT_WEEK_RE.search(segment)
        if this_week:
            segment = _cut(segment, this_week)
            spread = "THIS_WEEK"
        elif next_week:
            segment = _cut(segment, next_week)
            if day is not None and day.kind == "weekday":
                day = DayRef("weekday", day.value, next_week=True)
            else:
                spread = "NEXT_WEEK"

        recurrence = None
        if freq is not None:
            weekdays = fixed_weekdays or (named_weekdays if freq == "WEEKLY" else ())
            if weekdays and day is None:
                day = DayRef("weekday", weekdays[0])
            recurrence = ParsedRecurrence(
                freq=freq,
                weekdays=tuple(weekdays),
                until_end_of_week=spread == "THIS_WEEK",
            )
            if spread == "THIS_WEEK":
                spread = None
            elif spread == "NEXT_WEEK" and day is None:
                day = DayRef("weekday", weekdays[0] if weekdays else 0, next_week=True)
                spread = None
        elif len(named_weekdays) > 1:
            # "Thứ 2/4 học toán" without "mỗi" means those days this week.
            recurrence = ParsedRecurrence(
                freq="WEEKLY", weekdays=named_weekdays, until_end_of_week=True
            )

        if day is not None:
            named_days.append(day)
            current_day = day
            if trailing and position == len(segments) - 1:
                trailing_day = day

        interval_start, interval_end = None, None
        window_match = WINDOW_RE.search(segment)
        if window_match:
            interval_start = _clock(window_match.group(1), window_match.group(2))
            interval_end = _clock(window_match.group(3), window_match.group(4))
            segment = _cut(segment, window_match)

        fixed = FIXED_RE.search(segment)
        fixed_start = _clock(fixed.group(1), fixed.group(2)) if fixed else None
        if fixed:
            segment = _cut(segment, fixed)
        deadline = DEADLINE_RE.search(segment)
        deadline_time = _clock(deadline.group(1), deadline.group(2)) if deadline else None
        if deadline:
            segment = _cut(segment, deadline)
        if fixed_start is None:
            fixed_start, segment = _clock_token(segment)
        segment = HALF_HOUR_RE.sub(
            lambda m: f" {int(m.group(1)) * 60 + 30}p ", segment
        )
        duration, segment = _duration(segment)
        plain = normalize(segment)
        optional = bool(
            re.search(
                r"\b(nếu còn thời gian|neu con thoi gian|nếu kịp|neu kip|optional|if time|not urgent)\b"
                r"|if there is time|if i have time|when time permits|time permitting",
                plain,
            )
        )
        urgent = bool(
            re.search(
                r"\b(quan trọng|quan trong|gấp|gap|urgent|important|phải xong|phai xong)\b",
                plain,
            )
        )
        segment = re.sub(
            r"\b(nếu còn thời gian|nếu kịp|optional|if time|not urgent|quan trọng|gấp|urgent|important|phải xong)\b",
            " ",
            segment,
            flags=re.IGNORECASE,
        )
        title = _clean_title(segment)

        is_avail = normalize(title) in {
            "i am available", "im available", "my availability is", "toi ranh", "minh ranh", "available", "toi co the lam"
        }

        if len(title) < 2 or not any(c.isalnum() for c in title) or normalize(title) in {"hom nay", "today", "toi", "i", "can", "muon", "minh"} or is_avail:
            if interval_start and interval_end and interval_start < interval_end:
                windows.append((interval_start, interval_end))
            continue

        fixed_end = None
        if interval_start and interval_end:
            fixed_start = interval_start
            fixed_end = interval_end
            if duration is None:
                from datetime import datetime
                t1 = datetime.strptime(interval_start, "%H:%M")
                t2 = datetime.strptime(interval_end, "%H:%M")
                duration = int((t2 - t1).total_seconds() / 60)
                if duration <= 0:
                    duration = None

        source: Literal["USER", "RULE"] = "USER" if duration is not None else "RULE"
        guessed = estimate(title) if duration is None else None
        category: str | None
        if guessed:
            duration, category = guessed
        else:
            other_guess = estimate(title)
            category = other_guess[1] if other_guess else None
        if duration is None:
            unresolved.append(len(tasks))
            if lenient:
                duration = 45
                assumptions.append(f"Estimated 45 minutes for {title}")
        tasks.append(
            ParsedTask(
                title=title,
                duration_min=duration,
                source=source,
                importance="OPTIONAL" if optional else "CORE",
                priority="LOW" if optional else "HIGH" if urgent else "MEDIUM",
                category=category,
                fixed_start=fixed_start,
                fixed_end=fixed_end,
                deadline=deadline_time,
                recurrence=recurrence,
                spread=spread,
            )
        )
        task_days.append(current_day)

    # A day applies from where it is named onwards ("Học 1h, thứ 6 đi gym"
    # keeps "Học" today). The one exception is a single day closing the whole
    # message ("Học 1h và làm bài 30p ngày mai"), which covers every task.
    distinct_days = list(dict.fromkeys(named_days))
    message_day = (
        distinct_days[0]
        if len(distinct_days) == 1
        and (trailing_day is not None or (task_days and task_days[0] is not None))
        else None
    )
    tasks = [
        _with_day(task, message_day if message_day is not None else task_day)
        for task, task_day in zip(tasks, task_days)
    ]
    offset = (
        message_day.value
        if message_day is not None and message_day.kind == "offset"
        else 0
    )

    confidence = 1.0 if (tasks or windows or assumptions or named_days) else 0.0
    if re.search(
        r"\?|\b(giúp|giup|gợi ý|goi y|nên|nen|không biết|khong biet|suggest|maybe)\b",
        message,
        re.IGNORECASE,
    ):
        confidence -= 0.3
    confidence -= 0.15 * len(unresolved)
    if len(tasks) > 10:
        confidence -= 0.2
    return ParsedPlan(
        tasks=tuple(tasks),
        windows=tuple(windows),
        plan_date_offset=offset,
        unresolved=tuple(unresolved),
        confidence=max(0.0, confidence),
        assumptions=tuple(assumptions),
        day=message_day,
    )


def _with_day(task: ParsedTask, day: DayRef | None) -> ParsedTask:
    return task if day is None else replace(task, day=day)
