"""Current weather for the user's configured location, with bounded provider calls."""

import asyncio
import re
import time
import weakref

import httpx


GEOCODING_URL = "https://geocoding-api.open-meteo.com/v1/search"
FORECAST_URL = "https://api.open-meteo.com/v1/forecast"
WEATHER_TTL_SECONDS = 900
LOCATION_TTL_SECONDS = 86400

_weather_cache: dict[str, tuple[float, str]] = {}
_location_cache: dict[str, tuple[float, tuple[float, float]]] = {}
_location_locks: weakref.WeakValueDictionary[str, asyncio.Lock] = weakref.WeakValueDictionary()
_COORDINATES = re.compile(r"^\s*(-?\d+(?:\.\d+)?)\s*,\s*(-?\d+(?:\.\d+)?)\s*$")


def parse_coordinates(location: str) -> tuple[float, float] | None:
    match = _COORDINATES.fullmatch(location)
    if not match:
        return None
    latitude, longitude = map(float, match.groups())
    if -90 <= latitude <= 90 and -180 <= longitude <= 180:
        return latitude, longitude
    return None


def normalize_weather(code: int) -> str:
    """Map WMO weather codes to the widget's five supported conditions."""
    if code in (95, 96, 99):
        return "THUNDERSTORM"
    if code in (51, 53, 55, 56, 57, 61, 63, 65, 66, 67, 80, 81, 82):
        return "RAIN"
    # The widget has no snow layer; show its cloud cover without fake rain.
    if code in (3, 45, 48, 71, 73, 75, 77, 85, 86):
        return "OVERCAST"
    if code == 2:
        return "CLOUDY"
    return "CLEAR"


async def current_weather(location: str) -> str:
    key = location.strip().casefold()
    if not key:
        return "CLEAR"
    # Serialize fetches for this location only. Other users' locations can
    # contact the provider while this one is waiting for a response.
    async with _location_locks.setdefault(key, asyncio.Lock()):
        now = time.monotonic()
        cached = _weather_cache.get(key)
        if cached and cached[0] > now:
            return cached[1]
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                coordinates = _location_cache.get(key)
                device_point = parse_coordinates(location)
                if device_point is not None:
                    point = device_point
                elif not coordinates or coordinates[0] <= now:
                    response = await client.get(GEOCODING_URL, params={"name": location.strip(), "count": 1})
                    response.raise_for_status()
                    results = response.json().get("results") or []
                    if not results:
                        _weather_cache[key] = (now + WEATHER_TTL_SECONDS, "CLEAR")
                        return "CLEAR"
                    point = (float(results[0]["latitude"]), float(results[0]["longitude"]))
                    _location_cache[key] = (now + LOCATION_TTL_SECONDS, point)
                else:
                    point = coordinates[1]
                response = await client.get(
                    FORECAST_URL,
                    params={"latitude": point[0], "longitude": point[1], "current": "weather_code"},
                )
                response.raise_for_status()
                condition = normalize_weather(int(response.json()["current"]["weather_code"]))
                _weather_cache[key] = (now + WEATHER_TTL_SECONDS, condition)
                return condition
        except (httpx.HTTPError, ValueError, KeyError, TypeError, IndexError):
            # An expired condition may be hours old; use the safe fallback.
            _weather_cache.pop(key, None)
            return "CLEAR"
