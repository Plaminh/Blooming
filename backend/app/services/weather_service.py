"""Bounded Open-Meteo calls using approximate coordinates only."""

import asyncio
import math
from datetime import datetime, timezone

import httpx
from cachetools import TTLCache

from app.core.enums import WeatherCondition, WeatherStatus
from app.schemas.weather import PlaceCandidate, PlaceSearchResponse, WeatherResponse

GEOCODING_URL = "https://geocoding-api.open-meteo.com/v1/search"
FORECAST_URL = "https://api.open-meteo.com/v1/forecast"
WEATHER_TTL_SECONDS = 900
LOCATION_TTL_SECONDS = 86400
STALE_CUTOFF_SECONDS = 7200
_place_search_cache = TTLCache(maxsize=1000, ttl=LOCATION_TTL_SECONDS)
_forecast_cache = TTLCache(maxsize=100, ttl=WEATHER_TTL_SECONDS)
_last_known_forecast = TTLCache(maxsize=100, ttl=STALE_CUTOFF_SECONDS)
_forecast_inflight: dict[tuple[float, float], asyncio.Task[WeatherResponse]] = {}


class WeatherProviderError(Exception):
    """Expected weather-provider failure."""


def reset_caches() -> None:
    _place_search_cache.clear()
    _forecast_cache.clear()
    _last_known_forecast.clear()
    _forecast_inflight.clear()


def normalize_weather(code: int) -> WeatherCondition:
    if type(code) is not int:
        raise ValueError("Invalid WMO code")
    if code in (95, 96, 99):
        return WeatherCondition.THUNDERSTORM
    if code in (51, 53, 55, 56, 57, 61, 63, 65, 66, 67, 80, 81, 82):
        return WeatherCondition.RAIN
    if code in (3, 45, 48, 71, 73, 75, 77, 85, 86):
        return WeatherCondition.OVERCAST
    if code == 2:
        return WeatherCondition.CLOUDY
    if code in (0, 1):
        return WeatherCondition.CLEAR
    raise ValueError("Unknown WMO code")


def _candidate(item: object) -> PlaceCandidate | None:
    if not isinstance(item, dict):
        return None
    name = item.get("name")
    lat, lon = item.get("latitude"), item.get("longitude")
    if not isinstance(name, str) or not name.strip():
        return None
    if isinstance(lat, bool) or isinstance(lon, bool):
        return None
    if not isinstance(lat, (int, float)) or not isinstance(lon, (int, float)):
        return None
    if (
        not math.isfinite(lat)
        or not math.isfinite(lon)
        or not -90 <= lat <= 90
        or not -180 <= lon <= 180
    ):
        return None
    parts = [name.strip()]
    for key in ("admin1", "country"):
        part = item.get(key)
        if isinstance(part, str) and part.strip() and part.strip() not in parts:
            parts.append(part.strip())
    display = ", ".join(parts)
    return (
        PlaceCandidate(name=display, lat=round(lat, 2), lon=round(lon, 2))
        if len(display) <= 255
        else None
    )


async def search_places(query: str, language: str = "en") -> PlaceSearchResponse:
    query = query.strip()
    if len(query) < 2:
        return PlaceSearchResponse(candidates=[])
    key = f"{query.casefold()}:{language}"
    if key in _place_search_cache:
        return _place_search_cache[key]
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.get(
                GEOCODING_URL,
                params={
                    "name": query,
                    "count": 20,
                    "language": language,
                    "format": "json",
                },
            )
            response.raise_for_status()
            data = response.json()
        if not isinstance(data, dict) or not isinstance(data.get("results"), list):
            raise WeatherProviderError("Malformed place response")
        candidates = []
        for item in data["results"]:
            candidate = _candidate(item)
            if candidate is not None:
                candidates.append(candidate)
            if len(candidates) == 5:
                break
        result = PlaceSearchResponse(candidates=candidates)
        _place_search_cache[key] = result
        return result
    except (httpx.HTTPError, ValueError, TypeError, KeyError) as exc:
        raise WeatherProviderError("Place provider unavailable") from exc


def _fallback(key: tuple[float, float]) -> WeatherResponse:
    previous = _last_known_forecast.get(key)
    if previous:
        return WeatherResponse(
            condition=previous[0], status=WeatherStatus.STALE, updated_at=previous[1]
        )
    return WeatherResponse(
        condition=WeatherCondition.CLEAR, status=WeatherStatus.UNAVAILABLE
    )


async def get_forecast(lat: float, lon: float) -> WeatherResponse:
    if (
        not math.isfinite(lat)
        or not math.isfinite(lon)
        or not -90 <= lat <= 90
        or not -180 <= lon <= 180
    ):
        raise ValueError("Invalid coordinates")
    key = (round(lat, 2), round(lon, 2))
    cached = _forecast_cache.get(key)
    if cached:
        return WeatherResponse(
            condition=cached[0], status=WeatherStatus.OK, updated_at=cached[1]
        )
    task = _forecast_inflight.get(key)
    if task is None:
        task = asyncio.create_task(_fetch_uncached(key))
        _forecast_inflight[key] = task
        def release(completed: asyncio.Task[WeatherResponse]) -> None:
            if _forecast_inflight.get(key) is completed:
                _forecast_inflight.pop(key)

        task.add_done_callback(release)
    return await asyncio.shield(task)


async def _fetch_uncached(key: tuple[float, float]) -> WeatherResponse:
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.get(
                FORECAST_URL,
                params={
                    "latitude": key[0],
                    "longitude": key[1],
                    "current": "weather_code",
                },
            )
            response.raise_for_status()
            data = response.json()
        if not isinstance(data, dict) or not isinstance(data.get("current"), dict):
            raise TypeError("Malformed forecast")
        condition = normalize_weather(data["current"]["weather_code"])
    except (httpx.HTTPError, ValueError, TypeError, KeyError):
        return _fallback(key)
    updated_at = datetime.now(timezone.utc)
    _forecast_cache[key] = (condition, updated_at)
    _last_known_forecast[key] = (condition, updated_at)
    return WeatherResponse(
        condition=condition, status=WeatherStatus.OK, updated_at=updated_at
    )
