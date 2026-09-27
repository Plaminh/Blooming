import pytest

pytestmark = pytest.mark.integration


async def test_catalog_free_unlock_select_and_leaf_requirement(async_client, auth_headers):
    response = await async_client.get("/api/v1/garden", headers=auth_headers)
    assert response.status_code == 200, response.text
    catalog = {plant["species"]: plant for plant in response.json()["catalog"]}
    assert set(catalog) == {"monstera", "sunflower", "bonsai", "jasmine", "lavender"}
    assert catalog["monstera"]["unlock_cost"] == 0
    assert response.json()["leaves_balance"] == 0
    assert response.json()["selected_plant_id"] == catalog["monstera"]["id"]
    assert catalog["monstera"]["is_unlocked"]

    monstera_id = catalog["monstera"]["id"]
    response = await async_client.post(
        f"/api/v1/garden/plants/{monstera_id}/unlock", headers=auth_headers
    )
    assert response.status_code == 200, response.text
    assert response.json()["leaves_balance"] == 0
    assert next(p for p in response.json()["catalog"] if p["id"] == monstera_id)[
        "is_unlocked"
    ]

    response = await async_client.post(
        f"/api/v1/garden/plants/{monstera_id}/select", headers=auth_headers
    )
    assert response.status_code == 200, response.text
    assert response.json()["selected_plant_id"] == monstera_id

    sunflower_id = catalog["sunflower"]["id"]
    response = await async_client.post(
        f"/api/v1/garden/plants/{sunflower_id}/unlock", headers=auth_headers
    )
    assert response.status_code == 409, response.text
    assert response.json()["detail"]["code"] == "INSUFFICIENT_LEAVES"
    assert response.json()["detail"]["required"] == catalog["sunflower"]["unlock_cost"]


async def test_water_plant_api_idempotency(async_client, auth_headers, test_user, db_session):
    from app.services import garden_service
    import uuid
    garden, _ = await garden_service._ensure_garden_state(db_session, test_user.id)
    garden.water_balance = 10
    
    from app.db.models.garden import Plant
    from sqlalchemy import select
    plant = await db_session.scalar(select(Plant).limit(1))
    garden.selected_plant_id = plant.id
    await db_session.commit()

    key1 = str(uuid.uuid4())
    key2 = str(uuid.uuid4())

    # Call water API
    response = await async_client.post(
        "/api/v1/garden/water",
        json={"operation_key": key1},
        headers=auth_headers
    )
    assert response.status_code == 200, response.text
    assert response.json()["water_balance"] == 9

    # Call with same key
    response2 = await async_client.post(
        "/api/v1/garden/water",
        json={"operation_key": key1},
        headers=auth_headers
    )
    assert response2.status_code == 200, response2.text
    assert response2.json()["water_balance"] == 9

    # Call with new key
    response3 = await async_client.post(
        "/api/v1/garden/water",
        json={"operation_key": key2},
        headers=auth_headers
    )
    assert response3.status_code == 200, response3.text
    assert response3.json()["water_balance"] == 8

    # Ensure missing key is 422
    response4 = await async_client.post(
        "/api/v1/garden/water",
        json={},
        headers=auth_headers
    )
    assert response4.status_code == 422

    # Ensure malformed key is 422
    response5 = await async_client.post(
        "/api/v1/garden/water",
        json={"operation_key": "not-a-uuid"},
        headers=auth_headers
    )
    assert response5.status_code == 422
