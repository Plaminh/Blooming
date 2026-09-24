from datetime import datetime, timezone
from uuid import uuid4

from app.core.scheduler import DeterministicScheduler, ScheduleTask, ScheduleWindow


def test_scheduler_pure_logic():
    scheduler = DeterministicScheduler()
    windows = [ScheduleWindow(
        start_at=datetime(2026, 9, 19, 9, 0, tzinfo=timezone.utc),
        end_at=datetime(2026, 9, 19, 17, 0, tzinfo=timezone.utc)
    )]
    task1 = ScheduleTask(
        id=uuid4(),
        title="Test Task",
        estimated_duration_minutes=60,
        priority="HIGH",
        scheduling_type="FLEXIBLE",
        created_at=datetime.now(timezone.utc)
    )
    result = scheduler.schedule([task1], windows)
    task_blocks = [block for block in result.blocks if block.block_type == "TASK"]
    assert len(task_blocks) == 1
    assert task_blocks[0].title == "Test Task"
    assert any(block.block_type == "BUFFER" for block in result.blocks)
    assert not result.unscheduled_tasks
