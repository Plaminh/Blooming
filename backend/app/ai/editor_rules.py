import re
from typing import Literal, cast

from app.schemas.patches import PatchOp
from app.ai.router import normalize
from app.schemas.drafts import TodayDraft
from pydantic import TypeAdapter


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

    scale_match = re.search(r"\b(scale|nhan)\b.*?\b(\d+(?:\.\d+)?)\b", text)
    if scale_match:
        factor = float(scale_match.group(2))
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
        # Avoid matching generic terms if they are not explicitly task names
        matches = [
            task
            for task in draft.tasks
            if normalize(task.title) in text and len(normalize(task.title)) > 2
        ]

        explicit_action = re.search(
            r"\b(remove|delete|drop|bo|xoa|change|update|sua|optional|core|priority)\b",
            text,
        )
        if explicit_action:
            if len(matches) > 1:
                raise ValueError("Which task did you mean?")
            if len(matches) == 1:
                task_id = matches[0].id
        else:
            if len(matches) == 1:
                task_id = matches[0].id

    if not task_id:
        return None

    if re.search(r"\b(remove|delete|drop|bo|xoa)\b", text):
        return [
            TypeAdapter(PatchOp).validate_python(
                dict(op="remove_task", task_id=task_id)
            )
        ]

    duration = re.search(r"\b(\d+)\s*(?:p|phut|min|minutes?)\b", text)
    if duration:
        return [
            TypeAdapter(PatchOp).validate_python(
                dict(
                    op="update_task",
                    task_id=task_id,
                    duration_min=int(duration.group(1)),
                )
            )
        ]

    if re.search(r"\b(optional|khong bat buoc)\b", text):
        return [
            TypeAdapter(PatchOp).validate_python(
                dict(op="update_task", task_id=task_id, importance="OPTIONAL")
            )
        ]
    if re.search(r"\b(core|bat buoc)\b", text):
        return [
            TypeAdapter(PatchOp).validate_python(
                dict(op="update_task", task_id=task_id, importance="CORE")
            )
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
