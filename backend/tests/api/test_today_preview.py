from datetime import date, datetime, timedelta, timezone
from unittest.mock import patch
from uuid import uuid4

import pytest
from fastapi.encoders import jsonable_encoder
from app.core.scheduler import DeterministicScheduler
from app.db.models.daily_plans import DailyPlan, PlanBlock, PlanRevision
from app.db.models.tasks import Task, TaskDependency
from app.schemas.drafts import AvailabilityWindowDraft, TaskDraft, TodayDraft
from app.services.today_service import today_service
from httpx import AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

pytestmark = pytest.mark.asyncio


async def get_preview_token(
    async_client: AsyncClient, auth_headers: dict[str, str], draft_json: dict
) -> str:
    resp = await async_client.post(
        "/api/v1/today/preview", headers=auth_headers, json={"draft": draft_json}
    )
    assert resp.status_code == 200, resp.text
    return resp.json()["preview_token"]


async def test_today_save_success_and_idempotency(
    async_client: AsyncClient,
    auth_headers: dict[str, str],
    test_user: dict,
    db_session: AsyncSession,
):
    draft = TodayDraft(
        type="today",
        planDate=date.today().isoformat(),
        timezone="UTC",
        windows=[AvailabilityWindowDraft(start="09:00", end="17:00")],
        tasks=[
            TaskDraft(id="t1", title="Task 1", durationMin=60, priority="HIGH"),
            TaskDraft(
                id="t2",
                title="Task 2",
                durationMin=30,
                priority="MEDIUM",
                dependencies=["t1"],
            ),
        ],
    )
    draft_dict = draft.model_dump(mode="json")

    token1 = await get_preview_token(async_client, auth_headers, draft_dict)

    save_resp1 = await async_client.post(
        "/api/v1/today/save",
        headers=auth_headers,
        json={"preview_token": token1, "draft": draft_dict},
    )
    assert save_resp1.status_code == 200

    plan_res = await db_session.execute(
        select(DailyPlan).where(DailyPlan.user_id == test_user.id)
    )
    plan = plan_res.scalars().first()
    assert plan is not None

    token2 = await get_preview_token(async_client, auth_headers, draft_dict)
    # Don't assert token1 == token2 since expiry makes them differ

    save_resp2 = await async_client.post(
        "/api/v1/today/save",
        headers=auth_headers,
        json={"preview_token": token2, "draft": draft_dict},
    )
    assert save_resp2.status_code == 200

    tasks_res = await db_session.execute(select(Task).where(Task.title == "Task 1"))
    assert len(tasks_res.scalars().all()) == 1


async def test_preview_save_and_reload_preserve_planning_fields(
    async_client: AsyncClient,
    auth_headers: dict[str, str],
    test_user: dict,
    db_session: AsyncSession,
):
    draft = TodayDraft(
        planDate=date.today(),
        timezone="UTC",
        windows=[AvailabilityWindowDraft(start="09:00", end="17:00")],
        tasks=[
            TaskDraft(
                id="preserved",
                title="Write report",
                durationMin=60,
                priority="HIGH",
                importance="OPTIONAL",
                category="Work",
                estimateSource="USER",
                breakAfterMin=10,
            )
        ],
    )
    payload = draft.model_dump(mode="json")
    preview = await async_client.post(
        "/api/v1/today/preview", headers=auth_headers, json={"draft": payload}
    )
    assert preview.status_code == 200, preview.text
    task_block = next(
        block for block in preview.json()["blocks"] if block["block_type"] == "TASK"
    )
    assert task_block["importance"] == "OPTIONAL"
    assert task_block["category"] == "Work"
    assert task_block["preferred_break_duration_minutes"] == 10
    assert any(block["block_type"] == "BREAK" for block in preview.json()["blocks"])

    saved = await async_client.post(
        "/api/v1/today/save",
        headers=auth_headers,
        json={"preview_token": preview.json()["preview_token"], "draft": payload},
    )
    assert saved.status_code == 200, saved.text
    stored = await db_session.scalar(
        select(Task).where(Task.user_id == test_user.id, Task.title == "Write report")
    )
    assert stored.importance == "OPTIONAL"
    assert stored.category == "Work"
    assert stored.preferred_break_duration_minutes == 10
    assert stored.source == "MANUAL"

    restored = await async_client.get("/api/v1/today", headers=auth_headers)
    restored_task = next(
        block for block in restored.json()["blocks"] if block["block_type"] == "TASK"
    )
    assert restored_task["importance"] == "OPTIONAL"
    assert restored_task["category"] == "Work"
    assert restored_task["preferred_break_duration_minutes"] == 10


