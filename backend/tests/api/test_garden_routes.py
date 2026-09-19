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
