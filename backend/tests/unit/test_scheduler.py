import uuid
from datetime import datetime, timezone

import pytest
from app.core.scheduler import DeterministicScheduler, ScheduleTask, ScheduleWindow


def schedule_tasks(tasks, windows, satisfied):
    scheduler = DeterministicScheduler()
    return scheduler.schedule(tasks, windows, satisfied)


def _create_task(
    tid: str,
    duration: int,
    scheduling_type="FLEXIBLE",
    deps=None,
    is_splittable=False,
    min_split=None,
    priority="MEDIUM",
    fixed_start=None,
    fixed_end=None,
):
    return ScheduleTask(
        id=uuid.UUID(int=int(tid)),
        title=f"Task {tid}",
        estimated_duration_minutes=duration,
        priority=priority,
        scheduling_type=scheduling_type,
        created_at=datetime(2026, 1, 1, tzinfo=timezone.utc),
        is_splittable=is_splittable,
        min_split_duration_minutes=min_split,
        fixed_start_at=fixed_start,
        fixed_end_at=fixed_end,
        dependencies=deps or [],
    )


@pytest.mark.unit
def test_valid_flexible_scheduling():
    """Verify that valid flexible tasks are scheduled in priority/creation order within windows."""
    windows = [
        ScheduleWindow(
            start_at=datetime(2026, 1, 1, 9, 0, tzinfo=timezone.utc),
            end_at=datetime(2026, 1, 1, 11, 0, tzinfo=timezone.utc),
        )
    ]
    t1 = _create_task("1", 60, priority="HIGH")
    t2 = _create_task("2", 30, priority="LOW")

    res = schedule_tasks([t1, t2], windows, {})

    assert len(res.unscheduled_tasks) == 0
    task_blocks = [block for block in res.blocks if block.block_type == "TASK"]
    assert len(task_blocks) == 2
    assert task_blocks[0].task_id == uuid.UUID(int=1)
    assert task_blocks[0].start_at == datetime(2026, 1, 1, 9, 0, tzinfo=timezone.utc)
    assert task_blocks[0].end_at == datetime(2026, 1, 1, 10, 0, tzinfo=timezone.utc)
    assert task_blocks[1].task_id == uuid.UUID(int=2)
    assert task_blocks[1].start_at == datetime(2026, 1, 1, 10, 5, tzinfo=timezone.utc)
    assert task_blocks[1].end_at == datetime(2026, 1, 1, 10, 35, tzinfo=timezone.utc)
    assert len([block for block in res.blocks if block.block_type == "BUFFER"]) == 2
    assert res.workload_minutes == 90


@pytest.mark.unit
def test_deterministic_results():
    """Verify that identical inputs produce identically ordered blocks and outputs."""
    windows = [
        ScheduleWindow(
            start_at=datetime(2026, 1, 1, 9, 0, tzinfo=timezone.utc),
            end_at=datetime(2026, 1, 1, 11, 0, tzinfo=timezone.utc),
        )
    ]
    t1 = _create_task("1", 30, priority="MEDIUM")
    t2 = _create_task("2", 30, priority="MEDIUM")

    res1 = schedule_tasks([t1, t2], windows, {})
    res2 = schedule_tasks([t2, t1], windows, {})

    assert res1.blocks == res2.blocks
    assert res1.unscheduled_tasks == res2.unscheduled_tasks


@pytest.mark.unit
def test_direct_cycles():
    """Verify that two tasks depending on each other are marked unscheduled for CYCLIC_DEPENDENCY."""
    t1 = _create_task("1", 30, deps=[uuid.UUID(int=2)])
    t2 = _create_task("2", 30, deps=[uuid.UUID(int=1)])
    windows = [
        ScheduleWindow(
            datetime(2026, 1, 1, 9, 0, tzinfo=timezone.utc),
            datetime(2026, 1, 1, 11, 0, tzinfo=timezone.utc),
        )
    ]

    res = schedule_tasks([t1, t2], windows, {})
    assert len(res.unscheduled_tasks) == 2
    assert len(res.reasons) == 2
    assert {
        "code": "CYCLIC_DEPENDENCY",
        "task_id": uuid.UUID(int=1),
        "dependency_id": uuid.UUID(int=2),
    } in res.reasons
    assert {
        "code": "CYCLIC_DEPENDENCY",
        "task_id": uuid.UUID(int=2),
        "dependency_id": uuid.UUID(int=1),
    } in res.reasons


