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

async def get_preview_token(async_client: AsyncClient, auth_headers: dict[str, str], draft_json: dict) -> str:
    resp = await async_client.post(
        "/api/v1/today/preview",
        headers=auth_headers,
        json={"draft": draft_json}
    )
    assert resp.status_code == 200, resp.text
    return resp.json()["preview_token"]

async def test_today_save_success_and_idempotency(async_client: AsyncClient, auth_headers: dict[str, str], test_user: dict, db_session: AsyncSession):
    draft = TodayDraft(
        type="today",
        planDate=date.today().isoformat(),
        timezone="UTC",
        windows=[AvailabilityWindowDraft(start="09:00", end="17:00")],
        tasks=[
            TaskDraft(id="t1", title="Task 1", durationMin=60, priority="HIGH"),
            TaskDraft(id="t2", title="Task 2", durationMin=30, priority="MEDIUM", dependencies=["t1"])
        ]
    )
    draft_dict = draft.model_dump(mode="json")
    
    token1 = await get_preview_token(async_client, auth_headers, draft_dict)
    
    save_resp1 = await async_client.post("/api/v1/today/save", headers=auth_headers, json={"preview_token": token1, "draft": draft_dict})
    assert save_resp1.status_code == 200
    
    plan_res = await db_session.execute(select(DailyPlan).where(DailyPlan.user_id == test_user.id))
    plan = plan_res.scalars().first()
    assert plan is not None
    
    token2 = await get_preview_token(async_client, auth_headers, draft_dict)
    # Don't assert token1 == token2 since expiry makes them differ
    
    save_resp2 = await async_client.post("/api/v1/today/save", headers=auth_headers, json={"preview_token": token2, "draft": draft_dict})
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

async def test_today_save_atomic_rollback(async_client: AsyncClient, auth_headers: dict[str, str], test_user: dict, db_session: AsyncSession):
    user_id = test_user.id
    draft = TodayDraft(
        type="today",
        planDate=date.today().isoformat(),
        timezone="UTC",
        windows=[AvailabilityWindowDraft(start="09:00", end="17:00")],
        tasks=[
            TaskDraft(id="t1", title="Valid Title", durationMin=60, priority="HIGH"),
            TaskDraft(id="t2", title="Dependent Title", durationMin=30, dependencies=["t1"]),
        ]
    )
    draft_dict = draft.model_dump(mode="json")
    token = await get_preview_token(async_client, auth_headers, draft_dict)
    
    async def mock_commit(*args, **kwargs):
        raise ValueError("Injected DB failure after flushes, during commit")
        
    with patch("sqlalchemy.ext.asyncio.AsyncSession.commit", new=mock_commit):
        save_resp = await async_client.post("/api/v1/today/save", headers=auth_headers, json={"preview_token": token, "draft": draft_dict})
        assert save_resp.status_code == 500
        
    plan_res = await db_session.execute(select(DailyPlan).where(DailyPlan.user_id == user_id))
    assert plan_res.scalars().first() is None
    tasks_res = await db_session.execute(select(Task).where(Task.user_id == user_id))
    assert tasks_res.scalars().first() is None
    blocks_res = await db_session.execute(select(PlanBlock))
    assert blocks_res.scalars().first() is None
    deps_res = await db_session.execute(select(TaskDependency))
    assert deps_res.scalars().first() is None
    rev_res = await db_session.execute(select(PlanRevision))
    assert rev_res.scalars().first() is None

async def test_deterministic_consistency(async_client: AsyncClient, auth_headers: dict[str, str], test_user: dict, db_session: AsyncSession):
    draft = TodayDraft(
        type="today",
        planDate=date.today().isoformat(),
        timezone="UTC",
        windows=[AvailabilityWindowDraft(start="09:00", end="17:00")],
        tasks=[
            TaskDraft(id="t1", title="Consistency Task", durationMin=60, priority="HIGH")
        ]
    )
    draft_dict = draft.model_dump(mode="json")
    
    preview_resp = await async_client.post("/api/v1/today/preview", headers=auth_headers, json={"draft": draft_dict})
    assert preview_resp.status_code == 200
    preview_data = preview_resp.json()
    preview_blocks = preview_data["blocks"]
    
    save_resp = await async_client.post("/api/v1/today/save", headers=auth_headers, json={"preview_token": preview_data["preview_token"], "draft": draft_dict})
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

