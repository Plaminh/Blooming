from unittest.mock import AsyncMock, Mock

import pytest

from app import main


@pytest.mark.asyncio
async def test_lifespan_closes_shared_provider_on_shutdown(monkeypatch):
    init_client = Mock()
    close_client = AsyncMock()
    dispose = AsyncMock()
    monkeypatch.setattr(main.llm_provider, "init_client", init_client)
    monkeypatch.setattr(main.llm_provider, "close_client", close_client)
    monkeypatch.setattr(main, "engine", Mock(dispose=dispose))
    async with main.lifespan(main.app):
        init_client.assert_called_once()
    close_client.assert_awaited_once()
    dispose.assert_awaited_once()