@pytest.mark.unit
def test_multi_task_cycles():
    """Verify that a cycle involving multiple tasks is correctly identified."""
    t1 = _create_task("1", 30, deps=[uuid.UUID(int=2)])
    t2 = _create_task("2", 30, deps=[uuid.UUID(int=3)])
    t3 = _create_task("3", 30, deps=[uuid.UUID(int=1)])
    windows = [
        ScheduleWindow(
            datetime(2026, 1, 1, 9, 0, tzinfo=timezone.utc),
            datetime(2026, 1, 1, 11, 0, tzinfo=timezone.utc),
        )
    ]

    res = schedule_tasks([t1, t2, t3], windows, {})
    assert len(res.unscheduled_tasks) == 3
    assert {
        "code": "CYCLIC_DEPENDENCY",
        "task_id": uuid.UUID(int=1),
        "dependency_id": uuid.UUID(int=2),
    } in res.reasons
    assert {
        "code": "CYCLIC_DEPENDENCY",
        "task_id": uuid.UUID(int=2),
        "dependency_id": uuid.UUID(int=3),
    } in res.reasons
    assert {
        "code": "CYCLIC_DEPENDENCY",
        "task_id": uuid.UUID(int=3),
        "dependency_id": uuid.UUID(int=1),
    } in res.reasons


@pytest.mark.unit
def test_missing_dependencies():
    """Verify that tasks with unfulfilled dependencies are unscheduled."""
    t1 = _create_task("1", 30, deps=[uuid.UUID(int=2)])
    windows = [
        ScheduleWindow(
            datetime(2026, 1, 1, 9, 0, tzinfo=timezone.utc),
            datetime(2026, 1, 1, 11, 0, tzinfo=timezone.utc),
        )
    ]

    res = schedule_tasks([t1], windows, {})
    assert len(res.unscheduled_tasks) == 1
    assert res.reasons[0] == {
        "code": "MISSING_DEPENDENCY",
        "task_id": uuid.UUID(int=1),
        "dependency_id": uuid.UUID(int=2),
    }


@pytest.mark.unit
def test_cascading_dependency_failures():
    """Verify that descendants of failed tasks are also failed recursively."""
    t1 = _create_task("1", 30, deps=[uuid.UUID(int=2)])
    t2 = _create_task("2", 30, deps=[uuid.UUID(int=3)])  # missing t3

    windows = [
        ScheduleWindow(
            datetime(2026, 1, 1, 9, 0, tzinfo=timezone.utc),
            datetime(2026, 1, 1, 11, 0, tzinfo=timezone.utc),
        )
    ]

    res = schedule_tasks([t1, t2], windows, {})
    assert len(res.unscheduled_tasks) == 2
    assert {
        "code": "MISSING_DEPENDENCY",
        "task_id": uuid.UUID(int=2),
        "dependency_id": uuid.UUID(int=3),
    } in res.reasons
    assert {
        "code": "DEPENDENCY_UNSCHEDULED",
        "task_id": uuid.UUID(int=1),
        "dependency_id": uuid.UUID(int=2),
    } in res.reasons


@pytest.mark.unit
def test_invalid_fixed_intervals():
    """Verify that fixed tasks with inverted start/end times are rejected."""
    t1 = _create_task(
        "1",
        30,
        scheduling_type="FIXED",
        fixed_start=datetime(2026, 1, 1, 10, 0, tzinfo=timezone.utc),
        fixed_end=datetime(2026, 1, 1, 9, 0, tzinfo=timezone.utc),
    )

    windows = [
        ScheduleWindow(
            datetime(2026, 1, 1, 8, 0, tzinfo=timezone.utc),
            datetime(2026, 1, 1, 11, 0, tzinfo=timezone.utc),
        )
    ]

    res = schedule_tasks([t1], windows, {})
    assert len(res.unscheduled_tasks) == 1
    assert res.reasons[0] == {
        "code": "INVALID_FIXED_INTERVAL",
        "task_id": uuid.UUID(int=1),
    }


@pytest.mark.unit
def test_fixed_task_overlaps():
    """Verify that overlapping fixed tasks trigger overlap failures for both tasks."""
    t1 = _create_task(
        "1",
        60,
        scheduling_type="FIXED",
        fixed_start=datetime(2026, 1, 1, 9, 0, tzinfo=timezone.utc),
        fixed_end=datetime(2026, 1, 1, 10, 0, tzinfo=timezone.utc),
    )
    t2 = _create_task(
        "2",
        60,
        scheduling_type="FIXED",
        fixed_start=datetime(2026, 1, 1, 9, 30, tzinfo=timezone.utc),
        fixed_end=datetime(2026, 1, 1, 10, 30, tzinfo=timezone.utc),
    )

    windows = [
        ScheduleWindow(
            datetime(2026, 1, 1, 8, 0, tzinfo=timezone.utc),
            datetime(2026, 1, 1, 11, 0, tzinfo=timezone.utc),
        )
    ]

    res = schedule_tasks([t1, t2], windows, {})
    assert len(res.unscheduled_tasks) == 2
    assert {
        "code": "FIXED_TASK_OVERLAP",
        "task_id": uuid.UUID(int=1),
        "dependency_id": uuid.UUID(int=2),
    } in res.reasons
    assert {
        "code": "FIXED_TASK_OVERLAP",
        "task_id": uuid.UUID(int=2),
        "dependency_id": uuid.UUID(int=1),
    } in res.reasons