async def test_today_save_atomic_rollback(
    async_client: AsyncClient,
    auth_headers: dict[str, str],
    test_user: dict,
    db_session: AsyncSession,
):
    user_id = test_user.id
    draft = TodayDraft(
        type="today",
        planDate=date.today().isoformat(),
        timezone="UTC",
        windows=[AvailabilityWindowDraft(start="09:00", end="17:00")],
        tasks=[
            TaskDraft(id="t1", title="Valid Title", durationMin=60, priority="HIGH"),
            TaskDraft(
                id="t2", title="Dependent Title", durationMin=30, dependencies=["t1"]
            ),
        ],
    )
    draft_dict = draft.model_dump(mode="json")
    token = await get_preview_token(async_client, auth_headers, draft_dict)

    async def mock_commit(*args, **kwargs):
        raise ValueError("Injected DB failure after flushes, during commit")

    with patch("sqlalchemy.ext.asyncio.AsyncSession.commit", new=mock_commit):
        save_resp = await async_client.post(
            "/api/v1/today/save",
            headers=auth_headers,
            json={"preview_token": token, "draft": draft_dict},
        )
        assert save_resp.status_code == 500

    plan_res = await db_session.execute(
        select(DailyPlan).where(DailyPlan.user_id == user_id)
    )
    assert plan_res.scalars().first() is None
    tasks_res = await db_session.execute(select(Task).where(Task.user_id == user_id))
    assert tasks_res.scalars().first() is None
    blocks_res = await db_session.execute(select(PlanBlock))
    assert blocks_res.scalars().first() is None
    deps_res = await db_session.execute(select(TaskDependency))
    assert deps_res.scalars().first() is None
    rev_res = await db_session.execute(select(PlanRevision))
    assert rev_res.scalars().first() is None


async def test_deterministic_consistency(
    async_client: AsyncClient,
    auth_headers: dict[str, str],
    test_user: dict,
    db_session: AsyncSession,
):
    draft = TodayDraft(
        type="today",
        planDate=date.today().isoformat(),
        timezone="UTC",
        windows=[AvailabilityWindowDraft(start="09:00", end="17:00")],
        tasks=[
            TaskDraft(
                id="t1", title="Consistency Task", durationMin=60, priority="HIGH"
            )
        ],
    )
    draft_dict = draft.model_dump(mode="json")

    preview_resp = await async_client.post(
        "/api/v1/today/preview", headers=auth_headers, json={"draft": draft_dict}
    )
    assert preview_resp.status_code == 200
    preview_data = preview_resp.json()
    preview_blocks = preview_data["blocks"]

    save_resp = await async_client.post(
        "/api/v1/today/save",
        headers=auth_headers,
        json={"preview_token": preview_data["preview_token"], "draft": draft_dict},
    )
    assert save_resp.status_code == 200
    save_data = save_resp.json()
    save_blocks = save_data["blocks"]

    assert len(preview_blocks) == len(save_blocks)
    for p_block, s_block in zip(preview_blocks, save_blocks):
        assert p_block["block_type"] == s_block["block_type"]
        assert p_block["planned_start_at"] == s_block["planned_start_at"]
        assert p_block["planned_end_at"] == s_block["planned_end_at"]
        assert p_block["position"] == s_block["position"]
        assert p_block["draft_task_id"] == s_block["draft_task_id"]
    assert save_blocks[0]["draft_task_id"] == "t1"

    restored = await async_client.get("/api/v1/today", headers=auth_headers)
    assert restored.status_code == 200
    assert [block["draft_task_id"] for block in restored.json()["blocks"]] == [
        block["draft_task_id"] for block in preview_blocks
    ]


