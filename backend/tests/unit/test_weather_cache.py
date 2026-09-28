import asyncio
from unittest.mock import AsyncMock, MagicMock, patch

import httpx
import pytest
from cachetools import TTLCache

from app.core.enums import WeatherCondition, WeatherStatus
from app.services import weather_service as service


class Clock:
    now = 0.0

    def __call__(self):
        return self.now


@pytest.fixture(autouse=True)
def timed_caches(monkeypatch):
    clock = Clock()
    monkeypatch.setattr(
        service, "_forecast_cache", TTLCache(maxsize=2, ttl=900, timer=clock)
    )
    monkeypatch.setattr(
        service, "_last_known_forecast", TTLCache(maxsize=2, ttl=7200, timer=clock)
    )
    monkeypatch.setattr(
        service, "_place_search_cache", TTLCache(maxsize=2, ttl=86400, timer=clock)
    )
    service.reset_caches()
    return clock


def response(code):
    result = MagicMock()
    result.raise_for_status.return_value = None
    result.json.return_value = {"current": {"weather_code": code}}
    return result


@pytest.mark.asyncio
async def test_forecast_ttl_stale_cutoff_and_equivalent_keys(timed_caches):
    with patch("httpx.AsyncClient.get", new_callable=AsyncMock) as get:
        get.return_value = response(61)
        first = await service.get_forecast(10.001, 20.001)
        assert first.condition == WeatherCondition.RAIN
        assert (
            await service.get_forecast(10.004, 20.004)
        ).updated_at == first.updated_at
        assert get.await_count == 1
        assert get.await_args.kwargs["params"]["latitude"] == 10.0
        timed_caches.now = 899
        await service.get_forecast(10, 20)
        assert get.await_count == 1
        timed_caches.now = 901
        get.side_effect = httpx.TimeoutException("timeout")
        stale = await service.get_forecast(10, 20)
        assert stale.status == WeatherStatus.STALE
        assert stale.condition == WeatherCondition.RAIN
        assert stale.updated_at == first.updated_at
        timed_caches.now = 7201
        assert (await service.get_forecast(10, 20)).status == WeatherStatus.UNAVAILABLE


@pytest.mark.asyncio
async def test_cache_eviction_requires_an_extra_key(timed_caches):
    with patch(
        "httpx.AsyncClient.get", new_callable=AsyncMock, return_value=response(0)
    ) as get:
        for lat in (1, 2, 3):
            await service.get_forecast(lat, 1)
        assert len(service._forecast_cache) == 2
        await service.get_forecast(1, 1)
        assert get.await_count == 4


@pytest.mark.asyncio
async def test_place_cache_expires_after_24_hours_and_evicts(timed_caches):
    provider = MagicMock()
    provider.raise_for_status.return_value = None
    provider.json.return_value = {
        "results": [{"name": "Place", "latitude": 1, "longitude": 2}]
    }
    with patch(
        "httpx.AsyncClient.get", new_callable=AsyncMock, return_value=provider
    ) as get:
        await service.search_places("one")
        await service.search_places("one")
        assert get.await_count == 1
        timed_caches.now = 86401
        await service.search_places("one")
        assert get.await_count == 2
        await service.search_places("two")
        await service.search_places("three")
        assert len(service._place_search_cache) == 2
        await service.search_places("one")
        assert get.await_count == 5


@pytest.mark.asyncio
async def test_same_key_requests_share_fetch_and_other_key_can_progress():
    entered = asyncio.Event()
    release = asyncio.Event()

    async def get(_self, _url, **kwargs):
        if kwargs["params"]["latitude"] == 1:
            entered.set()
            await release.wait()
        return response(61)

    with patch("httpx.AsyncClient.get", autospec=True, side_effect=get) as mocked:
        first = asyncio.create_task(service.get_forecast(1, 2))
        await entered.wait()
        second = asyncio.create_task(service.get_forecast(1, 2))
        other = await asyncio.wait_for(service.get_forecast(3, 2), 1)
        assert other.status == WeatherStatus.OK
        release.set()
        assert (await first).status == WeatherStatus.OK
        assert (await second).status == WeatherStatus.OK
        assert mocked.call_count == 2