@pytest.mark.unit
def test_fixed_tasks_outside_availability():
    """Verify that fixed tasks placed outside any availability window are rejected."""
    t1 = _create_task(
        "1",
        60,
        scheduling_type="FIXED",
        fixed_start=datetime(2026, 1, 1, 12, 0, tzinfo=timezone.utc),
        fixed_end=datetime(2026, 1, 1, 13, 0, tzinfo=timezone.utc),
    )

    windows = [
        ScheduleWindow(
            datetime(2026, 1, 1, 8, 0, tzinfo=timezone.utc),
            datetime(2026, 1, 1, 11, 0, tzinfo=timezone.utc),
        )
    ]

    res = schedule_tasks([t1], windows, {})
    assert len(res.unscheduled_tasks) == 1
    assert res.reasons[0] == {
        "code": "FIXED_TASK_OUTSIDE_BOUNDS",
        "task_id": uuid.UUID(int=1),
    }


@pytest.mark.unit
def test_prerequisite_scheduling_order():
    """Verify that prerequisites are fully scheduled before their dependents."""
    t1 = _create_task("1", 30, deps=[uuid.UUID(int=2)])
    t2 = _create_task("2", 30)

    windows = [
        ScheduleWindow(
            datetime(2026, 1, 1, 9, 0, tzinfo=timezone.utc),
            datetime(2026, 1, 1, 11, 0, tzinfo=timezone.utc),
        )
    ]

    res = schedule_tasks([t1, t2], windows, {})
    task_blocks = [block for block in res.blocks if block.block_type == "TASK"]
    assert len(task_blocks) == 2
    assert task_blocks[0].task_id == uuid.UUID(int=2)
    assert task_blocks[1].task_id == uuid.UUID(int=1)
    assert task_blocks[0].end_at <= task_blocks[1].start_at


@pytest.mark.unit
def test_satisfied_external_dependencies():
    """Verify that externally satisfied dependencies allow the task to be scheduled."""
    t1 = _create_task("1", 30, deps=[uuid.UUID(int=99)])

    satisfied = {uuid.UUID(int=99): datetime(2026, 1, 1, 8, 0, tzinfo=timezone.utc)}
    windows = [
        ScheduleWindow(
            datetime(2026, 1, 1, 9, 0, tzinfo=timezone.utc),
            datetime(2026, 1, 1, 11, 0, tzinfo=timezone.utc),
        )
    ]

    res = schedule_tasks([t1], windows, satisfied)
    assert len(res.unscheduled_tasks) == 0


@pytest.mark.unit
def test_splitting_splittable_tasks():
    """Verify that splittable tasks span across distinct availability windows."""
    t1 = _create_task("1", 90, is_splittable=True, min_split=30)

    windows = [
        ScheduleWindow(
            datetime(2026, 1, 1, 9, 0, tzinfo=timezone.utc),
            datetime(2026, 1, 1, 10, 0, tzinfo=timezone.utc),
        ),
        ScheduleWindow(
            datetime(2026, 1, 1, 11, 0, tzinfo=timezone.utc),
            datetime(2026, 1, 1, 11, 30, tzinfo=timezone.utc),
        ),
    ]

    res = schedule_tasks([t1], windows, {})
    assert len(res.unscheduled_tasks) == 0
    assert len(res.blocks) == 2
    assert res.workload_minutes == 90
    assert res.blocks[0].start_at == datetime(2026, 1, 1, 9, 0, tzinfo=timezone.utc)
    assert res.blocks[1].start_at == datetime(2026, 1, 1, 11, 0, tzinfo=timezone.utc)