async def test_invalid_token(
    async_client: AsyncClient, auth_headers: dict[str, str], test_user: dict
):
    user_id = test_user.id
    draft = TodayDraft(
        type="today",
        planDate=date.today().isoformat(),
        timezone="UTC",
        windows=[AvailabilityWindowDraft(start="09:00", end="17:00")],
        tasks=[TaskDraft(id="valid", title="Valid task", durationMin=30)],
    )
    draft_dict = draft.model_dump(mode="json")

    save_resp = await async_client.post(
        "/api/v1/today/save",
        headers=auth_headers,
        json={"preview_token": "invalid_token", "draft": draft_dict},
    )
    assert save_resp.status_code == 409

    import time

    draft_json = draft.model_dump_json()
    with patch("time.time", return_value=time.time() - 90000):
        expired_token = today_service._generate_hmac_token(user_id, draft_json)

    save_resp2 = await async_client.post(
        "/api/v1/today/save",
        headers=auth_headers,
        json={"preview_token": expired_token, "draft": draft_dict},
    )
    assert save_resp2.status_code == 409

    cross_token = today_service._generate_hmac_token(uuid4(), draft_json)

    save_resp3 = await async_client.post(
        "/api/v1/today/save",
        headers=auth_headers,
        json={"preview_token": cross_token, "draft": draft_dict},
    )
    assert save_resp3.status_code == 409

    valid_token = await get_preview_token(async_client, auth_headers, draft_dict)
    tampered_token = valid_token[:-1] + ("A" if valid_token[-1] != "A" else "B")
    tampered = await async_client.post(
        "/api/v1/today/save",
        headers=auth_headers,
        json={"preview_token": tampered_token, "draft": draft_dict},
    )
    assert tampered.status_code == 409

    changed_date = {
        **draft_dict,
        "planDate": (date.today() + timedelta(days=1)).isoformat(),
    }
    wrong_date = await async_client.post(
        "/api/v1/today/save",
        headers=auth_headers,
        json={"preview_token": valid_token, "draft": changed_date},
    )
    assert wrong_date.status_code == 409


async def test_draft_modified_after_preview(
    async_client: AsyncClient, auth_headers: dict[str, str], test_user: dict
):
    draft = TodayDraft(
        type="today",
        planDate=date.today().isoformat(),
        timezone="UTC",
        windows=[AvailabilityWindowDraft(start="09:00", end="17:00")],
        tasks=[TaskDraft(id="t1", title="Task 1", durationMin=60, priority="HIGH")],
    )
    draft_dict = draft.model_dump(mode="json")
    token = await get_preview_token(async_client, auth_headers, draft_dict)

    draft_dict["tasks"][0]["title"] = "Modified Task"

    save_resp = await async_client.post(
        "/api/v1/today/save",
        headers=auth_headers,
        json={"preview_token": token, "draft": draft_dict},
    )
    assert save_resp.status_code == 409


