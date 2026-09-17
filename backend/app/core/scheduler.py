from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
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
    def schedule(self, tasks: List[ScheduleTask], windows: List[ScheduleWindow]) -> ScheduleResult:
        blocks: List[ScheduleBlock] = []
        unscheduled_tasks: List[UUID] = []
        reasons: List[Dict[str, Any]] = []

        if not windows:
            reasons.append({"code": "NO_AVAILABILITY_WINDOWS"})
            return ScheduleResult([], [t.id for t in tasks], reasons, 0, 0)

        # 1. Normalize windows (merge overlapping)
        windows = sorted(windows, key=lambda w: w.start_at)
        merged_windows = []
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

        # Validate missing dependencies
        task_ids_set = {t.id for t in tasks}
        for t in tasks:
            for dep in t.dependencies:
                if dep not in task_ids_set:
                    reasons.append({"code": "MISSING_DEPENDENCY", "task_id": t.id, "dependency_id": dep})
                    unscheduled_tasks.append(t.id)

        # 3. Detect Cycles across ALL tasks
        graph = defaultdict(list)
        for t in tasks:
            if t.id not in unscheduled_tasks:
                for dep in t.dependencies:
                    if dep not in unscheduled_tasks:
                        graph[dep].append(t.id)

        def has_cycle(node, visited, rec_stack, path):
            visited.add(node)
            rec_stack.add(node)
            path.append(node)
            for neighbor in graph[node]:
                if neighbor not in visited:
                    if has_cycle(neighbor, visited, rec_stack, path):
                        return True
                elif neighbor in rec_stack:
                    return True
            rec_stack.remove(node)
            path.pop()
            return False

        visited = set()
        rec_stack = set()
        for t in tasks:
            if t.id not in visited and t.id not in unscheduled_tasks:
                path = []
                if has_cycle(t.id, visited, rec_stack, path):
                    for ct in path:
                        if ct not in unscheduled_tasks:
                            unscheduled_tasks.append(ct)
                            reasons.append({"code": "CYCLIC_DEPENDENCY", "task_id": ct})

        # Separate FIXED and FLEXIBLE tasks
        valid_tasks = [t for t in tasks if t.id not in unscheduled_tasks]
        fixed_tasks = [t for t in valid_tasks if t.scheduling_type == 'FIXED']
        flexible_tasks = [t for t in valid_tasks if t.scheduling_type == 'FLEXIBLE']

        # 4. Place FIXED tasks
        for ft in fixed_tasks:
            if not ft.fixed_start_at or not ft.fixed_end_at:
                continue

            # Out of bounds check
            in_window = any(w.start_at <= ft.fixed_start_at and ft.fixed_end_at <= w.end_at for w in windows)
            if not in_window:
                reasons.append({"code": "FIXED_TASK_OUTSIDE_BOUNDS", "task_id": ft.id})
                unscheduled_tasks.append(ft.id)
                continue

            blocks.append(ScheduleBlock(
                block_type="FIXED_EVENT",
                start_at=ft.fixed_start_at,
                end_at=ft.fixed_end_at,
                task_id=ft.id,
                title=ft.title
            ))

        # Check overlaps in fixed tasks
        blocks.sort(key=lambda b: b.start_at)
        for i, ft1 in enumerate(blocks):
            for ft2 in blocks[:i]:
                if max(ft1.start_at, ft2.start_at) < min(ft1.end_at, ft2.end_at):
                    if ft1.task_id and {"code": "FIXED_TASK_OVERLAP", "task_id": ft1.task_id} not in reasons:
                        reasons.append({"code": "FIXED_TASK_OVERLAP", "task_id": ft1.task_id})
                    if ft2.task_id and {"code": "FIXED_TASK_OVERLAP", "task_id": ft2.task_id} not in reasons:
                        reasons.append({"code": "FIXED_TASK_OVERLAP", "task_id": ft2.task_id})

        # 5. Topologically sort valid flexible tasks
        in_degree = defaultdict(int)
        task_map = {t.id: t for t in valid_tasks}

        # Build dependency graph considering all valid tasks (fixed + flexible)
        flex_graph = defaultdict(list)
        for t in valid_tasks:
            if t.id in unscheduled_tasks:
                continue
            for dep in t.dependencies:
                if dep in task_map:
                    flex_graph[dep].append(t.id)
                    in_degree[t.id] += 1

        ordered_flexible = []
        available_all = [t.id for t in valid_tasks if in_degree[t.id] == 0 and t.id not in unscheduled_tasks]

        while available_all:
            available_all.sort(key=lambda tid: (
                priority_map.get(task_map[tid].priority, 99),
                task_map[tid].created_at,
                str(tid)
            ))
            curr_id = available_all.pop(0)

            if task_map[curr_id].scheduling_type == 'FLEXIBLE':
                ordered_flexible.append(curr_id)

            for child_id in flex_graph[curr_id]:
                in_degree[child_id] -= 1
                if in_degree[child_id] == 0:
                    available_all.append(child_id)

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

        task_end_times = {b.task_id: b.end_at for b in blocks if b.task_id}

        for tid in ordered_flexible:
            task = task_map[tid]

            dep_end_times = [task_end_times.get(d) for d in task.dependencies if task_end_times.get(d)]
            earliest_start = max(dep_end_times) if dep_end_times else windows[0].start_at

            remaining_duration = timedelta(minutes=task.estimated_duration_minutes)
            min_split = timedelta(minutes=task.min_split_duration_minutes or task.estimated_duration_minutes)
            if not task.is_splittable:
                min_split = remaining_duration

            task_blocks = []

            while remaining_duration.total_seconds() > 0:
                gaps = find_gaps(earliest_start)

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

                if remaining_duration.total_seconds() == 0 and task.preferred_break_duration_minutes:
                    break_duration = timedelta(minutes=task.preferred_break_duration_minutes)
                    break_gaps = find_gaps(earliest_start)
                    if break_gaps and (break_gaps[0][1] - break_gaps[0][0]) >= break_duration:
                        bg_start = break_gaps[0][0]
                        blocks.append(ScheduleBlock(
                            block_type="BREAK",
                            start_at=bg_start,
                            end_at=bg_start + break_duration,
                            task_id=None,
                            title="Break"
                        ))

            if remaining_duration.total_seconds() > 0:
                for b in task_blocks:
                    blocks.remove(b)
                unscheduled_tasks.append(task.id)
                reasons.append({"code": "INSUFFICIENT_TIME", "task_id": task.id})
            else:
                task_end_times[task.id] = task_blocks[-1].end_at

        blocks.sort(key=lambda b: b.start_at)

        workload_minutes = int(sum((b.end_at - b.start_at).total_seconds() for b in blocks if b.block_type == "TASK") // 60)

        return ScheduleResult(
            blocks=blocks,
            unscheduled_tasks=unscheduled_tasks,
            reasons=reasons,
            workload_minutes=workload_minutes,
            available_minutes=available_minutes
        )
