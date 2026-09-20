"""Pre-scheduler checks for canonical drafts."""

from app.ai.router import normalize
from app.schemas.drafts import TodayDraft


def check_today(draft: TodayDraft) -> list[str]:
    issues = []
    if not draft.windows:
        issues.append("NO_WINDOWS")
    if not draft.tasks:
        issues.append("NO_TASKS")
    if len(draft.tasks) > 15:
        issues.append("TOO_MANY_TASKS")
    ids = [task.id for task in draft.tasks]
    if len(set(ids)) != len(ids):
        issues.append("DUPLICATE_ID")
    titles = [normalize(task.title) for task in draft.tasks]
    if len(set(titles)) != len(titles):
        issues.append("DUPLICATE_TITLE")
    for task in draft.tasks:
        if not 5 <= task.durationMin <= 480:
            issues.append("INVALID_DURATION")
        if any(dep not in ids or dep == task.id for dep in task.dependencies):
            issues.append("INVALID_DEPENDENCY")
        if task.schedulingType == "FIXED" and (
            task.fixedStart is None
            or task.fixedEnd is None
            or task.fixedEnd <= task.fixedStart
        ):
            issues.append("INVALID_FIXED_TIME")
    graph = {task.id: task.dependencies for task in draft.tasks}
    visiting: set[str] = set()
    visited: set[str] = set()

    def visit(task_id: str) -> bool:
        if task_id in visiting:
            return True
        if task_id in visited or task_id not in graph:
            return False
        visiting.add(task_id)
        cycle = any(visit(dep) for dep in graph[task_id])
        visiting.remove(task_id)
        visited.add(task_id)
        return cycle

    if any(visit(task_id) for task_id in graph):
        issues.append("CYCLIC_DEPENDENCY")
    return list(dict.fromkeys(issues))