async def test_edited_draft_in_same_session(
    async_client: AsyncClient,
    auth_headers: dict[str, str],
    test_user: dict,
    db_session: AsyncSession,
):
    draft1 = TodayDraft(
        type="today",
        planDate=date.today().isoformat(),
        timezone="UTC",
        windows=[AvailabilityWindowDraft(start="09:00", end="17:00")],
        tasks=[TaskDraft(id="t1", title="Task 1", durationMin=60, priority="HIGH")],
    )
    draft_dict1 = draft1.model_dump(mode="json")
    token1 = await get_preview_token(async_client, auth_headers, draft_dict1)
    await async_client.post(
        "/api/v1/today/save",
        headers=auth_headers,
        json={"preview_token": token1, "draft": draft_dict1},
    )

    draft2 = TodayDraft(
        type="today",
        planDate=date.today().isoformat(),
        timezone="UTC",
        windows=[AvailabilityWindowDraft(start="09:00", end="17:00")],
        tasks=[TaskDraft(id="t2", title="Task 2", durationMin=30, priority="HIGH")],
    )
    draft_dict2 = draft2.model_dump(mode="json")
    token2 = await get_preview_token(async_client, auth_headers, draft_dict2)
    save_resp = await async_client.post(
        "/api/v1/today/save",
        headers=auth_headers,
        json={"preview_token": token2, "draft": draft_dict2},
    )
    assert save_resp.status_code == 409
    save_resp = await async_client.post(
        "/api/v1/today/save",
        headers=auth_headers,
        json={"preview_token": token2, "draft": draft_dict2, "replace_existing": True},
    )
    assert save_resp.status_code == 200
    assert [
        block["title"]
        for block in save_resp.json()["blocks"]
        if block["block_type"] == "TASK"
    ] == ["Task 2"]

    tasks_res = await db_session.execute(select(Task).where(Task.title == "Task 1"))
    assert tasks_res.scalars().first() is None
    tasks_res2 = await db_session.execute(select(Task).where(Task.title == "Task 2"))
    assert tasks_res2.scalars().first() is not None


async def test_replace_existing_preserves_completed_history_and_replaces_future_work(
    async_client: AsyncClient,
    auth_headers: dict[str, str],
    test_user: dict,
    db_session: AsyncSession,
):
    target_date = date.today() + timedelta(days=1)
    original = TodayDraft(
        type="today",
        planDate=target_date,
        timezone="UTC",
        windows=[AvailabilityWindowDraft(start="08:00", end="18:00")],
        tasks=[
            TaskDraft(
                id="old-done",
                title="Completed history",
                durationMin=30,
                priority="HIGH",
            ),
            TaskDraft(
                id="old-future", title="Old unfinished future work", durationMin=60
            ),
        ],
    ).model_dump(mode="json")
    original_token = await get_preview_token(async_client, auth_headers, original)
    original_save = await async_client.post(
        "/api/v1/today/save",
        headers=auth_headers,
        json={"preview_token": original_token, "draft": original},
    )
    assert original_save.status_code == 200, original_save.text

    plan = await db_session.scalar(
        select(DailyPlan).where(
            DailyPlan.user_id == test_user.id,
            DailyPlan.plan_date == target_date,
            DailyPlan.status == "ACTIVE",
        )
    )
    assert plan is not None
    original_plan_id = plan.id
    completed_block = await db_session.scalar(
        select(PlanBlock).where(
            PlanBlock.daily_plan_id == plan.id,
            PlanBlock.title == "Completed history",
        )
    )
    assert completed_block is not None
    completed_block.status = "COMPLETED"
    completed_block.completed_at = datetime.now(timezone.utc)
    completed_task = await db_session.get(Task, completed_block.task_id)
    assert completed_task is not None
    completed_task.status = "COMPLETED"
    completed_task.completed_at = datetime.now(timezone.utc)
    await db_session.commit()

    replacement = TodayDraft(
        type="today",
        planDate=target_date,
        timezone="UTC",
        windows=[AvailabilityWindowDraft(start="09:00", end="17:00")],
        tasks=[TaskDraft(id="new-task", title="New reviewed work", durationMin=45)],
    ).model_dump(mode="json")
    replacement_token = await get_preview_token(async_client, auth_headers, replacement)
    rejected = await async_client.post(
        "/api/v1/today/save",
        headers=auth_headers,
        json={"preview_token": replacement_token, "draft": replacement},
    )
    assert rejected.status_code == 409
    assert rejected.json()["detail"]["code"] == "PLAN_EXISTS"

    unchanged = await async_client.get(
        f"/api/v1/today?date={target_date.isoformat()}", headers=auth_headers
    )
    assert {
        block["title"]
        for block in unchanged.json()["blocks"]
        if block["block_type"] == "TASK"
    } == {"Completed history", "Old unfinished future work"}

    payload = {
        "preview_token": replacement_token,
        "idempotency_key": replacement_token,
        "draft": replacement,
        "replace_existing": True,
    }
    replaced = await async_client.post(
        "/api/v1/today/save", headers=auth_headers, json=payload
    )
    assert replaced.status_code == 200, replaced.text
    titles = {
        block["title"]
        for block in replaced.json()["blocks"]
        if block["block_type"] == "TASK"
    }
    assert titles == {"Completed history", "New reviewed work"}

    retry = await async_client.post(
        "/api/v1/today/save", headers=auth_headers, json=payload
    )
    assert retry.status_code == 200, retry.text
    reloaded = await async_client.get(
        f"/api/v1/today?date={target_date.isoformat()}", headers=auth_headers
    )
    assert reloaded.status_code == 200
    reloaded_titles = [
        block["title"]
        for block in reloaded.json()["blocks"]
        if block["block_type"] == "TASK"
    ]
    assert sorted(reloaded_titles) == ["Completed history", "New reviewed work"]

    active_plans = (
        await db_session.scalars(
            select(DailyPlan).where(
                DailyPlan.user_id == test_user.id,
                DailyPlan.plan_date == target_date,
                DailyPlan.status.in_(("DRAFT", "CONFIRMED", "ACTIVE")),
            )
        )
    ).all()
    assert len(active_plans) == 1
    assert active_plans[0].id == original_plan_id


