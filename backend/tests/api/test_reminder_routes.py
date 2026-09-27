from unittest.mock import AsyncMock
from uuid import uuid4

import pytest
from app.db.models.daily_plans import DailyPlan
from app.db.models.reminders import Reminder, ReminderAction
from app.services.reminders_service import reminders_service
from sqlalchemy import select
from tests.api.test_focus_routes import assert_error

pytestmark = pytest.mark.integration
PREFIX = "/api/v1/reminders"


async def test_reminder_routes_valid_request_and_db_override(
    async_client, db_session, auth_headers, test_reminder
):
    reminder_id = test_reminder.id
    response = await async_client.post(
        f"{PREFIX}/{reminder_id}/actions",
        json={"action_type": "MARK_COMPLETED"},
        headers=auth_headers,
    )
    assert response.status_code == 200, response.text
    assert response.json()["status"] == "COMPLETED"
    assert response.json()["id"] == str(reminder_id)
    db_session.expire_all()
    assert (await db_session.get(Reminder, reminder_id)).status == "COMPLETED"
    actions = (await db_session.scalars(select(ReminderAction))).all()
    assert [(a.reminder_id, a.action_type) for a in actions] == [
        (reminder_id, "MARK_COMPLETED")
    ]


async def test_reminder_routes_auth_failure(async_client, test_reminder):
    response = await async_client.post(
        f"{PREFIX}/{test_reminder.id}/actions", json={"action_type": "MARK_COMPLETED"}
    )
    assert_error(response, 401, "Not authenticated")
    assert response.headers["www-authenticate"] == "Bearer"


async def test_reminder_routes_semantic_validation_and_rollback(
    async_client, db_session, auth_headers, test_reminder
):
    reminder_id = test_reminder.id
    response = await async_client.post(
        f"{PREFIX}/{reminder_id}/actions",
        json={"action_type": "REMIND_LATER"},
        headers=auth_headers,
    )
    assert response.status_code == 422
    assert "REMIND_LATER requires new_due_at" in response.text
    assert (await db_session.scalars(select(ReminderAction))).all() == []
    assert (await db_session.get(Reminder, reminder_id)).status == "SCHEDULED"


async def test_reminder_routes_validation_schema(
    async_client, auth_headers, test_reminder
):
    response = await async_client.post(
        f"{PREFIX}/{test_reminder.id}/actions", json={}, headers=auth_headers
    )
    assert response.status_code == 422
    assert set(response.json()) == {"detail"}
    errors = response.json()["detail"]
    assert len(errors) == 1
    assert errors[0]["loc"] == ["body", "action_type"]
    assert errors[0]["type"] == "missing"
    assert isinstance(errors[0]["msg"], str)


async def test_reminder_routes_not_found(async_client, auth_headers):
    response = await async_client.post(
        f"{PREFIX}/{uuid4()}/actions",
        json={"action_type": "MARK_COMPLETED"},
        headers=auth_headers,
    )
    assert_error(
        response, 404, {"code": "RESOURCE_NOT_FOUND", "message": "Reminder not found"}
    )


async def test_reminder_routes_cross_user(
    async_client, db_session, auth_headers_two, test_reminder
):
    reminder_id = test_reminder.id
    response = await async_client.post(
        f"{PREFIX}/{reminder_id}/actions",
        json={"action_type": "MARK_COMPLETED"},
        headers=auth_headers_two,
    )
    assert_error(
        response, 404, {"code": "RESOURCE_NOT_FOUND", "message": "Reminder not found"}
    )
    assert (await db_session.get(Reminder, reminder_id)).status == "SCHEDULED"
    assert (await db_session.scalars(select(ReminderAction))).all() == []


async def test_create_plan_existing_active_is_idempotent_success(
    async_client, db_session, auth_headers, test_reminder, test_daily_plan, clock
):
    for _ in range(2):
        response = await async_client.post(
            f"{PREFIX}/{test_reminder.id}/actions",
            json={"action_type": "CREATE_PLAN"},
            headers=auth_headers,
        )
        assert response.status_code == 200, response.text
        assert response.json()["status"] == "COMPLETED"
    assert len((await db_session.scalars(select(DailyPlan))).all()) == 1
    assert len((await db_session.scalars(select(ReminderAction))).all()) == 1


async def test_internal_error_does_not_leak_details(
    async_client, auth_headers, test_reminder, monkeypatch
):
    spy = AsyncMock(
        side_effect=RuntimeError("SELECT secret FROM users; postgres://private")
    )
    monkeypatch.setattr(reminders_service, "execute_action", spy)
    response = await async_client.post(
        f"{PREFIX}/{test_reminder.id}/actions",
        json={"action_type": "MARK_COMPLETED"},
        headers=auth_headers,
    )
    spy.assert_awaited_once()
    assert_error(response, 500, "Internal server error")
