from types import SimpleNamespace
from unittest.mock import AsyncMock

import pytest

from app.api.routes import weather


@pytest.mark.asyncio
async def test_weather_route_uses_saved_location(monkeypatch):
    settings = SimpleNamespace(weather_enabled=True, weather_location="Ho Chi Minh City")
    fetch_settings = AsyncMock(return_value=settings)
    fetch_weather = AsyncMock(return_value="RAIN")
    monkeypatch.setattr(weather, "get_user_settings", fetch_settings)
    monkeypatch.setattr(weather, "current_weather", fetch_weather)

    user = SimpleNamespace(id="user-id")
    assert await weather.read_weather(object(), user) == {"condition": "RAIN"}
    fetch_settings.assert_awaited_once()
    fetch_weather.assert_awaited_once_with("Ho Chi Minh City")


@pytest.mark.asyncio
async def test_weather_route_skips_provider_when_disabled(monkeypatch):
    settings = SimpleNamespace(weather_enabled=False, weather_location="Ho Chi Minh City")
    fetch_weather = AsyncMock()
    monkeypatch.setattr(weather, "get_user_settings", AsyncMock(return_value=settings))
    monkeypatch.setattr(weather, "current_weather", fetch_weather)

    assert await weather.read_weather(object(), SimpleNamespace(id="user-id")) == {"condition": "CLEAR"}
    fetch_weather.assert_not_awaited()


@pytest.mark.asyncio
async def test_weather_route_skips_provider_without_location(monkeypatch):
    settings = SimpleNamespace(weather_enabled=True, weather_location=None)
    fetch_weather = AsyncMock()
    monkeypatch.setattr(weather, "get_user_settings", AsyncMock(return_value=settings))
    monkeypatch.setattr(weather, "current_weather", fetch_weather)

    assert await weather.read_weather(object(), SimpleNamespace(id="user-id")) == {"condition": "CLEAR"}
    fetch_weather.assert_not_awaited()