async def test_fixed_datetimes(
    async_client: AsyncClient, auth_headers: dict[str, str], test_user: dict
):
    aware_dt = datetime.now(timezone.utc).replace(
        hour=10, minute=0, second=0, microsecond=0
    )
    deadline_date = date.today()

    draft = TodayDraft(
        type="today",
        planDate=datetime.now(timezone.utc).date().isoformat(),
        timezone="UTC",
        windows=[AvailabilityWindowDraft(start="09:00", end="17:00")],
        tasks=[
            TaskDraft(
                id="t1",
                title="Fixed 1",
                durationMin=60,
                schedulingType="FIXED",
                fixedStart=aware_dt.isoformat(),
                fixedEnd=(aware_dt + timedelta(minutes=60)).isoformat(),
                deadline=deadline_date.isoformat(),
            ),
        ],
    )
    draft_dict = draft.model_dump(mode="json")
    preview = await async_client.post(
        "/api/v1/today/preview", headers=auth_headers, json={"draft": draft_dict}
    )
    assert preview.status_code == 200
    resp = await async_client.post(
        "/api/v1/today/save",
        headers=auth_headers,
        json={"preview_token": preview.json()["preview_token"], "draft": draft_dict},
    )
    assert resp.status_code == 200
    assert (
        preview.json()["blocks"][0]["draft_task_id"]
        == resp.json()["blocks"][0]["draft_task_id"]
        == "t1"
    )


async def test_overlapping_fixed_tasks(
    async_client: AsyncClient, auth_headers: dict[str, str], test_user: dict
):
    dt1 = datetime.now(timezone.utc).replace(hour=10, minute=0, second=0, microsecond=0)
    dt2 = datetime.now(timezone.utc).replace(
        hour=10, minute=30, second=0, microsecond=0
    )

    draft = {
        "type": "today",
        "planDate": datetime.now(timezone.utc).date().isoformat(),
        "timezone": "UTC",
        "windows": [{"start": "09:00", "end": "17:00"}],
        "tasks": [
            {
                "id": "t1",
                "title": "Fixed 1",
                "durationMin": 60,
                "schedulingType": "FIXED",
                "fixedStart": dt1.isoformat(),
                "fixedEnd": (dt1 + timedelta(minutes=60)).isoformat(),
                "dependencies": [],
            },
            {
                "id": "t2",
                "title": "Fixed 2",
                "durationMin": 60,
                "schedulingType": "FIXED",
                "fixedStart": dt2.isoformat(),
                "fixedEnd": (dt2 + timedelta(minutes=60)).isoformat(),
                "dependencies": [],
            },
        ],
    }
    resp = await async_client.post(
        "/api/v1/today/preview", headers=auth_headers, json={"draft": draft}
    )
    assert resp.status_code == 422


