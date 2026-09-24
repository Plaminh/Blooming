"""Multi-day and recurring work through the real API and PostgreSQL."""

import datetime

import pytest
from sqlalchemy import func, select

from app.db.models.daily_plans import PlanBlock
from app.db.models.tasks import RecurringTask, Task


def _task(task_id: str, title: str, minutes: int = 30, **extra) -> dict:
    return {
        "id": task_id,
        "title": title,
        "durationMin": minutes,
        "priority": "MEDIUM",
        "schedulingType": "FLEXIBLE",
        "importance": "CORE",
        "estimateSource": "USER",
        "dependencies": [],
        "splittable": False,
        **extra,
    }


def _draft(plan_date: datetime.date, tasks: list[dict], deferred: list[dict] | None = None) -> dict:
    return {
        "type": "today",
        "planDate": plan_date.isoformat(),
        "timezone": "UTC",
        "windows": [{"start": "09:00", "end": "12:00"}],
        "tasks": tasks,
        "deferred_tasks": deferred or [],
    }


async def _preview_and_save(client, headers, draft: dict, replace: bool = False):
    preview = await client.post("/api/v1/today/preview", json={"draft": draft}, headers=headers)
    assert preview.status_code == 200, preview.text
    saved = await client.post(
        "/api/v1/today/save",
        json={
            "preview_token": preview.json()["preview_token"],
            "draft": draft,
            "replace_existing": replace,
        },
        headers=headers,
    )
    assert saved.status_code == 200, saved.text
    return saved


@pytest.mark.asyncio
async def test_recurring_task_creates_one_template_and_returns_on_its_days(
    async_client, auth_headers, db_session, test_user, test_user_settings
):
    today = datetime.datetime.now(datetime.timezone.utc).date()
    tomorrow = today + datetime.timedelta(days=1)
    draft = _draft(today, [_task("d1", "Học tiếng Anh", recurrence={"freq": "DAILY"})])
    await _preview_and_save(async_client, auth_headers, draft)

    templates = (
        await db_session.scalars(select(RecurringTask).where(RecurringTask.user_id == test_user.id))
    ).all()
    assert [(item.title, item.frequency, item.start_date) for item in templates] == [
        ("Học tiếng Anh", "DAILY", today)
    ]
    occurrence = await db_session.scalar(select(Task).where(Task.user_id == test_user.id))
    assert occurrence.recurring_task_id == templates[0].id
    assert occurrence.planned_date == today

    listed = await async_client.get("/api/v1/recurring-tasks", headers=auth_headers)
    assert [item["title"] for item in listed.json()] == ["Học tiếng Anh"]

    upcoming = await async_client.get(f"/api/v1/today?date={tomorrow}", headers=auth_headers)
    assert [(item["title"], item["reason"]) for item in upcoming.json()["pending_tasks"]] == [
        ("Học tiếng Anh", "RECURRING")
    ]

    # Replacing today's plan with the same repeating task must not make it
    # appear twice on every later day.
    replaced = _draft(
        today,
        [_task("d1", "Học tiếng Anh", recurrence={"freq": "DAILY"}), _task("d2", "Đọc sách")],
    )
    await _preview_and_save(async_client, auth_headers, replaced, replace=True)
    count = await db_session.scalar(
        select(func.count(RecurringTask.id)).where(RecurringTask.user_id == test_user.id)
    )
    assert count == 1

    stopped = await async_client.patch(
        f"/api/v1/recurring-tasks/{templates[0].id}", json={"is_active": False}, headers=auth_headers
    )
    assert stopped.status_code == 200
    upcoming = await async_client.get(f"/api/v1/today?date={tomorrow}", headers=auth_headers)
    assert upcoming.json()["pending_tasks"] == []


@pytest.mark.asyncio
async def test_planning_a_later_day_reuses_the_deferred_task(
    async_client, auth_headers, db_session, test_user, test_user_settings
):
    today = datetime.datetime.now(datetime.timezone.utc).date()
    tomorrow = today + datetime.timedelta(days=1)
    first = _draft(
        today,
        [_task("d1", "Họp nhóm")],
        deferred=[{"targetDate": tomorrow.isoformat(), "task": _task("d2", "Viết báo cáo", 60)}],
    )
    await _preview_and_save(async_client, auth_headers, first)
    deferred = await db_session.scalar(select(Task).where(Task.title == "Viết báo cáo"))
    assert deferred.planned_date == tomorrow and deferred.status == "PENDING"
    before = await db_session.scalar(select(func.count(Task.id)).where(Task.user_id == test_user.id))

    second = _draft(tomorrow, [_task("d1", "Viết báo cáo", 60, sourceTaskId=str(deferred.id))])
    await _preview_and_save(async_client, auth_headers, second)

    after = await db_session.scalar(select(func.count(Task.id)).where(Task.user_id == test_user.id))
    assert after == before  # reused, not duplicated
    scheduled = await db_session.scalar(
        select(func.count(PlanBlock.id)).where(PlanBlock.task_id == deferred.id)
    )
    assert scheduled >= 1


@pytest.mark.asyncio
async def test_another_users_task_id_is_never_reused(
    async_client, auth_headers, auth_headers_two, db_session, test_user, test_user_settings
):
    today = datetime.datetime.now(datetime.timezone.utc).date()
    tomorrow = today + datetime.timedelta(days=1)
    first = _draft(
        today,
        [_task("d1", "Họp nhóm")],
        deferred=[{"targetDate": tomorrow.isoformat(), "task": _task("d2", "Riêng tư", 60)}],
    )
    await _preview_and_save(async_client, auth_headers, first)
    private = await db_session.scalar(select(Task).where(Task.title == "Riêng tư"))

    stolen = _draft(tomorrow, [_task("d1", "Đổi tên", 30, sourceTaskId=str(private.id))])
    await _preview_and_save(async_client, auth_headers_two, stolen)
    await db_session.refresh(private)
    assert private.title == "Riêng tư"
    assert private.user_id == test_user.id


@pytest.mark.asyncio
async def test_replanning_twice_after_unscheduled_work_does_not_fail(
    async_client, auth_headers, test_user_settings
):
    today = datetime.datetime.now(datetime.timezone.utc).date()
    # Far more work than the window holds, so replans leave tasks unscheduled.
    overloaded = _draft(today, [_task("d1", "Việc lớn A", 240), _task("d2", "Việc lớn B", 240)])
    await _preview_and_save(async_client, auth_headers, overloaded)
    for _ in range(2):
        response = await async_client.post("/api/v1/today/replan", headers=auth_headers)
        assert response.status_code == 200, response.text
