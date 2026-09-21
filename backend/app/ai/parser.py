"""Zero-token task extraction for explicit Vietnamese and English day plans."""

import re
from dataclasses import dataclass
from typing import Literal

from app.ai.estimates import estimate
from app.ai.router import normalize

HOUR = r"(?:h|g|giờ|gio|tiếng|tieng|hours?|hrs?)"
MINUTE = r"(?:p|m|phút|phut|mins?|minutes?)"
HOUR_MINUTE_RE = re.compile(r"(?<!\w)(\d{1,2})\s*h\s*(\d{1,2})(?!\w)", re.IGNORECASE)
HOUR_RE = re.compile(rf"(?<!\w)(\d+(?:[.,]\d+)?)\s*{HOUR}\b", re.IGNORECASE)
MINUTE_RE = re.compile(rf"(?<!\w)(\d+)\s*{MINUTE}\b", re.IGNORECASE)
TIME_RE = r"(?:[01]?\d|2[0-3])(?::[0-5]\d|h[0-5]?\d|h)?"
WINDOW_RE = re.compile(
    rf"(?:rảnh\s+)?(?:từ|tu|from)\s+({TIME_RE})\s+(?:đến|den|to|tới|toi)\s+({TIME_RE})",
    re.IGNORECASE,
)
FIXED_RE = re.compile(rf"(?:lúc|luc|vào|vao|at)\s+({TIME_RE})", re.IGNORECASE)
DEADLINE_RE = re.compile(
    rf"(?:trước|truoc|before|deadline)\s+({TIME_RE})", re.IGNORECASE
)
SPLIT_RE = re.compile(
    r"\s*(?:,(?!\d)|;|\n|\s+và\s+|\s+and\s+|\s+rồi\s+|\s+then\s+)\s*", re.IGNORECASE
)
PREFIX_RE = re.compile(
    r"^\s*(?:plan my day|schedule my day|lập lịch|lên kế hoạch|xếp lịch|sắp xếp lịch|plan|hãy|please)\s*[:：-]?\s*",
    re.IGNORECASE,
)


def _clock(raw: str) -> str:
    raw = normalize(raw).replace("h", ":")
    if ":" not in raw:
        raw += ":00"
    elif raw.endswith(":"):
        raw += "00"
    hour, minute = raw.split(":", 1)
    return f"{int(hour):02d}:{int(minute):02d}"


@dataclass(frozen=True)
class ParsedTask:
    title: str
    duration_min: int | None
    source: Literal["USER", "RULE", "AI"]
    importance: Literal["CORE", "OPTIONAL"] = "CORE"
    priority: Literal["LOW", "MEDIUM", "HIGH"] = "MEDIUM"
    category: str | None = None
    fixed_start: str | None = None
    deadline: str | None = None


@dataclass(frozen=True)
class ParsedPlan:
    tasks: tuple[ParsedTask, ...] = ()
    windows: tuple[tuple[str, str], ...] = ()
    plan_date_offset: int = 0
    unresolved: tuple[int, ...] = ()
    confidence: float = 0.0
    assumptions: tuple[str, ...] = ()


def _duration(segment: str) -> tuple[int | None, str]:
    text = segment
    total = 0
    found = False
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
    if not found and re.search(
        r"\b(một tiếng rưỡi|mot tieng ruoi|an hour and a half)\b", text, re.IGNORECASE
    ):
        total = 90
        text = re.sub(
            r"\b(một tiếng rưỡi|mot tieng ruoi|an hour and a half)\b",
            " ",
            text,
            flags=re.IGNORECASE,
        )
        found = True
    return (total if found else None), text


def parse(message: str, *, lenient: bool = False) -> ParsedPlan:
    text = PREFIX_RE.sub("", message.strip())
    offset = (
        1 if re.search(r"\b(ngày mai|ngay mai|tomorrow)\b", text, re.IGNORECASE) else 0
    )
    text = re.sub(r"\b(ngày mai|ngay mai|tomorrow)\b", " ", text, flags=re.IGNORECASE)
    windows: list[tuple[str, str]] = []
    for match in reversed(list(WINDOW_RE.finditer(text))):
        start, end = _clock(match.group(1)), _clock(match.group(2))
        if start < end:
            windows.insert(0, (start, end))
        text = text[: match.start()] + " " + text[match.end() :]
    tasks: list[ParsedTask] = []
    unresolved = []
    assumptions = []
    for raw in SPLIT_RE.split(text):
        segment = re.sub(r"^\s*(?:[-*•]|\d+[.)])\s*", "", raw).strip(" .:-")
        segment = PREFIX_RE.sub("", segment)
        if not segment:
            continue
        fixed = FIXED_RE.search(segment)
        fixed_start = _clock(fixed.group(1)) if fixed else None
        if fixed:
            segment = segment[: fixed.start()] + " " + segment[fixed.end() :]
        deadline = DEADLINE_RE.search(segment)
        deadline_time = _clock(deadline.group(1)) if deadline else None
        if deadline:
            segment = segment[: deadline.start()] + " " + segment[deadline.end() :]
        duration, segment = _duration(segment)
        plain = normalize(segment)
        optional = bool(
            re.search(
                r"\b(nếu còn thời gian|neu con thoi gian|nếu kịp|neu kip|optional|if time|not urgent)\b",
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
        title = re.sub(r"\s+", " ", segment).strip(" .:-")
        if len(title) < 2 or normalize(title) in {
            "hom nay",
            "today",
            "toi",
            "i",
            "can",
            "muon",
        }:
            continue
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
                deadline=deadline_time,
            )
        )
    confidence = 1.0 if tasks else 0.0
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
    )
