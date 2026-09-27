from uuid import uuid4
import pytest
from httpx import AsyncClient

pytestmark = pytest.mark.integration

async def test_get_goal_draft_other_user(
    async_client: AsyncClient, test_goal, auth_headers_two
):
    response = await async_client.get(
        f"/goals/{test_goal.id}/draft", headers=auth_headers_two
    )
    assert response.status_code == 404

async def test_put_goal_from_roadmap_other_user(
    async_client: AsyncClient, test_goal, auth_headers_two
):
    draft_payload = {
        "type": "roadmap",
        "goalId": str(test_goal.id),
        "goalTitle": "Hacked",
        "targetDate": "2030-01-01",
        "milestones": [
            {
                "id": str(uuid4()),
                "title": "Hacked",
                "targetDate": "2030-01-01"
            }
        ]
    }
    
    response = await async_client.put(
        f"/goals/{test_goal.id}/from-roadmap",
        json={"draft": draft_payload, "idempotency_key": "test_auth"},
        headers=auth_headers_two,
    )
    assert response.status_code == 404
