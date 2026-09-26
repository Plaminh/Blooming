from uuid import uuid4
import pytest
from httpx import AsyncClient

pytestmark = pytest.mark.integration

async def test_get_goal_draft_other_user(
    api_client: AsyncClient, test_goal, test_user_two_token
):
    response = await api_client.get(
        f"/goals/{test_goal.id}/draft", headers={"Authorization": f"Bearer {test_user_two_token}"}
    )
    assert response.status_code == 404

async def test_put_goal_from_roadmap_other_user(
    api_client: AsyncClient, test_goal, test_user_two_token
):
    draft_payload = {
        "type": "roadmap",
        "goalId": str(test_goal.id),
        "goalTitle": "Hacked",
        "targetDate": "2030-01-01",
        "milestones": [
            {
                "id": str(test_goal.milestones[0].id),
                "title": "Hacked",
                "targetDate": "2030-01-01"
            }
        ]
    }
    
    response = await api_client.put(
        f"/goals/{test_goal.id}/from-roadmap",
        json={"draft": draft_payload, "idempotency_key": "test_auth"},
        headers={"Authorization": f"Bearer {test_user_two_token}"},
    )
    assert response.status_code == 404

