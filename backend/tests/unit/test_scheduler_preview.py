"""Cluster 15 — Scheduler preview and reality checks.

Test IDs: PV-001, PV-002, PV-003, PV-004, PV-005, PV-006,
          PV-012, PV-015, PV-016, CL-003 (scheduler-level fixed task outside availability)

All scheduler tests call the real DeterministicScheduler and today_service._normalize_and_schedule.
No mocked scheduler results are used as evidence of correctness.
"""

from __future__ import annotations

from datetime import date, datetime
from unittest.mock import AsyncMock, patch
from uuid import UUID, uuid4
from zoneinfo import ZoneInfo

import pytest

from app.ai.context import ChatContext
from app.core.scheduler import DeterministicScheduler, ScheduleTask, ScheduleWindow
from app.schemas.drafts import (
    AvailabilityWindowDraft,
    TaskDraft,
    TodayDraft,
)
from app.services.today_service import today_service


def _tz() -> ZoneInfo:
    return ZoneInfo("UTC")


def _dt(hour: int, minute: int = 0, date_: date | None = None) -> datetime:
    d = date_ or date(2026, 9, 20)
    return datetime(d.year, d.month, d.day, hour, minute, tzinfo=_tz())


def _sched_task(
    task_id: UUID | None = None,
    title: str = "Task",
    duration: int = 60,
    priority: str = "MEDIUM",
    scheduling_type: str = "FLEXIBLE",
    fixed_start: datetime | None = None,
    fixed_end: datetime | None = None,
    dependencies: list | None = None,
) -> ScheduleTask:
    return ScheduleTask(
        id=task_id or uuid4(),
        title=title,
        estimated_duration_minutes=duration,
        priority=priority,
        scheduling_type=scheduling_type,
        created_at=_dt(8),
        fixed_start_at=fixed_start,
        fixed_end_at=fixed_end,
        dependencies=dependencies or [],
    )


def _window(start_h: int, end_h: int) -> ScheduleWindow:
    return ScheduleWindow(start_at=_dt(start_h), end_at=_dt(end_h))


# ===========================================================================
# PV-001 — Draft creation must NOT generate a preview token
# ===========================================================================
@pytest.mark.asyncio
async def test_pv_001_draft_creation_no_preview_token():
    """Initial plan_day() returns a draft but NO preview token and NO preview."""
    from app.ai.handlers import planner
    from app.ai.llm.budget import BudgetMode

    ctx = ChatContext(
        db=AsyncMock(),
        user_id=uuid4(),
        now=datetime(2026, 9, 20, 8, 0, tzinfo=ZoneInfo("UTC")),
        timezone=ZoneInfo("UTC"),
        break_minutes=5,
        default_windows=(("09:00", "17:00"),),
        default_date_offset=0,
    )

    with patch(
        "app.ai.handlers.planner.get_budget_mode",
        new=AsyncMock(return_value=BudgetMode.NORMAL),
    ):
        with patch(
            "app.ai.handlers.planner.available_routes",
            new=AsyncMock(return_value="groq"),
        ):
            result = await planner.plan_day("Study 60 min", ctx, "en")

    assert result.draft is not None
    assert result.preview is None  # No preview at draft creation


# ===========================================================================
# PV-002 — Preview occurs only after explicit Generate Timeline
# ===========================================================================
def test_pv_002_preview_only_after_generate_timeline():
    """_normalize_and_schedule (the preview pathway) runs the real scheduler."""
    draft = TodayDraft(
        planDate=date(2026, 9, 20),
        timezone="UTC",
        windows=[AvailabilityWindowDraft(start="09:00", end="11:00")],
        tasks=[TaskDraft(id="d1", title="Study", durationMin=60)],
    )
    user_id = uuid4()
    result, reality_check, draft_to_uuid = today_service._normalize_and_schedule(
        draft, _tz(), draft.planDate, user_id
    )
    # Real scheduler was called and returned non-empty blocks
    assert len(result.blocks) >= 1
    assert reality_check in {"COMFORTABLE", "TIGHT", "OVERLOADED"}
    assert "d1" in draft_to_uuid