async def test_invalid_token(async_client: AsyncClient, auth_headers: dict[str, str], test_user: dict):
    user_id = test_user.id
    draft = TodayDraft(
        type="today",
        planDate=date.today().isoformat(),
        timezone="UTC",
        windows=[AvailabilityWindowDraft(start="09:00", end="17:00")],
        tasks=[]
    )
    draft_dict = draft.model_dump(mode="json")
    
    save_resp = await async_client.post("/api/v1/today/save", headers=auth_headers, json={"preview_token": "invalid_token", "draft": draft_dict})
    assert save_resp.status_code == 409
    
    import time

    draft_json = draft.model_dump_json()
    with patch("time.time", return_value=time.time() - 90000):
        expired_token = today_service._generate_hmac_token(user_id, draft_json)
    
    save_resp2 = await async_client.post("/api/v1/today/save", headers=auth_headers, json={"preview_token": expired_token, "draft": draft_dict})
    assert save_resp2.status_code == 409
    
    cross_token = today_service._generate_hmac_token(uuid4(), draft_json)
    
    save_resp3 = await async_client.post("/api/v1/today/save", headers=auth_headers, json={"preview_token": cross_token, "draft": draft_dict})
    assert save_resp3.status_code == 409

    valid_token = await get_preview_token(async_client, auth_headers, draft_dict)
    tampered_token = valid_token[:-1] + ("A" if valid_token[-1] != "A" else "B")
    tampered = await async_client.post(
        "/api/v1/today/save", headers=auth_headers,
        json={"preview_token": tampered_token, "draft": draft_dict},
    )
    assert tampered.status_code == 409

    changed_date = {**draft_dict, "planDate": (date.today() + timedelta(days=1)).isoformat()}
    wrong_date = await async_client.post(
        "/api/v1/today/save", headers=auth_headers,
        json={"preview_token": valid_token, "draft": changed_date},
    )
    assert wrong_date.status_code == 409

async def test_draft_modified_after_preview(async_client: AsyncClient, auth_headers: dict[str, str], test_user: dict):
    draft = TodayDraft(
        type="today",
        planDate=date.today().isoformat(),
        timezone="UTC",
        windows=[AvailabilityWindowDraft(start="09:00", end="17:00")],
        tasks=[TaskDraft(id="t1", title="Task 1", durationMin=60, priority="HIGH")]
    )
    draft_dict = draft.model_dump(mode="json")
    token = await get_preview_token(async_client, auth_headers, draft_dict)
    
    draft_dict["tasks"][0]["title"] = "Modified Task"
    
    save_resp = await async_client.post("/api/v1/today/save", headers=auth_headers, json={"preview_token": token, "draft": draft_dict})
    assert save_resp.status_code == 409

async def test_edited_draft_in_same_session(async_client: AsyncClient, auth_headers: dict[str, str], test_user: dict, db_session: AsyncSession):
    draft1 = TodayDraft(
        type="today",
        planDate=date.today().isoformat(),
        timezone="UTC",
        windows=[AvailabilityWindowDraft(start="09:00", end="17:00")],
        tasks=[TaskDraft(id="t1", title="Task 1", durationMin=60, priority="HIGH")]
    )
    draft_dict1 = draft1.model_dump(mode="json")
    token1 = await get_preview_token(async_client, auth_headers, draft_dict1)
    await async_client.post("/api/v1/today/save", headers=auth_headers, json={"preview_token": token1, "draft": draft_dict1})
    
    draft2 = TodayDraft(
        type="today",
        planDate=date.today().isoformat(),
        timezone="UTC",
        windows=[AvailabilityWindowDraft(start="09:00", end="17:00")],
        tasks=[TaskDraft(id="t2", title="Task 2", durationMin=30, priority="HIGH")]
    )
    draft_dict2 = draft2.model_dump(mode="json")
    token2 = await get_preview_token(async_client, auth_headers, draft_dict2)
    save_resp = await async_client.post("/api/v1/today/save", headers=auth_headers, json={"preview_token": token2, "draft": draft_dict2})
    assert save_resp.status_code == 409
    save_resp = await async_client.post(
        "/api/v1/today/save",
        headers=auth_headers,
        json={"preview_token": token2, "draft": draft_dict2, "replace_existing": True},
    )
    assert save_resp.status_code == 200
    assert [block["title"] for block in save_resp.json()["blocks"]] == ["Task 2"]
    
    tasks_res = await db_session.execute(select(Task).where(Task.title == "Task 1"))
    assert tasks_res.scalars().first() is None
    tasks_res2 = await db_session.execute(select(Task).where(Task.title == "Task 2"))
    assert tasks_res2.scalars().first() is not None