@pytest.mark.unit
def test_minimum_split_duration():
    """Verify that splittable tasks respect the minimum split duration constraint."""
    t1 = _create_task("1", 90, is_splittable=True, min_split=60)

    windows = [
        ScheduleWindow(
            datetime(2026, 1, 1, 9, 0, tzinfo=timezone.utc),
            datetime(2026, 1, 1, 9, 30, tzinfo=timezone.utc),
        ),
        ScheduleWindow(
            datetime(2026, 1, 1, 10, 0, tzinfo=timezone.utc),
            datetime(2026, 1, 1, 11, 30, tzinfo=timezone.utc),
        ),
    ]

    res = schedule_tasks([t1], windows, {})
    assert len(res.unscheduled_tasks) == 0
    assert len(res.blocks) == 1
    assert res.blocks[0].start_at == datetime(2026, 1, 1, 10, 0, tzinfo=timezone.utc)
    assert res.blocks[0].end_at == datetime(2026, 1, 1, 11, 30, tzinfo=timezone.utc)


@pytest.mark.unit
def test_non_splittable_tasks():
    """Verify that non-splittable tasks are rejected if no single window can fit them entirely."""
    t1 = _create_task("1", 90, is_splittable=False)

    windows = [
        ScheduleWindow(
            datetime(2026, 1, 1, 9, 0, tzinfo=timezone.utc),
            datetime(2026, 1, 1, 10, 0, tzinfo=timezone.utc),
        ),
        ScheduleWindow(
            datetime(2026, 1, 1, 11, 0, tzinfo=timezone.utc),
            datetime(2026, 1, 1, 11, 30, tzinfo=timezone.utc),
        ),
    ]

    res = schedule_tasks([t1], windows, {})
    assert len(res.unscheduled_tasks) == 1
    assert res.reasons[0] == {"code": "INSUFFICIENT_TIME", "task_id": uuid.UUID(int=1)}


@pytest.mark.unit
def test_fixed_dependent_cutoff_behavior():
    """Verify that a prerequisite must finish before a dependent fixed task's start time."""
    t1 = _create_task("1", 60)
    t2 = _create_task(
        "2",
        30,
        scheduling_type="FIXED",
        fixed_start=datetime(2026, 1, 1, 9, 30, tzinfo=timezone.utc),
        fixed_end=datetime(2026, 1, 1, 10, 0, tzinfo=timezone.utc),
        deps=[uuid.UUID(int=1)],
    )

    windows = [
        ScheduleWindow(
            datetime(2026, 1, 1, 9, 0, tzinfo=timezone.utc),
            datetime(2026, 1, 1, 11, 0, tzinfo=timezone.utc),
        )
    ]

    res = schedule_tasks([t1, t2], windows, {})
    assert len(res.unscheduled_tasks) == 2
    assert {
        "code": "INSUFFICIENT_TIME_BEFORE_DEPENDENT",
        "task_id": uuid.UUID(int=1),
        "dependency_id": uuid.UUID(int=2),
    } in res.reasons


@pytest.mark.unit
def test_empty_invalid_windows():
    """Verify that empty or backward windows yield zero availability."""
    t1 = _create_task("1", 30)
    invalid_window = ScheduleWindow(
        start_at=datetime(2026, 1, 1, 10, 0, tzinfo=timezone.utc),
        end_at=datetime(2026, 1, 1, 9, 0, tzinfo=timezone.utc),
    )
    res = schedule_tasks([t1], [invalid_window], {})
    assert len(res.unscheduled_tasks) == 1
    assert res.reasons[0] == {
        "code": "NO_AVAILABILITY_WINDOWS",
        "task_id": uuid.UUID(int=1),
    }


@pytest.mark.unit
def test_stable_reason_codes():
    """Verify that each task fails exactly once with a single reason, even with multiple failure paths."""
    t1 = _create_task("1", 30, deps=[uuid.UUID(int=99)])
    t2 = _create_task("2", 30, deps=[uuid.UUID(int=99)])

    windows = [
        ScheduleWindow(
            datetime(2026, 1, 1, 9, 0, tzinfo=timezone.utc),
            datetime(2026, 1, 1, 11, 0, tzinfo=timezone.utc),
        )
    ]

    res = schedule_tasks([t1, t2], windows, {})
    assert len(res.unscheduled_tasks) == 2

    task_ids_in_reasons = [r["task_id"] for r in res.reasons]
    # Verify no duplicate reasons per task
    assert len(task_ids_in_reasons) == len(set(task_ids_in_reasons))
    assert {
        "code": "MISSING_DEPENDENCY",
        "task_id": uuid.UUID(int=1),
        "dependency_id": uuid.UUID(int=99),
    } in res.reasons
    assert {
        "code": "MISSING_DEPENDENCY",
        "task_id": uuid.UUID(int=2),
        "dependency_id": uuid.UUID(int=99),
    } in res.reasons