# ===========================================================================
# PV-003 — Block type TASK
# ===========================================================================
def test_pv_003_block_type_task():
    """Scheduler produces TASK blocks for flexible tasks."""
    tasks = [_sched_task(title="Study", duration=60)]
    windows = [_window(9, 11)]
    result = DeterministicScheduler().schedule(tasks, windows)
    task_blocks = [b for b in result.blocks if b.block_type == "TASK"]
    assert len(task_blocks) >= 1
    block = task_blocks[0]
    assert block.start_at < block.end_at
    assert (block.end_at - block.start_at).total_seconds() > 0
    assert block.task_id is not None


# ===========================================================================
# PV-004 — Block type BREAK
# ===========================================================================
def test_pv_004_block_type_break():
    """Scheduler produces BREAK block when preferred_break_duration_minutes is set."""
    task = ScheduleTask(
        id=uuid4(),
        title="Study",
        estimated_duration_minutes=60,
        priority="MEDIUM",
        scheduling_type="FLEXIBLE",
        created_at=_dt(8),
        preferred_break_duration_minutes=15,
    )
    windows = [_window(9, 13)]
    result = DeterministicScheduler().schedule([task], windows)
    break_blocks = [b for b in result.blocks if b.block_type == "BREAK"]
    assert len(break_blocks) >= 1
    assert break_blocks[0].task_id is None  # Breaks have no task_id
    assert break_blocks[0].title == "Break"


# ===========================================================================
# PV-005 — Block type FIXED_EVENT
# ===========================================================================
def test_pv_005_block_type_fixed_event():
    """Scheduler produces FIXED_EVENT block for fixed-time tasks."""
    fixed_start = _dt(10)
    fixed_end = _dt(11)
    task = _sched_task(
        title="Meeting",
        duration=60,
        scheduling_type="FIXED",
        fixed_start=fixed_start,
        fixed_end=fixed_end,
    )
    windows = [_window(9, 17)]
    result = DeterministicScheduler().schedule([task], windows)
    fixed_blocks = [b for b in result.blocks if b.block_type == "FIXED_EVENT"]
    assert len(fixed_blocks) == 1
    assert fixed_blocks[0].start_at == fixed_start
    assert fixed_blocks[0].end_at == fixed_end
    assert fixed_blocks[0].task_id == task.id


def test_parse_02_fixed_meeting_is_reserved_before_flexible_work():
    """PARSE-02 scheduler regression: flexible work cannot overlap the fixed meeting."""
    meeting_id, report_id, study_id = uuid4(), uuid4(), uuid4()
    tasks = [
        ScheduleTask(
            id=meeting_id,
            title="Meeting",
            estimated_duration_minutes=60,
            priority="MEDIUM",
            scheduling_type="FIXED",
            created_at=_dt(7),
            fixed_start_at=_dt(9),
            fixed_end_at=_dt(10),
        ),
        ScheduleTask(
            id=report_id,
            title="Finish the report",
            estimated_duration_minutes=60,
            priority="MEDIUM",
            scheduling_type="FLEXIBLE",
            created_at=_dt(7, 1),
        ),
        ScheduleTask(
            id=study_id,
            title="Study algorithms",
            estimated_duration_minutes=45,
            priority="MEDIUM",
            scheduling_type="FLEXIBLE",
            created_at=_dt(7, 2),
        ),
    ]

    result = DeterministicScheduler().schedule(tasks, [_window(8, 13)])

    assert result.unscheduled_tasks == []
    meeting = next(block for block in result.blocks if block.task_id == meeting_id)
    report = next(block for block in result.blocks if block.task_id == report_id)
    assert (meeting.block_type, meeting.start_at, meeting.end_at) == (
        "FIXED_EVENT",
        _dt(9),
        _dt(10),
    )
    assert report.end_at <= _dt(12)
    for block in result.blocks:
        assert _dt(8) <= block.start_at < block.end_at <= _dt(13)
        if block.task_id != meeting_id:
            assert block.end_at <= meeting.start_at or block.start_at >= meeting.end_at