async def test_fixed_datetimes(async_client: AsyncClient, auth_headers: dict[str, str], test_user: dict):
    aware_dt = datetime.now(timezone.utc).replace(hour=10, minute=0, second=0, microsecond=0)
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
                deadline=deadline_date.isoformat()
            ),
        ]
    )
    draft_dict = draft.model_dump(mode="json")
    preview = await async_client.post("/api/v1/today/preview", headers=auth_headers, json={"draft": draft_dict})
    assert preview.status_code == 200
    resp = await async_client.post("/api/v1/today/save", headers=auth_headers, json={"preview_token": preview.json()["preview_token"], "draft": draft_dict})
    assert resp.status_code == 200
    assert preview.json()["blocks"][0]["draft_task_id"] == resp.json()["blocks"][0]["draft_task_id"] == "t1"

async def test_overlapping_fixed_tasks(async_client: AsyncClient, auth_headers: dict[str, str], test_user: dict):
    dt1 = datetime.now(timezone.utc).replace(hour=10, minute=0, second=0, microsecond=0)
    dt2 = datetime.now(timezone.utc).replace(hour=10, minute=30, second=0, microsecond=0)
    
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
                "dependencies": []
            },
            {
                "id": "t2", 
                "title": "Fixed 2", 
                "durationMin": 60, 
                "schedulingType": "FIXED", 
                "fixedStart": dt2.isoformat(), 
                "fixedEnd": (dt2 + timedelta(minutes=60)).isoformat(),
                "dependencies": []
            }
        ]
    }
    resp = await async_client.post("/api/v1/today/preview", headers=auth_headers, json={"draft": draft})
    assert resp.status_code == 422


async def test_transaction_not_already_begun(async_client: AsyncClient, auth_headers: dict[str, str], test_user: dict, db_session: AsyncSession):
    # Proves that no "transaction already begun" is raised when save_today_draft executes
    draft = TodayDraft(
        type="today",
        planDate=date.today().isoformat(),
        timezone="UTC",
        windows=[AvailabilityWindowDraft(start="09:00", end="17:00")],
        tasks=[TaskDraft(id="t_tx", title="TX Test", durationMin=15, priority="LOW")]
    )
    draft_dict = draft.model_dump(mode="json")
    token = await get_preview_token(async_client, auth_headers, draft_dict)
    
    # Send the request; if transaction was already begun and db.begin() was improperly called, it would 500
    save_resp = await async_client.post("/api/v1/today/save", headers=auth_headers, json={"preview_token": token, "draft": draft_dict})
    assert save_resp.status_code == 200



async def test_overloaded_schedule_preview(async_client: AsyncClient, auth_headers: dict[str, str], test_user: dict, db_session: AsyncSession, monkeypatch):
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
        windows=[AvailabilityWindowDraft(start="09:00", end="10:00")], # Only 1 hour available
        tasks=[
            TaskDraft(id="t_over1", title="Too Big Task", durationMin=120, priority="HIGH"),
            TaskDraft(id="t_over2", title="Another Big Task", durationMin=120, priority="MEDIUM")
        ]
    )
    draft_dict = draft.model_dump(mode="json")
    
    resp = await async_client.post("/api/v1/today/preview", headers=auth_headers, json={"draft": draft_dict})
    assert resp.status_code == 200
    data = resp.json()
    
    assert data["reality_check"] == "OVERLOADED"
    
    unsched = data["unscheduled_tasks"]
    assert len(unsched) > 0
    assert {task["draft_task_id"] for task in unsched} == {"t_over1", "t_over2"}
    assert {task["reason"] for task in unsched} == {"INSUFFICIENT_TIME"}
    
    reasons = data["reasons"]
    assert len(reasons) > 0
    assert reasons == actual_reasons
    assert {reason["code"] for reason in reasons} == {"INSUFFICIENT_TIME"}
    
    plan_res = await db_session.execute(select(DailyPlan).where(DailyPlan.user_id == test_user.id))
    assert plan_res.scalars().first() is None
    tasks_res = await db_session.execute(select(Task).where(Task.user_id == test_user.id))
    assert tasks_res.scalars().first() is None

    saved = await async_client.post(
        "/api/v1/today/save", headers=auth_headers,
        json={"preview_token": data["preview_token"], "draft": draft_dict},
    )
    assert saved.status_code == 200, saved.text
    assert saved.json()["unscheduled_tasks"] == unsched
    assert [
        {key: value for key, value in reason.items() if value is not None}
        for reason in saved.json()["reasons"]
    ] == reasons

    restored = await async_client.get("/api/v1/today", headers=auth_headers)
    assert restored.status_code == 200
    assert restored.json()["unscheduled_tasks"] == unsched
