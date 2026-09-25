from copy import deepcopy
from datetime import datetime
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from app.schemas.drafts import RoadmapDraft, TodayDraft
from app.schemas.patches import PatchOp
from app.ai.router import normalize


def apply_patch(
    draft: TodayDraft | RoadmapDraft, ops: list[PatchOp]
) -> TodayDraft | RoadmapDraft:
    if not isinstance(draft, TodayDraft):
        raise ValueError("Roadmap patch operations are not supported")
    result = deepcopy(draft)
    try:
        draft_timezone = ZoneInfo(result.timezone)
    except ZoneInfoNotFoundError as exc:
        raise ValueError(f"Unknown draft timezone: {result.timezone}") from exc
    for op in ops:
        if op.op == "set_plan_date":
            # "Today" is the draft owner's local day, not the server's.
            if op.plan_date is None or op.plan_date < datetime.now(draft_timezone).date():
                raise ValueError("Plan date cannot be in the past")
            for item in result.tasks:
                for field_name in ("deadline", "fixedStart", "fixedEnd"):
                    old_value = getattr(item, field_name)
                    if old_value is not None:
                        setattr(
                            item,
                            field_name,
                            old_value.replace(
                                year=op.plan_date.year,
                                month=op.plan_date.month,
                                day=op.plan_date.day,
                            ),
                        )
            result.planDate = op.plan_date
            continue
        if op.op == "remove_deferred_task":
            remaining = [item for item in result.deferred_tasks if item.task.id != op.task_id]
            if len(remaining) == len(result.deferred_tasks):
                raise ValueError("Task not found")
            result.deferred_tasks = remaining
            continue
        if op.op == "set_windows":
            result.windows = op.windows or []
            continue
        if op.op == "add_task":
            if op.task is None or any(item.id == op.task.id for item in result.tasks):
                raise ValueError("Task ID already exists")
            result.tasks.append(deepcopy(op.task))
            continue
        if op.op == "scale_durations":
            if op.task_id is not None and not any(
                item.id == op.task_id for item in result.tasks
            ):
                raise ValueError("Task not found")
            for item in result.tasks:
                if op.task_id is None or item.id == op.task_id:
                    item.durationMin = min(
                        480, max(5, round(item.durationMin * (op.factor or 1) / 5) * 5)
                    )
                    item.estimateSource = "USER"
            continue
        if op.op == "update_window":
            if op.window_index is None or op.window_index >= len(result.windows):
                raise ValueError("Window not found")
            old_start = result.windows[op.window_index].start
            old_end = result.windows[op.window_index].end
            new_start = op.start if op.start is not None else old_start
            new_end = op.end if op.end is not None else old_end
            if new_start >= new_end:
                raise ValueError("Invalid window")
            result.windows[op.window_index].start = new_start  # type: ignore[assignment]
            result.windows[op.window_index].end = new_end  # type: ignore[assignment]
            continue
        task = next((item for item in result.tasks if item.id == op.task_id), None)
        if task is None:
            raise ValueError("Task not found")
        if op.op == "remove_task" or op.op == "move_task_to_date":
            if any(
                task.id in item.dependencies
                for item in result.tasks
                if item.id != task.id
            ):
                raise ValueError("Cannot remove a task required by another task")
            result.tasks = [item for item in result.tasks if item.id != task.id]
            if op.op == "move_task_to_date":
                target_date = datetime.strptime(op.target_date, "%Y-%m-%d").date()
                from app.schemas.drafts import DeferredTaskDraft

                result.deferred_tasks.append(
                    DeferredTaskDraft(task=task, targetDate=target_date)
                )
        elif op.op == "split_task":
            first = op.split_minutes or 0
            if not 5 <= first <= task.durationMin - 5:
                raise ValueError("Split must leave at least five minutes per part")
            second_id = f"{task.id}-2"
            if any(item.id == second_id for item in result.tasks):
                raise ValueError("Split task ID already exists")
            remainder = deepcopy(task)
            remainder.id = second_id
            original_title = task.title
            task.title = f"{original_title} (part 1)"[:200]
            remainder.title = f"{original_title} (part 2)"[:200]
            remainder.durationMin = task.durationMin - first
            remainder.dependencies = [task.id]
            task.durationMin = first
            task.estimateSource = "USER"
            remainder.estimateSource = "USER"
            result.tasks.insert(result.tasks.index(task) + 1, remainder)
        else:
            if "duration_min" in op.model_dump(exclude_unset=True):
                task.durationMin = op.duration_min
                task.estimateSource = "USER"
            if "title" in op.model_dump(exclude_unset=True) and op.title is not None:
                task.title = op.title.strip()
            if "importance" in op.model_dump(exclude_unset=True):
                task.importance = op.importance
            if "priority" in op.model_dump(exclude_unset=True):
                task.priority = op.priority
            if "category" in op.model_dump(exclude_unset=True):
                task.category = op.category
            if "break_after_min" in op.model_dump(exclude_unset=True):
                task.breakAfterMin = op.break_after_min
            if "scheduling_type" in op.model_dump(exclude_unset=True):
                task.schedulingType = op.scheduling_type
            if "splittable" in op.model_dump(exclude_unset=True):
                task.splittable = bool(op.splittable)

            for attr, field in [
                ("fixedStart", "fixed_start"),
                ("fixedEnd", "fixed_end"),
                ("deadline", "deadline"),
            ]:
                if field in op.model_dump(exclude_unset=True):
                    val = getattr(op, field)
                    if val is None:
                        setattr(task, attr, None)
                    else:
                        parsed_time = datetime.strptime(val, "%H:%M").time()
                        setattr(
                            task,
                            attr,
                            datetime.combine(
                                result.planDate, parsed_time, draft_timezone
                            ),
                        )
    validated = TodayDraft.model_validate(result.model_dump())
    from app.ai.validators import check_today

    issues = check_today(validated)
    # A duration/importance edit may resolve one member of an already-ambiguous
    # duplicate-title set. Do not make that unrelated pre-existing condition
    # block the selected task patch; title-changing operations remain guarded.
    original_titles = [normalize(item.title) for item in draft.tasks]
    validated_titles = [normalize(item.title) for item in validated.tasks]
    if original_titles == validated_titles:
        issues = [issue for issue in issues if issue != "DUPLICATE_TITLE"]
    if issues:
        raise ValueError(", ".join(issues))
    return validated