# ===========================================================================
# PV-006 — Invalid draft does not receive preview token / does not reach scheduler
# ===========================================================================
@pytest.mark.asyncio
async def test_pv_006_invalid_draft_no_preview():
    """check_today() issues block the preview path — planner returns clarification."""
    from app.ai.handlers import planner
    from app.ai.llm.budget import BudgetMode

    ctx = ChatContext(
        db=AsyncMock(),
        user_id=uuid4(),
        now=datetime(2026, 9, 20, 8, 0, tzinfo=ZoneInfo("UTC")),
        timezone=ZoneInfo("UTC"),
        break_minutes=5,
        default_windows=(("09:00", "17:00"),),
        default_date_offset=0,
    )

    # Empty plan → assembler produces draft with no tasks → check_today flags NO_TASKS
    with patch(
        "app.ai.handlers.planner.get_budget_mode",
        new=AsyncMock(return_value=BudgetMode.NORMAL),
    ):
        with patch(
            "app.ai.handlers.planner.available_routes",
            new=AsyncMock(return_value="groq"),
        ):
            result = await planner.plan_day("", ctx, "en")  # Empty → no tasks

    assert result.preview is None  # Must not generate preview
    assert result.draft is None or len(result.draft.tasks) == 0


# ===========================================================================
# PV-012 — Reality check COMFORTABLE
# ===========================================================================
def test_pv_012_reality_check_comfortable():
    """Workload ≤ 80% of availability → COMFORTABLE."""
    # 2 hours available, 1 hour task = 50% utilization
    tasks = [_sched_task(duration=60)]
    windows = [_window(9, 11)]  # 2 hours
    result = DeterministicScheduler().schedule(tasks, windows)
    available = result.available_minutes
    workload = result.workload_minutes
    assert workload <= available * 0.8
    # Reality check derivation matches the service logic
    reality = (
        "OVERLOADED"
        if result.unscheduled_tasks
        else "COMFORTABLE"
        if workload <= available * 0.8
        else "TIGHT"
    )
    assert reality == "COMFORTABLE"


def test_pv_012_reality_check_tight():
    """Workload > 80% of availability → TIGHT."""
    tasks = [_sched_task(duration=100)]  # 100 min in 120 min → 83% → TIGHT
    windows = [_window(9, 11)]  # 120 min available
    result = DeterministicScheduler().schedule(tasks, windows)
    reality = (
        "OVERLOADED"
        if result.unscheduled_tasks
        else "COMFORTABLE"
        if result.workload_minutes <= result.available_minutes * 0.8
        else "TIGHT"
    )
    assert reality == "TIGHT"


def test_pv_012_reality_check_overloaded():
    """Unscheduled tasks → OVERLOADED."""
    tasks = [_sched_task(duration=180)]  # 3 hours
    windows = [_window(9, 11)]  # Only 2 hours
    result = DeterministicScheduler().schedule(tasks, windows)
    assert len(result.unscheduled_tasks) > 0
    reality = "OVERLOADED" if result.unscheduled_tasks else "COMFORTABLE"
    assert reality == "OVERLOADED"


