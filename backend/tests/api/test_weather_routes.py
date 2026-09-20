from decimal import Decimal
from unittest.mock import AsyncMock, patch

import pytest

from app.models.enums import WeatherCondition, WeatherStatus
from app.schemas.weather import WeatherResponse
from app.services.weather_service import WeatherProviderError

BASE = "/api/v1"


@pytest.mark.asyncio
async def test_search_requires_auth_and_maps_provider_errors(
    async_client, auth_headers
):
    assert (
        await async_client.get(f"{BASE}/weather/search?q=London")
    ).status_code == 401
    assert (
        await async_client.get(f"{BASE}/weather/search?q=x", headers=auth_headers)
    ).status_code == 422
    assert (
        await async_client.get(f"{BASE}/weather/search?q=%20%20", headers=auth_headers)
    ).status_code == 422
    with patch(
        "app.api.routes.weather.search_places", new_callable=AsyncMock
    ) as search:
        search.return_value = {
            "candidates": [{"name": "London, UK", "lat": 51.51, "lon": -0.13}]
        }
        result = await async_client.get(
            f"{BASE}/weather/search?q=London", headers=auth_headers
        )
        assert result.status_code == 200
        assert result.json()["candidates"][0]["name"] == "London, UK"
        await async_client.get(
            f"{BASE}/weather/search?q=Paris&lang=fr", headers=auth_headers
        )
        search.assert_awaited_with("Paris", language="fr")
        search.side_effect = WeatherProviderError("secret provider response")
        failed = await async_client.get(
            f"{BASE}/weather/search?q=Paris", headers=auth_headers
        )
        assert failed.status_code == 503
        assert "secret" not in failed.text


@pytest.mark.asyncio
async def test_current_weather_disabled_legacy_and_confirmed(
    async_client, test_user_settings, auth_headers, db_session
):
    assert (await async_client.get(f"{BASE}/weather/current")).status_code == 401
    disabled = await async_client.get(f"{BASE}/weather/current", headers=auth_headers)
    assert disabled.json()["status"] == "DISABLED"
    assert (await async_client.get(f"{BASE}/me/weather", headers=auth_headers)).json()[
        "status"
    ] == "DISABLED"
    test_user_settings.weather_enabled = True
    test_user_settings.weather_location = "Legacy text only"
    await db_session.commit()
    with patch(
        "app.api.routes.weather.get_forecast", new_callable=AsyncMock
    ) as forecast:
        legacy = await async_client.get(f"{BASE}/weather/current", headers=auth_headers)
        assert legacy.json()["status"] == "UNAVAILABLE"
        forecast.assert_not_awaited()
        test_user_settings.weather_location_name = "London"
        test_user_settings.weather_lat = Decimal("51.51")
        test_user_settings.weather_lon = Decimal("-0.13")
        await db_session.commit()
        forecast.return_value = WeatherResponse(
            condition=WeatherCondition.RAIN, status=WeatherStatus.OK
        )
        current = await async_client.get(
            f"{BASE}/weather/current", headers=auth_headers
        )
        assert current.json()["condition"] == "RAIN"
        forecast.assert_awaited_once_with(Decimal("51.51"), Decimal("-0.13"))
        forecast.return_value = WeatherResponse(
            condition=WeatherCondition.RAIN, status=WeatherStatus.STALE
        )
        stale = await async_client.get(f"{BASE}/weather/current", headers=auth_headers)
        assert stale.json()["status"] == "STALE"
        assert stale.json()["condition"] == "RAIN"


@pytest.mark.asyncio
async def test_settings_update_rounds_and_validates_location(
    async_client, test_user_settings, auth_headers
):
    url = f"{BASE}/me/settings"
    for payload in (
        {"weather_enabled": True},
        {"weather_lat": 1.234},
        {"weather_lat": 1.234, "weather_lon": 2.345},
        {"weather_location_name": " ", "weather_lat": 1, "weather_lon": 2},
        {"weather_location_name": "Place", "weather_lat": "NaN", "weather_lon": 2},
        {"scene_season": "INVALID"},
    ):
        result = await async_client.put(url, json=payload, headers=auth_headers)
        assert result.status_code == 422, payload
    saved = await async_client.put(
        url,
        json={
            "weather_enabled": True,
            "weather_location_name": "London",
            "weather_lat": 51.5074,
            "weather_lon": -0.1278,
            "scene_season": "WINTER",
        },
        headers=auth_headers,
    )
    assert saved.status_code == 200, saved.text
    assert saved.json()["weather_lat"] == 51.51
    assert saved.json()["weather_lon"] == -0.13
    assert saved.json()["scene_season"] == "WINTER"


@pytest.mark.asyncio
async def test_legacy_weather_user_can_change_unrelated_timezone(
    async_client, test_user_settings, auth_headers, db_session
):
    test_user_settings.weather_enabled = True
    test_user_settings.weather_location = "Unconfirmed legacy city"
    await db_session.commit()
    changed = await async_client.put(
        f"{BASE}/me/settings",
        json={"timezone": "Asia/Ho_Chi_Minh"},
        headers=auth_headers,
    )
    assert changed.status_code == 200
    assert changed.json()["weather_lat"] is None
    assert changed.json()["timezone"] == "Asia/Ho_Chi_Minh"
