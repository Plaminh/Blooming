import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from unittest.mock import AsyncMock, MagicMock
from app.schemas.assistant import ChatResponse, QuickReply
import json
import os


@pytest_asyncio.fixture
async def client_env():
    from app.main import app
    from app.api.deps import get_db_session, get_current_user
    from app.db.models.users import User

    mock_session = AsyncMock()
    mock_session.scalar.return_value = None
    mock_session.scalars.return_value.all = MagicMock(return_value=[])

    app.dependency_overrides[get_db_session] = lambda: mock_session
    app.dependency_overrides[get_current_user] = lambda: User(
        id="00000000-0000-0000-0000-000000000000"
    )

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        yield ac, mock_session

    app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_ct_002_valid_minimal_chat_request(client_env, monkeypatch):
    ac, mock_session = client_env

    mock_chat = AsyncMock(return_value=ChatResponse(reply="I am here."))
    monkeypatch.setattr("app.services.assistant_orchestrator.chat", mock_chat)

    response = await ac.post(
        "/api/v1/assistant/chat",
        json={"message": "   hello   "},
    )
    assert response.status_code == 200, response.text

    # Prove correct dependency called exactly once
    mock_chat.assert_awaited_once()

    # Passed request has normalized message
    req_arg = mock_chat.await_args.args[0]
    assert req_arg.message == "hello"

    # Check default values are properly set by Pydantic
    assert req_arg.history == []
    assert req_arg.session_id is None

    body = response.json()
    assert body["reply"] == "I am here."
    assert "session_id" in body

    # Verify response schema strictly validates
    ChatResponse.model_validate(body)


@pytest.mark.asyncio
async def test_ct_005_empty_message(client_env, monkeypatch):
    ac, mock_session = client_env

    mock_chat = AsyncMock()
    monkeypatch.setattr("app.services.assistant_orchestrator.chat", mock_chat)

    for invalid_msg in ["", "   \n "]:
        response = await ac.post(
            "/api/v1/assistant/chat",
            json={"message": invalid_msg},
        )
        assert response.status_code == 422

        # Verify FastAPI error structure
        body = response.json()
        assert "detail" in body
        assert any(e["loc"][-1] == "message" for e in body["detail"])

        # Service mock not awaited
        mock_chat.assert_not_awaited()
        # DB mock not called
        mock_session.add.assert_not_called()


@pytest.mark.asyncio
async def test_ct_006_exactly_2000_characters(client_env, monkeypatch):
    ac, mock_session = client_env
    mock_chat = AsyncMock(return_value=ChatResponse(reply="Accepted."))
    monkeypatch.setattr("app.services.assistant_orchestrator.chat", mock_chat)

    response = await ac.post(
        "/api/v1/assistant/chat",
        json={"message": "   " + "a" * 2000 + "   "},
    )
    assert response.status_code == 200, response.text

    mock_chat.assert_awaited_once()
    request_arg = mock_chat.await_args.args[0]
    assert len(request_arg.message) == 2000
    assert request_arg.message == "a" * 2000

    assert response.json()["reply"] == "Accepted."


@pytest.mark.asyncio
async def test_ct_007_over_2000_characters(client_env, monkeypatch):
    ac, mock_session = client_env
    mock_chat = AsyncMock()
    monkeypatch.setattr("app.services.assistant_orchestrator.chat", mock_chat)

    # Note: Because whitespace is stripped first, 'a'*2001 should fail
    response = await ac.post(
        "/api/v1/assistant/chat",
        json={"message": "a" * 2001},
    )
    assert response.status_code == 422
    body = response.json()
    assert "detail" in body
    assert any(e["loc"][-1] == "message" for e in body["detail"])

    mock_chat.assert_not_awaited()
    mock_session.add.assert_not_called()


@pytest.mark.asyncio
async def test_ct_011_maximum_four_suggestions(client_env, monkeypatch):
    ac, _ = client_env

    # Test exactly 0
    mock_chat_0 = AsyncMock(return_value=ChatResponse(reply="Zero", suggestions=[]))
    monkeypatch.setattr("app.services.assistant_orchestrator.chat", mock_chat_0)
    response_0 = await ac.post("/api/v1/assistant/chat", json={"message": "hello"})
    assert response_0.status_code == 200
    assert len(response_0.json()["suggestions"]) == 0

    # Test exactly 4
    mock_chat_4 = AsyncMock(
        return_value=ChatResponse(
            reply="Four",
            suggestions=[QuickReply(label=str(i), action="a") for i in range(1, 5)],
        )
    )
    monkeypatch.setattr("app.services.assistant_orchestrator.chat", mock_chat_4)
    response_4 = await ac.post("/api/v1/assistant/chat", json={"message": "hello"})
    assert response_4.status_code == 200
    assert len(response_4.json()["suggestions"]) == 4

    # Test upstream producing 5 suggestions
    mock_chat_5 = AsyncMock(
        return_value=ChatResponse(
            reply="Five",
            suggestions=[
                QuickReply(label="1", action="action1"),
                QuickReply(label="2", action="action2"),
                QuickReply(label="3", action="action3"),
                QuickReply(label="4", action="action4"),
                QuickReply(label="5", action="action5"),
            ],
        )
    )
    monkeypatch.setattr("app.services.assistant_orchestrator.chat", mock_chat_5)

    response_5 = await ac.post(
        "/api/v1/assistant/chat",
        json={"message": "hello"},
    )
    assert response_5.status_code == 200, response_5.text
    body = response_5.json()
    assert len(body["suggestions"]) == 4
    assert body["suggestions"][0]["label"] == "1"
    assert body["suggestions"][-1]["label"] == "4"


@pytest.mark.asyncio
async def test_ct_012_suggestion_label_length(client_env, monkeypatch):
    ac, _ = client_env

    # 80 characters is accepted
    mock_chat_80 = AsyncMock(
        return_value=ChatResponse(
            reply="OK", suggestions=[QuickReply(label="a" * 80, action="action1")]
        )
    )
    monkeypatch.setattr("app.services.assistant_orchestrator.chat", mock_chat_80)
    response = await ac.post("/api/v1/assistant/chat", json={"message": "hello"})
    assert response.status_code == 200
    assert response.json()["suggestions"][0]["label"] == "a" * 80

    # 81 characters is safely truncated to 80 characters instead of crashing
    mock_chat_81 = AsyncMock(
        return_value=ChatResponse(
            reply="Truncated",
            suggestions=[QuickReply(label="a" * 81, action="action1")],
        )
    )
    monkeypatch.setattr("app.services.assistant_orchestrator.chat", mock_chat_81)
    response_81 = await ac.post("/api/v1/assistant/chat", json={"message": "hello"})
    assert response_81.status_code == 200
    assert len(response_81.json()["suggestions"][0]["label"]) == 80


@pytest.mark.asyncio
async def test_ct_015_backend_frontend_type_compatibility():
    fixture_path = os.path.join(
        os.path.dirname(__file__), "../../../contracts/chat_response_fixture.json"
    )
    with open(fixture_path, "r") as f:
        data = json.load(f)

    for item in data:
        parsed = ChatResponse.model_validate(item)
        # exclude_unset=True makes sure it matches the exact fields provided in JSON,
        # but since we want to enforce the exact contract including nulls, we use the default dump
        dumped = parsed.model_dump(mode="json", exclude_unset=True)
        # If there are any default fields that weren't in the item, they will be present in dumped
        # So we assert the explicit item matches what is dumped.
        for key in item.keys():
            assert key in dumped
            assert dumped[key] == item[key], (
                f"Mismatch in {key}: {dumped[key]} != {item[key]}"
            )
        assert dumped == item