async def test_transaction_not_already_begun(
    async_client: AsyncClient,
    auth_headers: dict[str, str],
    test_user: dict,
    db_session: AsyncSession,
):
    # Proves that no "transaction already begun" is raised when save_today_draft executes
    draft = TodayDraft(
        type="today",
        planDate=date.today().isoformat(),
        timezone="UTC",
        windows=[AvailabilityWindowDraft(start="09:00", end="17:00")],
        tasks=[TaskDraft(id="t_tx", title="TX Test", durationMin=15, priority="LOW")],
    )
    draft_dict = draft.model_dump(mode="json")
    token = await get_preview_token(async_client, auth_headers, draft_dict)

    # Send the request; if transaction was already begun and db.begin() was improperly called, it would 500
    save_resp = await async_client.post(
        "/api/v1/today/save",
        headers=auth_headers,
        json={"preview_token": token, "draft": draft_dict},
    )
    assert save_resp.status_code == 200


async def test_overloaded_schedule_preview(
    async_client: AsyncClient,
    auth_headers: dict[str, str],
    test_user: dict,
    db_session: AsyncSession,
    monkeypatch,
):
    actual_reasons = []
    original_schedule = DeterministicScheduler.schedule

    def capture_schedule(self, tasks, windows, *args, **kwargs):
        result = original_schedule(self, tasks, windows, *args, **kwargs)
        actual_reasons.extend(jsonable_encoder(result.reasons))
        return result

    monkeypatch.setattr(DeterministicScheduler, "schedule", capture_schedule)
    draft = TodayDraft(
        type="today",
        planDate=date.today().isoformat(),
        timezone="UTC",
        windows=[
            AvailabilityWindowDraft(start="09:00", end="10:00")
        ],  # Only 1 hour available
        tasks=[
            TaskDraft(
                id="t_over1", title="Too Big Task", durationMin=120, priority="HIGH"
            ),
            TaskDraft(
                id="t_over2",
                title="Another Big Task",
                durationMin=120,
                priority="MEDIUM",
            ),
        ],
    )
    draft_dict = draft.model_dump(mode="json")

    resp = await async_client.post(
        "/api/v1/today/preview", headers=auth_headers, json={"draft": draft_dict}
    )
    assert resp.status_code == 200
    data = resp.json()

    assert data["reality_check"] == "OVERLOADED"

    unsched = data["unscheduled_tasks"]
    assert len(unsched) > 0
    assert {task["draft_task_id"] for task in unsched} == {"t_over1", "t_over2"}
    assert {task["reason"] for task in unsched} == {"INSUFFICIENT_TIME"}

    reasons = data["reasons"]
    assert len(reasons) > 0
    # The response schema always carries dependency_id, null when absent.
    def present(items):
        return [{k: v for k, v in r.items() if v is not None} for r in items]
    assert present(reasons) == present(actual_reasons)
    assert {reason["code"] for reason in reasons} == {"INSUFFICIENT_TIME"}

    plan_res = await db_session.execute(
        select(DailyPlan).where(DailyPlan.user_id == test_user.id)
    )
    assert plan_res.scalars().first() is None
    tasks_res = await db_session.execute(
        select(Task).where(Task.user_id == test_user.id)
    )
    assert tasks_res.scalars().first() is None

    saved = await async_client.post(
        "/api/v1/today/save",
        headers=auth_headers,
        json={"preview_token": data["preview_token"], "draft": draft_dict},
    )
    assert saved.status_code == 200, saved.text
    assert saved.json()["unscheduled_tasks"] == unsched
    assert present(saved.json()["reasons"]) == present(reasons)

    restored = await async_client.get("/api/v1/today", headers=auth_headers)
    assert restored.status_code == 200
    assert restored.json()["unscheduled_tasks"] == unsched

