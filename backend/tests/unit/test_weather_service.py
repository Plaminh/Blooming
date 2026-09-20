from unittest.mock import AsyncMock, MagicMock, patch

import httpx
import pytest

from app.models.enums import WeatherCondition, WeatherStatus
from app.services.weather_service import (
    WeatherProviderError,
    _forecast_cache,
    _last_known_forecast,
    _place_search_cache,
    get_forecast,
    normalize_weather,
    search_places,
)


@pytest.mark.asyncio
async def test_place_search_filters_malformed_candidates_and_caps_at_five():
    _place_search_cache.clear()
    items = [
        {"name": "Missing latitude", "longitude": 1},
        {"name": "Missing longitude", "latitude": 1},
        {"name": " ", "latitude": 1, "longitude": 2},
        {"name": "Invalid", "latitude": float("nan"), "longitude": 2},
        *(
            {"name": f"City {index}", "latitude": 10.123, "longitude": 20.456}
            for index in range(7)
        ),
    ]
    provider = MagicMock()
    provider.raise_for_status.return_value = None
    provider.json.return_value = {"results": items}
    with patch("httpx.AsyncClient.get", new_callable=AsyncMock, return_value=provider):
        found = await search_places("Cities")
    assert len(found.candidates) == 5
    assert all(place.name.startswith("City") for place in found.candidates)
    assert all((place.lat, place.lon) == (10.12, 20.46) for place in found.candidates)


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "payload", [None, [], {}, {"results": None}, {"results": "wrong"}]
)
async def test_malformed_place_payload_is_an_explicit_error(payload):
    _place_search_cache.clear()
    provider = MagicMock()
    provider.raise_for_status.return_value = None
    provider.json.return_value = payload
    with (
        patch("httpx.AsyncClient.get", new_callable=AsyncMock, return_value=provider),
        pytest.raises(WeatherProviderError),
    ):
        await search_places("Example")


@pytest.mark.asyncio
async def test_empty_place_results_are_valid():
    _place_search_cache.clear()
    provider = MagicMock()
    provider.raise_for_status.return_value = None
    provider.json.return_value = {"results": []}
    with patch("httpx.AsyncClient.get", new_callable=AsyncMock, return_value=provider):
        assert (await search_places("Missing")).candidates == []
    assert (await search_places(" ")).candidates == []


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "payload", [{"current": {"weather_code": 999}}, {"current": {}}, [], None]
)
async def test_bad_forecast_never_becomes_successful_clear(payload):
    _forecast_cache.clear()
    _last_known_forecast.clear()
    provider = MagicMock()
    provider.raise_for_status.return_value = None
    provider.json.return_value = payload
    with patch("httpx.AsyncClient.get", new_callable=AsyncMock, return_value=provider):
        result = await get_forecast(44, 55)
    assert result.status == WeatherStatus.UNAVAILABLE
    assert (44, 55) not in _forecast_cache


def test_normalize_weather_mapping():
    assert normalize_weather(0) == WeatherCondition.CLEAR
    assert normalize_weather(2) == WeatherCondition.CLOUDY
    assert normalize_weather(3) == WeatherCondition.OVERCAST
    assert normalize_weather(51) == WeatherCondition.RAIN
    assert normalize_weather(95) == WeatherCondition.THUNDERSTORM

    with pytest.raises(ValueError):
        normalize_weather(999)


@pytest.mark.asyncio
@patch("httpx.AsyncClient.get")
async def test_get_forecast_rounding(mock_get):
    _forecast_cache.clear()

    mock_resp_success = MagicMock()
    mock_resp_success.json.return_value = {"current": {"weather_code": 0}}
    mock_resp_success.raise_for_status = lambda: None

    mock_get.return_value = mock_resp_success

    res1 = await get_forecast(51.507, -0.128)
    assert res1.status == WeatherStatus.OK

    # Mock failure
    mock_resp_fail = MagicMock()
    mock_resp_fail.raise_for_status.side_effect = httpx.HTTPError("error")
    mock_get.return_value = mock_resp_fail

    res2 = await get_forecast(51.511, -0.134)
    assert res2.status == WeatherStatus.OK


@pytest.mark.asyncio
@patch("httpx.AsyncClient.get")
async def test_get_forecast_stale_fallback(mock_get):
    _forecast_cache.clear()
    _last_known_forecast.clear()

    mock_resp_success = MagicMock()
    mock_resp_success.json.return_value = {"current": {"weather_code": 51}}
    mock_resp_success.raise_for_status = lambda: None
    mock_get.return_value = mock_resp_success

    res1 = await get_forecast(10.0, 20.0)
    assert res1.status == WeatherStatus.OK
    assert res1.condition == WeatherCondition.RAIN

    _forecast_cache.clear()

    mock_resp_fail = MagicMock()
    mock_resp_fail.raise_for_status.side_effect = httpx.HTTPError("error")
    mock_get.return_value = mock_resp_fail

    res2 = await get_forecast(10.0, 20.0)
    assert res2.status == WeatherStatus.STALE
    assert res2.condition == WeatherCondition.RAIN

    _last_known_forecast.clear()
    res3 = await get_forecast(10.0, 20.0)
    assert res3.status == WeatherStatus.UNAVAILABLE


@pytest.mark.asyncio
@patch("httpx.AsyncClient.get")
async def test_search_places_provider_error(mock_get):
    _place_search_cache.clear()

    mock_resp_fail = MagicMock()
    mock_resp_fail.raise_for_status.side_effect = httpx.HTTPStatusError(
        "429", request=None, response=None
    )
    mock_get.return_value = mock_resp_fail

    with pytest.raises(WeatherProviderError):
        await search_places("London")
