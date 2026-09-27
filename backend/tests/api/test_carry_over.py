"""Moving today's unfinished work to tomorrow through the real API and PostgreSQL."""

import datetime

import pytest
from sqlalchemy import select

from app.db.models.tasks import Task
from tests.api.test_multi_day_recurring import _draft, _preview_and_save, _task


@pytest.mark.asyncio
async def test_unfinished_work_moves_to_tomorrow_and_comes_back_in_its_draft(
    async_client, auth_headers, db_session, test_user, test_user_settings
):
    today = datetime.datetime.now(datetime.timezone.utc).date()
    tomorrow = today + datetime.timedelta(days=1)
    await _preview_and_save(
        async_client, auth_headers, _draft(today, [_task("d1", "Đã làm"), _task("d2", "Chưa làm")])
    )
    done = await db_session.scalar(select(Task).where(Task.title == "Đã làm"))
    completed = await async_client.patch(
        f"/api/v1/today/tasks/{done.id}/status", json={"status": "COMPLETED"}, headers=auth_headers
    )
    assert completed.status_code == 200, completed.text

    moved = await async_client.post(
        "/api/v1/assistant/actions/CARRY_OVER_UNFINISHED", json={}, headers=auth_headers
    )
    assert moved.status_code == 200, moved.text
    assert moved.json()["target_date"] == tomorrow.isoformat()
    assert [item["title"] for item in moved.json()["moved"]] == ["Chưa làm"]

    open_task = await db_session.scalar(select(Task).where(Task.title == "Chưa làm"))
    await db_session.refresh(open_task)
    assert (open_task.status, open_task.planned_date) == ("PENDING", tomorrow)

    upcoming = await async_client.get(f"/api/v1/today?date={tomorrow}", headers=auth_headers)
    assert [item["title"] for item in upcoming.json()["pending_tasks"]] == ["Chưa làm"]

    # Running it again has nothing left to move.
    again = await async_client.post(
        "/api/v1/assistant/actions/CARRY_OVER_UNFINISHED", json={}, headers=auth_headers
    )
    assert again.json()["moved"] == []


@pytest.mark.asyncio
async def test_carry_over_without_a_plan_is_a_no_op(async_client, auth_headers, test_user_settings):
    response = await async_client.post(
        "/api/v1/assistant/actions/CARRY_OVER_UNFINISHED", json={}, headers=auth_headers
    )
    assert response.status_code == 200
    assert response.json()["moved"] == []
