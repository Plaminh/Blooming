from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Tuple
from uuid import UUID

@dataclass
class ScheduleTask:
    id: UUID
    title: str
    estimated_duration_minutes: int
    priority: str  # "URGENT", "HIGH", "MEDIUM", "LOW"
    scheduling_type: str  # "FLEXIBLE", "FIXED"
    created_at: datetime
    is_splittable: bool = False
    min_split_duration_minutes: Optional[int] = None
    preferred_break_duration_minutes: Optional[int] = None
    fixed_start_at: Optional[datetime] = None
    fixed_end_at: Optional[datetime] = None
    dependencies: List[UUID] = field(default_factory=list)

@dataclass
class ScheduleWindow:
    start_at: datetime
    end_at: datetime

@dataclass
class ScheduleBlock:
    block_type: str  # "TASK", "BREAK", "FIXED_EVENT"
    start_at: datetime
    end_at: datetime
    task_id: Optional[UUID] = None
    title: Optional[str] = None

@dataclass
class ScheduleResult:
    blocks: List[ScheduleBlock]
    unscheduled_tasks: List[UUID]
    reasons: List[Dict[str, Any]]
    workload_minutes: int
    available_minutes: int

class DeterministicScheduler:
    def schedule(self, tasks: List[ScheduleTask], windows: List[ScheduleWindow], satisfied_dependencies: Optional[Dict[UUID, datetime]] = None) -> ScheduleResult:
        blocks: List[ScheduleBlock] = []
        unscheduled_tasks: List[UUID] = []
        reasons: List[Dict[str, Any]] = []

        satisfied_dependencies = satisfied_dependencies or {}
        # Canonical ordering and one result/reason per failed task.
        task_map = {}
        failed = {}

        def fail(task_id, code, dependency_id=None):
            if task_id not in failed:
                reason = {"code": code, "task_id": task_id}
                if dependency_id is not None:
                    reason["dependency_id"] = dependency_id
                failed[task_id] = reason

        for task in tasks:
            if task.id in task_map:
                fail(task.id, "DUPLICATE_TASK_ID")
            task_map[task.id] = task
        tasks = sorted(task_map.values(), key=lambda t: str(t.id))
        graph = defaultdict(list)
        for task in tasks:
            for dep in sorted(set(task.dependencies), key=str):
                graph[dep].append(task.id)
                if dep not in task_map and dep not in satisfied_dependencies:
                    fail(task.id, "MISSING_DEPENDENCY", dep)
            if task.estimated_duration_minutes <= 0:
                fail(task.id, "INVALID_DURATION")
            if task.scheduling_type not in ("FIXED", "FLEXIBLE"):
                fail(task.id, "INVALID_SCHEDULING_TYPE")

        # Detect actual cycle members, then propagate failure to their descendants.
        visited: set[UUID] = set()
        path: list[UUID] = []
        def visit(task_id):
            if task_id in path:
                cycle = path[path.index(task_id):]
                for member in cycle:
                    dep = next(d for d in sorted(set(task_map[member].dependencies), key=str) if d in cycle)
                    fail(member, "CYCLIC_DEPENDENCY", dep)
                return
            if task_id in visited:
                return
            path.append(task_id)
            for dep in sorted(set(task_map[task_id].dependencies), key=str):
                if dep in task_map:
                    visit(dep)
            path.pop()
            visited.add(task_id)
        for task in tasks:
            visit(task.id)

        def cascade():
            queue = sorted(failed, key=str)
            seen = set(queue)
            while queue:
                parent = queue.pop(0)
                for child in graph[parent]:
                    fail(child, "DEPENDENCY_UNSCHEDULED", parent)
                    if child not in seen:
                        seen.add(child)
                        queue.append(child)
            blocks[:] = [b for b in blocks if b.task_id not in failed]

        cascade()
        windows = [w for w in windows if w.end_at > w.start_at]
        if not windows:
            for task in tasks:
                fail(task.id, "NO_AVAILABILITY_WINDOWS")
                cascade()
            ids = sorted(failed, key=str)
            return ScheduleResult([], ids, [failed[t] for t in ids], 0, 0)

        # 1. Normalize windows (merge overlapping)
        windows = sorted(windows, key=lambda w: w.start_at)
        merged_windows: list[ScheduleWindow] = []
        for w in windows:
            if not merged_windows:
                merged_windows.append(ScheduleWindow(w.start_at, w.end_at))
            else:
                last = merged_windows[-1]
                if w.start_at <= last.end_at:
                    last.end_at = max(last.end_at, w.end_at)
                else:
                    merged_windows.append(ScheduleWindow(w.start_at, w.end_at))
        windows = merged_windows

        available_minutes = int(sum((w.end_at - w.start_at).total_seconds() for w in windows) // 60)

        # 2. Setup Priority map for determinism
        priority_map = {"URGENT": 0, "HIGH": 1, "MEDIUM": 2, "LOW": 3}

        # Reserve fixed intervals before placing flexible prerequisites into gaps.
        fixed_tasks = [t for t in tasks if t.scheduling_type == "FIXED" and t.id not in failed]
        for task in fixed_tasks:
            if not task.fixed_start_at or not task.fixed_end_at or task.fixed_end_at <= task.fixed_start_at:
                fail(task.id, "INVALID_FIXED_INTERVAL")
            elif not any(w.start_at <= task.fixed_start_at and task.fixed_end_at <= w.end_at for w in windows):
                fail(task.id, "FIXED_TASK_OUTSIDE_BOUNDS")
            else:
                blocks.append(ScheduleBlock("FIXED_EVENT", task.fixed_start_at, task.fixed_end_at, task.id, task.title))
        blocks.sort(key=lambda b: (b.start_at, str(b.task_id)))
        for i, first in enumerate(blocks):
            for second in blocks[:i]:
                if max(first.start_at, second.start_at) < min(first.end_at, second.end_at):
                    fail(first.task_id, "FIXED_TASK_OVERLAP", second.task_id)
                    fail(second.task_id, "FIXED_TASK_OVERLAP", first.task_id)
        cascade()

        valid_tasks = [t for t in tasks if t.id not in failed]
        in_degree = {t.id: len(set(t.dependencies) - satisfied_dependencies.keys()) for t in valid_tasks}
        available_all = [tid for tid, degree in in_degree.items() if degree == 0]
        ordered_tasks = []
        while available_all:
            available_all.sort(key=lambda tid: (priority_map.get(task_map[tid].priority, 99), task_map[tid].created_at, str(tid)))
            curr_id = available_all.pop(0)
            ordered_tasks.append(curr_id)
            for child in graph[curr_id]:
                if child in in_degree:
                    in_degree[child] -= 1
                    if in_degree[child] == 0:
                        available_all.append(child)

        # Fixed descendants impose a real deadline, not a blanket FIXED/FLEXIBLE ban.
        deadlines: dict[UUID, tuple[datetime, UUID]] = {}
        for tid in reversed(ordered_tasks):
            task = task_map[tid]
            bounds = [deadlines[child] for child in graph[tid] if child in deadlines]
            if task.scheduling_type == "FIXED" and task.fixed_start_at is not None:
                bounds.append((task.fixed_start_at, tid))
            if bounds:
                deadlines[tid] = min(bounds, key=lambda bound: (bound[0], str(bound[1])))

        # 6. Place FLEXIBLE tasks in gaps
        def find_gaps(start_after: datetime) -> List[Tuple[datetime, datetime]]:
            gaps = []
            for w in windows:
                if w.end_at <= start_after:
                    continue
                curr = max(w.start_at, start_after)

                window_blocks = [b for b in blocks if max(b.start_at, curr) < min(b.end_at, w.end_at)]
                window_blocks.sort(key=lambda b: b.start_at)

                for b in window_blocks:
                    if b.start_at > curr:
                        gaps.append((curr, b.start_at))
                    curr = max(curr, b.end_at)

                if w.end_at > curr:
                    gaps.append((curr, w.end_at))
            return gaps

        task_end_times = {**satisfied_dependencies, **{b.task_id: b.end_at for b in blocks if b.task_id}}

        for tid in ordered_tasks:
            task = task_map[tid]
            if tid in failed:
                continue
            if task.scheduling_type == "FIXED":
                if task.fixed_start_at is None:
                    fail(tid, "INVALID_FIXED_INTERVAL")
                    cascade()
                    continue
                for dep in sorted(set(task.dependencies), key=str):
                    if dep not in task_end_times or task_end_times[dep] > task.fixed_start_at:
                        fail(tid, "DEPENDENCY_TIME_CONFLICT", dep)
                        cascade()
                        break
                continue

            dep_end_times = [task_end_times[d] for d in task.dependencies if d in task_end_times]
            earliest_start = max(dep_end_times) if dep_end_times else windows[0].start_at

            remaining_duration = timedelta(minutes=task.estimated_duration_minutes)
            min_split = timedelta(minutes=task.min_split_duration_minutes if task.min_split_duration_minutes else (15 if task.is_splittable else task.estimated_duration_minutes))
            if not task.is_splittable:
                min_split = remaining_duration

            task_blocks = []

            while remaining_duration.total_seconds() > 0:
                gaps = find_gaps(earliest_start)

                if tid in deadlines:
                    deadline, _ = deadlines[tid]
                    gaps = [(start, min(end, deadline)) for start, end in gaps if start < deadline]
                valid_gaps = [g for g in gaps if (g[1] - g[0]) >= min_split or (g[1] - g[0]) >= remaining_duration]

                if not valid_gaps:
                    break

                gap_start, gap_end = valid_gaps[0]
                gap_duration = gap_end - gap_start

                duration_to_use = min(gap_duration, remaining_duration)

                task_blocks.append(ScheduleBlock(
                    block_type="TASK",
                    start_at=gap_start,
                    end_at=gap_start + duration_to_use,
                    task_id=task.id,
                    title=task.title
                ))

                remaining_duration -= duration_to_use
                earliest_start = gap_start + duration_to_use
                blocks.append(task_blocks[-1])

                if remaining_duration.total_seconds() == 0:
                    if task.preferred_break_duration_minutes:
                        break_duration = timedelta(minutes=task.preferred_break_duration_minutes)
                        block_type = "BREAK"
                        title = "Break"
                    else:
                        break_duration = timedelta(minutes=5)
                        block_type = "BUFFER"
                        title = "Buffer"
                    break_gaps = find_gaps(earliest_start)
                    if break_gaps and (break_gaps[0][1] - break_gaps[0][0]) >= break_duration:
                        bg_start = break_gaps[0][0]
                        blocks.append(ScheduleBlock(
                            block_type=block_type,
                            start_at=bg_start,
                            end_at=bg_start + break_duration,
                            task_id=None,
                            title=title
                        ))

            if remaining_duration.total_seconds() > 0:
                for b in task_blocks:
                    blocks.remove(b)
                if tid in deadlines:
                    fail(tid, "INSUFFICIENT_TIME_BEFORE_DEPENDENT", deadlines[tid][1])
                else:
                    fail(tid, "INSUFFICIENT_TIME")
                cascade()
            else:
                task_end_times[task.id] = task_blocks[-1].end_at

        blocks.sort(key=lambda b: (b.start_at, str(b.task_id)))
        unscheduled_tasks = sorted(failed, key=str)
        reasons = [failed[tid] for tid in unscheduled_tasks]

        workload_minutes = int(sum((b.end_at - b.start_at).total_seconds() for b in blocks if b.block_type == "TASK") // 60)

        return ScheduleResult(
            blocks=blocks,
            unscheduled_tasks=unscheduled_tasks,
            reasons=reasons,
            workload_minutes=workload_minutes,
            available_minutes=available_minutes
        )
