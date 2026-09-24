import pytest
import datetime
from uuid import uuid4
from sqlalchemy import select, func
from app.db.models.tasks import Task
from app.db.models.daily_plans import DailyPlan, PlanRevision

@pytest.mark.asyncio
async def test_deferred_save_integration(async_client, auth_headers, auth_headers_two, db_session, test_user, test_user_two, tz):
    today_str = datetime.date.today().isoformat()
    tomorrow_date = datetime.date.today() + datetime.timedelta(days=1)
    tomorrow_str = tomorrow_date.isoformat()
    
    # 1. Preview to get real token
    draft_payload = {
        "type": "today",
        "planDate": today_str,
        "timezone": "UTC",
        "windows": [{"start": "09:00", "end": "12:00"}],
        "tasks": [{
            "id": "t1", "title": "Today Task", "durationMin": 30, "priority": "HIGH", 
            "schedulingType": "FLEXIBLE", "importance": "CORE", "estimateSource": "USER", 
            "dependencies": [], "splittable": False
        }],
        "deferred_tasks": [{
            "targetDate": tomorrow_str,
            "task": {
                "id": "t2", "title": "Deferred Task", "durationMin": 45, "priority": "MEDIUM", 
                "schedulingType": "FLEXIBLE", "importance": "OPTIONAL", "estimateSource": "USER", 
                "dependencies": [], "splittable": False
            }
        }]
    }

    # Query DB before Save
    before_task_count = await db_session.scalar(select(func.count(Task.id)).where(Task.user_id == test_user.id))
    
    preview_res = await async_client.post("/today/preview", json={"draft": draft_payload}, headers=auth_headers)
    assert preview_res.status_code == 200, preview_res.text
    preview_data = preview_res.json()
    preview_token = preview_data["preview_token"]
    
    # Assert deferred task not in blocks, only today task
    blocks = preview_data["blocks"]
    assert len(blocks) > 0
    assert any(b["title"] == "Today Task" for b in blocks if b["block_type"] == "TASK")
    assert not any(b["title"] == "Deferred Task" for b in blocks if b["block_type"] == "TASK")

    # 2. Save using real preview token
    save_payload = {
        "preview_token": preview_token,
        "draft": draft_payload,
        "replace_existing": True
    }
    save_res = await async_client.post("/today/save", json=save_payload, headers=auth_headers)
    assert save_res.status_code == 200, save_res.text
    
    # 3. Reload today
    today_res = await async_client.get(f"/today?date={today_str}", headers=auth_headers)
    assert today_res.status_code == 200
    today_data = today_res.json()
    assert len(today_data["blocks"]) > 0
    assert today_data["blocks"][0]["task_id"] is not None

    # 4. Reload tomorrow
    tomorrow_res = await async_client.get(f"/today?date={tomorrow_str}", headers=auth_headers)
    assert tomorrow_res.status_code == 200
    tomorrow_data = tomorrow_res.json()
    assert any(ut["title"] == "Deferred Task" for ut in tomorrow_data["unscheduled_tasks"])

    after_save_task_count = await db_session.scalar(select(func.count(Task.id)).where(Task.user_id == test_user.id))
    
    # 5. Idempotency test (retry)
    retry_res = await async_client.post("/today/save", json=save_payload, headers=auth_headers)
    assert retry_res.status_code == 200
    
    after_retry_task_count = await db_session.scalar(select(func.count(Task.id)).where(Task.user_id == test_user.id))
    assert after_retry_task_count == after_save_task_count
    
    # DB checks for uniqueness
    tomorrow_plan = await db_session.scalar(select(DailyPlan).where(DailyPlan.user_id == test_user.id, DailyPlan.plan_date == tomorrow_date))
    latest_rev = await db_session.scalar(
        select(PlanRevision)
        .where(PlanRevision.daily_plan_id == tomorrow_plan.id)
        .order_by(PlanRevision.revision_number.desc())
        .limit(1)
    )
    unscheduled = latest_rev.after_snapshot.get("unscheduled_tasks", [])
    deferred_matches = [u for u in unscheduled if u.get("title") == "Deferred Task"]
    assert len(deferred_matches) == 1

    # 6. Cross-user isolation
    user2_save_res = await async_client.post("/today/save", json=save_payload, headers=auth_headers_two)
    assert user2_save_res.status_code in [400, 403, 404]
    
    u2_tomorrow = await async_client.get(f"/today?date={tomorrow_str}", headers=auth_headers_two)
    assert "Deferred Task" not in str(u2_tomorrow.json())
    
@pytest.mark.asyncio
async def test_deferred_save_rollback(async_client, auth_headers, db_session, test_user, monkeypatch):
    today_str = datetime.date.today().isoformat()
    tomorrow_str = (datetime.date.today() + datetime.timedelta(days=1)).isoformat()
    
    draft_payload = {
        "type": "today",
        "planDate": today_str,
        "timezone": "UTC",
        "windows": [{"start": "09:00", "end": "12:00"}],
        "tasks": [{"id": "r1", "title": "Rollback Today", "durationMin": 30, "priority": "HIGH", "schedulingType": "FLEXIBLE", "importance": "CORE", "estimateSource": "USER", "dependencies": [], "splittable": False}],
        "deferred_tasks": [{"targetDate": tomorrow_str, "task": {"id": "r2", "title": "Rollback Tomorrow", "durationMin": 45, "priority": "MEDIUM", "schedulingType": "FLEXIBLE", "importance": "OPTIONAL", "estimateSource": "USER", "dependencies": [], "splittable": False}}]
    }

    preview_res = await async_client.post("/today/preview", json={"draft": draft_payload}, headers=auth_headers)
    preview_token = preview_res.json()["preview_token"]
    
    save_payload = {"preview_token": preview_token, "draft": draft_payload, "replace_existing": True}
    
    # Mock flush to fail on deferred task
    original_flush = db_session.flush
    async def mock_flush(*args, **kwargs):
        if hasattr(db_session, "_monkey_count"):
            db_session._monkey_count += 1
        else:
            db_session._monkey_count = 1
        if db_session._monkey_count >= 3:
            raise Exception("Forced Rollback")
        return await original_flush(*args, **kwargs)
        
    monkeypatch.setattr(db_session, "flush", mock_flush)
    
    with pytest.raises(Exception, match="Forced Rollback") as exc:
        from app.services.today_service import today_service
        from app.schemas.today import TodaySaveRequest
        req = TodaySaveRequest(**save_payload)
        await today_service.save_today_draft(db_session, test_user.id, req)
        
    # Check that transaction rolled back and no partial tasks exist
    task_exists = await db_session.scalar(select(Task).where(Task.title.in_(["Rollback Today", "Rollback Tomorrow"])))
    assert task_exists is None
