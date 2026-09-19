import asyncio
import gc

import httpx
import pytest

from app.services import weather_service


@pytest.mark.parametrize(
    ("code", "condition"),
    [(0, "CLEAR"), (2, "CLOUDY"), (3, "OVERCAST"), (61, "RAIN"), (71, "OVERCAST"), (95, "THUNDERSTORM")],
)
def test_normalize_weather(code, condition):
    assert weather_service.normalize_weather(code) == condition


@pytest.mark.asyncio
async def test_device_coordinates_skip_city_lookup(monkeypatch):
    weather_service._weather_cache.clear()
    calls = []

    def handler(request):
        calls.append((request.url.path, request.url.params))
        return httpx.Response(200, json={"current": {"weather_code": 61}})

    actual_client = httpx.AsyncClient
    monkeypatch.setattr(
        weather_service.httpx,
        "AsyncClient",
        lambda **kwargs: actual_client(transport=httpx.MockTransport(handler)),
    )
    assert await weather_service.current_weather("10.8231,106.6297") == "RAIN"
    assert len(calls) == 1
    assert calls[0][0].endswith("/forecast")
    assert calls[0][1]["latitude"] == "10.8231"


@pytest.mark.asyncio
async def test_weather_fetches_location_and_caches_result(monkeypatch):
    weather_service._weather_cache.clear()
    weather_service._location_cache.clear()
    calls = []

    def handler(request):
        calls.append(request.url.path)
        if request.url.path.endswith("/search"):
            return httpx.Response(200, json={"results": [{"latitude": 10.8, "longitude": 106.6}]})
        return httpx.Response(200, json={"current": {"weather_code": 95}})

    actual_client = httpx.AsyncClient
    monkeypatch.setattr(
        weather_service.httpx,
        "AsyncClient",
        lambda **kwargs: actual_client(transport=httpx.MockTransport(handler)),
    )
    assert await weather_service.current_weather("Ho Chi Minh City") == "THUNDERSTORM"
    assert await weather_service.current_weather("ho chi minh city") == "THUNDERSTORM"
    assert len(calls) == 2


@pytest.mark.asyncio
async def test_provider_failure_falls_back_to_clear(monkeypatch):
    weather_service._weather_cache.clear()
    weather_service._location_cache.clear()

    def handler(request):
        raise httpx.ConnectError("offline", request=request)

    actual_client = httpx.AsyncClient
    monkeypatch.setattr(
        weather_service.httpx,
        "AsyncClient",
        lambda **kwargs: actual_client(transport=httpx.MockTransport(handler)),
    )
    assert await weather_service.current_weather("Unknown City") == "CLEAR"


@pytest.mark.asyncio
async def test_expired_weather_is_not_served_when_provider_fails(monkeypatch):
    weather_service._weather_cache.clear()
    weather_service._location_cache.clear()
    weather_service._weather_cache["old city"] = (
        weather_service.time.monotonic() - 1,
        "RAIN",
    )

    def handler(request):
        raise httpx.ConnectError("offline", request=request)

    actual_client = httpx.AsyncClient
    monkeypatch.setattr(
        weather_service.httpx,
        "AsyncClient",
        lambda **kwargs: actual_client(transport=httpx.MockTransport(handler)),
    )
    assert await weather_service.current_weather("Old City") == "CLEAR"
    assert "old city" not in weather_service._weather_cache


@pytest.mark.asyncio
async def test_different_locations_fetch_concurrently(monkeypatch):
    weather_service._weather_cache.clear()
    weather_service._location_cache.clear()
    started = set()
    both_started = asyncio.Event()

    async def handler(request):
        if request.url.path.endswith("/search"):
            started.add(request.url.params["name"])
            if len(started) == 2:
                both_started.set()
            await asyncio.wait_for(both_started.wait(), timeout=1)
            return httpx.Response(200, json={"results": [{"latitude": 10.8, "longitude": 106.6}]})
        return httpx.Response(200, json={"current": {"weather_code": 2}})

    actual_client = httpx.AsyncClient
    monkeypatch.setattr(
        weather_service.httpx,
        "AsyncClient",
        lambda **kwargs: actual_client(transport=httpx.MockTransport(handler)),
    )
    results = await asyncio.wait_for(
        asyncio.gather(
            weather_service.current_weather("City A"),
            weather_service.current_weather("City B"),
        ),
        timeout=2,
    )
    assert results == ["CLOUDY", "CLOUDY"]
    assert started == {"City A", "City B"}
    gc.collect()
    assert "city a" not in weather_service._location_locks
    assert "city b" not in weather_service._location_locks