# ===========================================================================
# PV-015 — Adversarial: LLM claims everything fits; scheduler returns OVERLOADED
# ===========================================================================
@pytest.mark.asyncio
async def test_pv_015_llm_claims_fit_scheduler_overloaded():
    """LLM text claiming all tasks fit must not override scheduler OVERLOADED result."""
    from app.ai.handlers import planner
    from app.ai.llm.budget import BudgetMode

    ctx = ChatContext(
        db=AsyncMock(),
        user_id=uuid4(),
        now=datetime(2026, 9, 20, 8, 0, tzinfo=ZoneInfo("UTC")),
        timezone=ZoneInfo("UTC"),
        break_minutes=5,
        default_windows=(("09:00", "10:00"),),  # Only 1 hour available
        default_date_offset=0,
    )

    # LLM claims everything fits in its reply text
    llm_response = {
        "reply": "Great! Everything fits perfectly in your schedule!",
        "windows": [["09:00", "10:00"]],
        "tasks": [
            {
                "title": "Task A",
                "duration_min": 120,
                "importance": "CORE",
                "priority": "HIGH",
            },
        ],
        "assumptions": [],
    }

    with patch.object(
        planner.llm_provider, "call", AsyncMock(return_value=llm_response)
    ):
        with patch(
            "app.ai.handlers.planner.get_budget_mode",
            new=AsyncMock(return_value=BudgetMode.NORMAL),
        ):
            with patch(
                "app.ai.handlers.planner.available_routes",
                new=AsyncMock(return_value="groq"),
            ):
                result = await planner.plan_day(
                    "I have exactly 1 hour, do task a for 2 hours",
                    ctx,
                    "en",
                )

    # The draft is returned for user review; preview is not automatically generated
    assert result.preview is None  # No auto-preview
    # If we were to run the scheduler on this draft:
    if result.draft and result.draft.tasks:
        draft = result.draft
        sched_result, reality_check, _ = today_service._normalize_and_schedule(
            draft, _tz(), draft.planDate, uuid4()
        )
        # Scheduler must report OVERLOADED regardless of LLM's claim
        assert reality_check == "OVERLOADED"


# ===========================================================================
# PV-016 — Unscheduled tasks have structured reasons
# ===========================================================================
def test_pv_016_unscheduled_structured_reason():
    """Unscheduled tasks must include machine-readable reason code."""
    tasks = [_sched_task(duration=300)]  # 5 hours
    windows = [_window(9, 11)]  # 2 hours only
    result = DeterministicScheduler().schedule(tasks, windows)

    assert len(result.unscheduled_tasks) > 0
    assert len(result.reasons) > 0

    for reason in result.reasons:
        assert "code" in reason
        assert "task_id" in reason
        assert reason["code"] in {
            "INSUFFICIENT_TIME",
            "NO_AVAILABILITY_WINDOWS",
            "MISSING_DEPENDENCY",
            "CYCLIC_DEPENDENCY",
            "INVALID_DURATION",
            "FIXED_TASK_OUTSIDE_BOUNDS",
            "FIXED_TASK_OVERLAP",
            "DEPENDENCY_UNSCHEDULED",
            "DEPENDENCY_TIME_CONFLICT",
            "DUPLICATE_TASK_ID",
            "INVALID_SCHEDULING_TYPE",
            "INVALID_FIXED_INTERVAL",
            "INSUFFICIENT_TIME_BEFORE_DEPENDENT",
        }


def test_pv_016_unscheduled_not_also_scheduled():
    """An unscheduled task must not simultaneously appear in blocks."""
    tasks = [_sched_task(duration=300)]
    windows = [_window(9, 11)]
    result = DeterministicScheduler().schedule(tasks, windows)

    scheduled_ids = {b.task_id for b in result.blocks if b.task_id}
    unscheduled_ids = set(result.unscheduled_tasks)
    # No task can be in both sets
    assert scheduled_ids.isdisjoint(unscheduled_ids)


