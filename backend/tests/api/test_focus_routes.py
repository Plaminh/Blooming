from unittest.mock import AsyncMock
from uuid import UUID, uuid4

import pytest
from app.db.models.focus import FocusRun, FocusRunEvent
from app.db.models.garden import GardenState, RewardEvent
from app.db.models.daily_plans import PlanRevision
from app.core.economy import WATER_PER_POMODORO
from app.services.focus_service import focus_service
from sqlalchemy import select

pytestmark = pytest.mark.integration
PREFIX = "/api/v1/focus"


def assert_error(response, status, detail):
    assert response.status_code == status, response.text
    assert response.json() == {"detail": detail}


async def test_focus_routes_lifecycle_and_db_override(
    async_client, db_session, auth_headers, test_task
):
    response = await async_client.post(
        f"{PREFIX}/start",
        json={"task_id": str(test_task.id), "planned_focus_seconds": 1500},
        headers=auth_headers,
    )
    assert response.status_code == 200, response.text
    data = response.json()
    assert data["status"] == "FOCUSING"
    run = (await db_session.scalars(select(FocusRun))).one()
    assert str(run.id) == data["id"]
    assert run.task_id == test_task.id
    for action, expected in (("pause", "PAUSED"), ("resume", "FOCUSING")):
        result = await async_client.post(f"{PREFIX}/{action}", headers=auth_headers)
        assert result.status_code == 200, result.text
        assert result.json()["status"] == expected
    result = await async_client.post(
        f"{PREFIX}/finish",
        json={"run_id": data["id"], "outcome": "DONE"},
        headers=auth_headers,
    )
    assert result.status_code == 200, result.text
    assert (result.json()["status"], result.json()["outcome"]) == ("ENDED", "DONE")
    await db_session.refresh(run)
    assert run.status == "ENDED"


async def test_duplicate_finish_http_flow_rewards_and_ends_once(
    async_client, db_session, auth_headers, test_task, test_plan_block,
    test_availability_window,
):
    started = await async_client.post(
        f"{PREFIX}/start",
        json={"task_id": str(test_task.id), "planned_focus_seconds": 1500},
        headers=auth_headers,
    )
    payload = {
        "run_id": started.json()["id"],
        "outcome": "DONE",
        "should_replan": True,
    }
    first = await async_client.post(f"{PREFIX}/finish", json=payload, headers=auth_headers)
    second = await async_client.post(f"{PREFIX}/finish", json=payload, headers=auth_headers)
    assert first.status_code == second.status_code == 200
    assert len((await db_session.scalars(select(RewardEvent))).all()) == 1
    assert len((await db_session.scalars(
        select(FocusRunEvent).where(FocusRunEvent.event_type == "ENDED")
    )).all()) == 1
    run = await db_session.get(FocusRun, UUID(started.json()["id"]))
    assert run is not None and run.status == "ENDED"
    assert len((await db_session.scalars(select(PlanRevision))).all()) <= 1
    garden = await db_session.get(GardenState, test_task.user_id)
    assert garden is not None and garden.water_balance == WATER_PER_POMODORO


@pytest.mark.parametrize(
    "route,payload,field,error_type",
    [
        (
            "start",
            {"planned_focus_seconds": "not_an_int"},
            "planned_focus_seconds",
            "int_parsing",
        ),
        (
            "start",
            {"planned_focus_seconds": 0},
            "planned_focus_seconds",
            "greater_than_equal",
        ),
        ("finish", {"outcome": "COMPLETED"}, "outcome", "literal_error"),
    ],
)
async def test_focus_validation_schema(
    async_client, auth_headers, route, payload, field, error_type
):
    response = await async_client.post(
        f"{PREFIX}/{route}", json=payload, headers=auth_headers
    )
    assert response.status_code == 422, response.text
    body = response.json()
    assert set(body) == {"detail"}
    assert len(body["detail"]) == 1
    error = body["detail"][0]
    assert error["loc"] == ["body", field]
    assert error["type"] == error_type
    assert isinstance(error["msg"], str)


async def test_focus_routes_auth_failure(async_client):
    response = await async_client.post(
        f"{PREFIX}/start", json={"planned_focus_seconds": 1500}
    )
    assert_error(response, 401, "Not authenticated")
    assert response.headers["www-authenticate"] == "Bearer"


async def test_focus_routes_state_conflict(async_client, auth_headers):
    payload = {"planned_focus_seconds": 1500, "quick_task_title": "Read a chapter"}
    first = await async_client.post(
        f"{PREFIX}/start", json=payload, headers=auth_headers
    )
    assert first.status_code == 200
    response = await async_client.post(
        f"{PREFIX}/start", json=payload, headers=auth_headers
    )
    assert_error(
        response,
        409,
        {
            "code": "INVALID_STATUS_TRANSITION",
            "message": "An active focus session already exists",
        },
    )


async def test_focus_routes_not_found(async_client, auth_headers):
    response = await async_client.post(
        f"{PREFIX}/finish",
        json={"run_id": str(uuid4()), "outcome": "DONE"},
        headers=auth_headers,
    )
    assert_error(
        response,
        404,
        {"code": "RESOURCE_NOT_FOUND", "message": "No active focus session to finish"},
    )


async def test_focus_routes_cross_user(
    async_client, db_session, auth_headers, auth_headers_two, test_task
):
    first = await async_client.post(
        f"{PREFIX}/start",
        json={"task_id": str(test_task.id), "planned_focus_seconds": 1500},
        headers=auth_headers,
    )
    assert first.status_code == 200
    response = await async_client.post(
        f"{PREFIX}/finish",
        json={"run_id": first.json()["id"], "outcome": "DONE"},
        headers=auth_headers_two,
    )
    assert_error(
        response,
        404,
        {"code": "RESOURCE_NOT_FOUND", "message": "No active focus session to finish"},
    )
    run = (await db_session.scalars(select(FocusRun))).one()
    assert run.status == "FOCUSING"


async def test_internal_error_does_not_leak_details(
    async_client, auth_headers, monkeypatch
):
    spy = AsyncMock(
        side_effect=RuntimeError(
            "SELECT password FROM users; secret-token; postgres://private"
        )
    )
    monkeypatch.setattr(focus_service, "start_session", spy)
    response = await async_client.post(
        f"{PREFIX}/start", json={"planned_focus_seconds": 1500}, headers=auth_headers
    )
    spy.assert_awaited_once()
    assert_error(response, 500, "Internal server error")