async def test_removed_task_with_focus_preserves_task_but_drops_dependencies(
    async_client: AsyncClient,
    auth_headers: dict[str, str],
    test_user: dict,
    db_session: AsyncSession,
):
    from app.db.models.focus import FocusRun
    
    # 1. Create a first draft with two dependent tasks
    draft_1 = TodayDraft(
        type="today",
        planDate=date.today().isoformat(),
        timezone="UTC",
        windows=[AvailabilityWindowDraft(start="09:00", end="17:00")],
        tasks=[
            TaskDraft(id="t1", title="Task 1", durationMin=30, dependencies=[]),
            TaskDraft(id="t2", title="Task 2", durationMin=30, dependencies=["t1"]),
        ],
    )
    token_1 = await get_preview_token(async_client, auth_headers, draft_1.model_dump(mode="json"))
    save_resp_1 = await async_client.post(
        "/api/v1/today/save",
        headers=auth_headers,
        json={"preview_token": token_1, "draft": draft_1.model_dump(mode="json")},
    )
    assert save_resp_1.status_code == 200

    plan_1_data = save_resp_1.json()
    blocks = plan_1_data["blocks"]
    
    # Map draft IDs to real Task IDs
    task1_id = next(b["task_id"] for b in blocks if b["draft_task_id"] == "t1")
    task2_id = next(b["task_id"] for b in blocks if b["draft_task_id"] == "t2")
    
    now = datetime.now(timezone.utc)
    
    # 2. Add a FocusRun to Task 1
    run = FocusRun(
        user_id=test_user.id,
        task_id=task1_id,
        planned_focus_seconds=1500,
        status="ENDED",
        outcome="NEED_MORE_TIME",
        started_at=now - timedelta(minutes=25),
        ended_at=now,
        actual_duration_seconds=1500
    )
    db_session.add(run)
    await db_session.commit()
    
    # 3. Create a second draft that drops Task 1 (the one with the FocusRun) but keeps Task 2
    # The new draft does not carry 't1' in, so it counts as removed.
    draft_2 = TodayDraft(
        type="today",
        planDate=date.today().isoformat(),
        timezone="UTC",
        windows=[AvailabilityWindowDraft(start="09:00", end="17:00")],
        tasks=[
            TaskDraft(id="t2", sourceTaskId=str(task2_id), title="Task 2", durationMin=30, dependencies=[]),
        ],
    )
    token_2 = await get_preview_token(async_client, auth_headers, draft_2.model_dump(mode="json"))
    save_resp_2 = await async_client.post(
        "/api/v1/today/save",
        headers=auth_headers,
        json={"preview_token": token_2, "draft": draft_2.model_dump(mode="json")},
    )
    assert save_resp_2.status_code == 200
    
    # 4. Verify outcomes
    await db_session.expire_all()
    
    # historical task remains in DB as CANCELLED
    task1 = await db_session.get(Task, task1_id)
    assert task1 is not None
    assert task1.status == "CANCELLED"
    
    # FocusRun remains valid
    runs = (await db_session.execute(select(FocusRun).where(FocusRun.task_id == task1_id))).scalars().all()
    assert len(runs) == 1
    
    # obsolete TaskDependency row is gone
    deps = (await db_session.execute(
        select(TaskDependency)
        .where((TaskDependency.task_id == task1_id) | (TaskDependency.depends_on_task_id == task1_id))
    )).scalars().all()
    assert len(deps) == 0
    
    # remaining task is kept
    task2 = await db_session.get(Task, task2_id)
    assert task2 is not None
    assert task2.status != "CANCELLED"
