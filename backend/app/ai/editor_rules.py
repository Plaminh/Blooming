import re
from typing import Literal, cast

from app.schemas.patches import PatchOp
from app.ai.router import normalize
from app.schemas.drafts import TodayDraft
from pydantic import TypeAdapter

def parse_edit(message: str, draft: TodayDraft) -> list[PatchOp] | None:
    text = normalize(message)
    number = re.search(r"\b(?:task|viec)\s*(\d+)\b", text)
    if number:
        index = int(number.group(1)) - 1
        if not 0 <= index < len(draft.tasks):
            return None
        task_id = draft.tasks[index].id
    else:
        matches = [task for task in draft.tasks if normalize(task.title) in text]
        if len(matches) != 1:
            return None
        task_id = matches[0].id
    if re.search(r"\b(remove|delete|drop|bo|xoa)\b", text):
        return [TypeAdapter(PatchOp).validate_python(dict(op="remove_task", task_id=task_id))]
    duration = re.search(r"\b(\d+)\s*(?:p|phut|min|minutes?)\b", text)
    if duration:
        return [
            TypeAdapter(PatchOp).validate_python(dict(
                op="update_task", task_id=task_id, duration_min=int(duration.group(1))
            ))
        ]
    if re.search(r"\b(optional|khong bat buoc)\b", text):
        return [TypeAdapter(PatchOp).validate_python(dict(op="update_task", task_id=task_id, importance="OPTIONAL"))]
    priority = re.search(r"\b(low|medium|high|urgent)\s+priority\b", text)
    if priority:
        return [
            TypeAdapter(PatchOp).validate_python(dict(
                op="update_task",
                task_id=task_id,
                priority=cast(Literal["LOW", "MEDIUM", "HIGH", "URGENT"], priority.group(1).upper()),
            ))
        ]
    return None
