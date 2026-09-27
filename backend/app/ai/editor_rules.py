import re
from typing import Literal, cast

from app.schemas.patches import PatchOp
from app.ai.router import has_diacritics, normalize
from app.schemas.drafts import TodayDraft
from pydantic import TypeAdapter


_ARTICLES = {"a", "an", "the"}


def _title_tokens(value: str) -> tuple[str, ...]:
    """Canonical title words for conservative near-match resolution."""
    return tuple(
        token
        for token in re.findall(r"[a-z0-9]+", normalize(value))
        if token not in _ARTICLES
    )


def _referenced_title(text: str) -> str | None:
    match = re.search(
        r"\b(?:change|update|sua|doi)\s+(.+?)\s+(?:to\s+\d+|and\s+mark\b|thanh\s+\d+)",
        text,
    )
    return match.group(1).strip() if match else None


def _resolve_task_id(text: str, draft: TodayDraft) -> str | None:
    ordinal_match = re.search(r"\b(first|1st|second|2nd)\b", text)
    ordinal = (
        0 if ordinal_match and ordinal_match.group(1) in {"first", "1st"}
        else 1 if ordinal_match else None
    )
    exact = [
        task for task in draft.tasks
        if normalize(task.title) in text and len(normalize(task.title)) > 2
    ]
    if len(exact) > 1:
        if ordinal is not None and ordinal < len(exact):
            return exact[ordinal].id
        raise ValueError("Which task did you mean?")
    if len(exact) == 1:
        return exact[0].id

    reference = _referenced_title(text)
    if not reference:
        return None
    reference_tokens = set(_title_tokens(reference))
    if len(reference_tokens) < 2:
        return None
    plausible = []
    for task in draft.tasks:
        candidate_tokens = set(_title_tokens(task.title))
        shorter = min(len(reference_tokens), len(candidate_tokens))
        if shorter >= 2 and (
            reference_tokens <= candidate_tokens or candidate_tokens <= reference_tokens
        ):
            plausible.append(task)
    if len(plausible) > 1:
        if ordinal is not None and ordinal < len(plausible):
            return plausible[ordinal].id
        raise ValueError("Which task did you mean?")
    return plausible[0].id if plausible else None


_REPEAT_WORDS_RE = re.compile(
    r"\b(lap lai|repeat|repeats|repeating|moi ngay|hang ngay|hang tuan|moi tuan"
    r"|daily|weekly|every)\b"
)


def _recurrence_edit(
    message: str, text: str, task_id: str, draft: TodayDraft
) -> PatchOp | None:
    """Turn "cho việc 1 lặp lại mỗi ngày" into a set_recurrence patch."""
    from datetime import timedelta

    from app.ai.parser import (
        THIS_WEEK_RE,
        _collapse_weekday_lists,
        _take_day,
        _take_recurrence,
    )

    if not _REPEAT_WORDS_RE.search(text):
        return None
    if has_diacritics(message):
        stop = re.search(
            r"(?<!\w)(bỏ|không|thôi|dừng|ngừng|hủy|huỷ|xóa|xoá|tắt)(?!\w)", message.casefold()
        )
    else:
        stop = re.search(r"\b(khong|thoi|dung|ngung|huy|bo|xoa|tat)\b", text)
    stop = stop or re.search(r"\b(stop|no longer|don'?t|not)\b", text)
    if stop and re.search(r"\b(lap lai|repeat|repeats|repeating)\b", text):
        return TypeAdapter(PatchOp).validate_python(
            dict(op="set_recurrence", task_id=task_id, recurrence=None)
        )
    collapsed = _collapse_weekday_lists(message)
    freq, fixed_days, rest = _take_recurrence(collapsed)
    _, named_days, _, _ = _take_day(rest)
    if freq is None:
        if len(named_days) >= 1 and re.search(r"\b(lap lai|repeat|repeats)\b", text):
            freq = "WEEKLY"
        else:
            raise ValueError(
                "Lặp lại mỗi ngày hay vào những ngày nào trong tuần?"
                if has_diacritics(message)
                else "Should it repeat every day or on which weekdays?"
            )
    weekdays = list(fixed_days or (named_days if freq == "WEEKLY" else ()))
    until = None
    if THIS_WEEK_RE.search(collapsed):
        until = draft.planDate + timedelta(days=6 - draft.planDate.weekday())
    return TypeAdapter(PatchOp).validate_python(
        dict(
            op="set_recurrence",
            task_id=task_id,
            recurrence=dict(freq=freq, weekdays=weekdays, until=until),
        )
    )


def parse_edit(message: str, draft: TodayDraft, ctx_date=None) -> list[PatchOp] | None:
    text = normalize(message)

    # Global deterministic commands
    if re.search(r"\b(move|doi|chuyen)\b.*\b(tomorrow|ngay mai|mai)\b", text):
        if ctx_date:
            return [
                TypeAdapter(PatchOp).validate_python(
                    dict(op="set_plan_date", plan_date=ctx_date)
                )
            ]

    # The number must follow the verb directly, and accented input must say
    # "nhân" (multiply): stripped of accents, "nhận thêm 2 email" (receive two
    # more emails) would otherwise rescale every task in the draft.
    if has_diacritics(message):
        scale_match = re.search(
            r"(?<!\w)(?:scale(?: by)?|nhân(?: lên)?|x)\s*(\d+(?:[.,]\d+)?)(?!\w)",
            message.casefold(),
        )
    else:
        scale_match = re.search(
            r"\b(?:scale(?: by)?|nhan(?: len)?|x)\s*(\d+(?:\.\d+)?)\b", text
        )
    if scale_match:
        factor = float(scale_match.group(1).replace(",", "."))
        return [
            TypeAdapter(PatchOp).validate_python(
                dict(op="scale_durations", factor=factor)
            )
        ]

    number = re.search(r"\b(?:task|viec)\s*(\d+)\b", text)
    task_id = None
    if number:
        index = int(number.group(1)) - 1
        if not 0 <= index < len(draft.tasks):
            raise ValueError("Task number out of range.")
        task_id = draft.tasks[index].id
    else:
        task_id = _resolve_task_id(text, draft)

    if not task_id:
        return None

    # Before "remove": "bỏ lặp lại việc 1" stops repetition, it keeps the task.
    recurrence_op = _recurrence_edit(message, text, task_id, draft)
    if recurrence_op is not None:
        return [recurrence_op]

    if re.search(r"\b(remove|delete|drop|bo|xoa)\b", text):
        return [
            TypeAdapter(PatchOp).validate_python(
                dict(op="remove_task", task_id=task_id)
            )
        ]

    duration = re.search(r"\b(\d+)\s*(?:p|phut|min|minutes?)\b", text)
    optional = bool(re.search(r"\b(optional|khong bat buoc)\b", text))
    core = bool(re.search(r"\b(core|bat buoc)\b", text))
    if duration or optional or core:
        values: dict[str, object] = dict(op="update_task", task_id=task_id)
        if duration:
            values["duration_min"] = int(duration.group(1))
        if optional:
            values["importance"] = "OPTIONAL"
        elif core:
            values["importance"] = "CORE"
        return [
            TypeAdapter(PatchOp).validate_python(values)
        ]

    priority = re.search(r"\b(low|medium|high|urgent)\s+priority\b", text)
    if priority:
        return [
            TypeAdapter(PatchOp).validate_python(
                dict(
                    op="update_task",
                    task_id=task_id,
                    priority=cast(
                        Literal["LOW", "MEDIUM", "HIGH", "URGENT"],
                        priority.group(1).upper(),
                    ),
                )
            )
        ]

    return None