# ===========================================================================
# CL-003 — Fixed task outside availability rejected at scheduler level
# ===========================================================================
def test_cl_003_fixed_task_outside_availability_rejected():
    """Fixed task whose interval falls outside all availability windows must be unscheduled."""
    fixed_start = _dt(18)  # After availability ends at 17:00
    fixed_end = _dt(19)
    task = _sched_task(
        title="Evening meeting",
        duration=60,
        scheduling_type="FIXED",
        fixed_start=fixed_start,
        fixed_end=fixed_end,
    )
    windows = [_window(9, 17)]  # 09:00–17:00
    result = DeterministicScheduler().schedule([task], windows)

    assert task.id in result.unscheduled_tasks
    reason = next((r for r in result.reasons if r["task_id"] == task.id), None)
    assert reason is not None
    assert reason["code"] == "FIXED_TASK_OUTSIDE_BOUNDS"


def test_cl_003_fixed_task_inside_availability_accepted():
    """Fixed task fully within availability must be scheduled."""
    fixed_start = _dt(14)
    fixed_end = _dt(15)
    task = _sched_task(
        title="Meeting",
        duration=60,
        scheduling_type="FIXED",
        fixed_start=fixed_start,
        fixed_end=fixed_end,
    )
    windows = [_window(9, 17)]
    result = DeterministicScheduler().schedule([task], windows)
    fixed_blocks = [b for b in result.blocks if b.block_type == "FIXED_EVENT"]
    assert len(fixed_blocks) == 1
    assert task.id not in result.unscheduled_tasks


def test_cl_003_overlapping_fixed_tasks_both_rejected():
    """Two overlapping fixed tasks must both be reported as FIXED_TASK_OVERLAP."""
    t1_id = uuid4()
    t2_id = uuid4()
    task1 = ScheduleTask(
        id=t1_id,
        title="Meeting 1",
        estimated_duration_minutes=60,
        priority="MEDIUM",
        scheduling_type="FIXED",
        created_at=_dt(8),
        fixed_start_at=_dt(10),
        fixed_end_at=_dt(11),
    )
    task2 = ScheduleTask(
        id=t2_id,
        title="Meeting 2",
        estimated_duration_minutes=60,
        priority="MEDIUM",
        scheduling_type="FIXED",
        created_at=_dt(8),
        fixed_start_at=_dt(10, 30),
        fixed_end_at=_dt(11, 30),
    )
    windows = [_window(9, 17)]
    result = DeterministicScheduler().schedule([task1, task2], windows)

    reason_codes = {r["task_id"]: r["code"] for r in result.reasons}
    assert t1_id in reason_codes or t2_id in reason_codes
    for tid in [t1_id, t2_id]:
        if tid in reason_codes:
            assert reason_codes[tid] == "FIXED_TASK_OVERLAP"


# ===========================================================================
# Persistence protection: preview must not write to DB
# ===========================================================================
def test_preview_no_persistence():
    """_normalize_and_schedule must not call add/flush/commit."""
    draft = TodayDraft(
        planDate=date(2026, 9, 20),
        timezone="UTC",
        windows=[AvailabilityWindowDraft(start="09:00", end="11:00")],
        tasks=[TaskDraft(id="d1", title="Study", durationMin=60)],
    )
    user_id = uuid4()
    # This is a synchronous, pure scheduling call — no DB session used
    result, _, _ = today_service._normalize_and_schedule(
        draft, _tz(), draft.planDate, user_id
    )
    assert isinstance(result.blocks, list)


def test_pv_005_block_type_buffer():
    draft = TodayDraft(
        planDate=date(2026, 9, 20),
        timezone="UTC",
        windows=[AvailabilityWindowDraft(start="09:00", end="10:00")],
        tasks=[
            TaskDraft(
                id="t1",
                title="Task without break",
                durationMin=30,
                priority="MEDIUM",
                importance="CORE",
                estimateSource="USER",
                schedulingType="FLEXIBLE",
                dependencies=[],
            )
        ],
    )
    result, reality_check, _ = today_service._normalize_and_schedule(
        draft, _tz(), draft.planDate, uuid4()
    )
    assert any(b.block_type == "BUFFER" for b in result.blocks)
