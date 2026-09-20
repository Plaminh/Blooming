# Research: Weather Environment Reliability

## Needs Clarification Resolutions

**Unknown**: "Bounded 15-minute forecast cache and 24-hour place-search cache implementation details"
- **Decision**: Use `cachetools` with `TTLCache` in Python backend for in-memory caching.
- **Rationale**: `cachetools` is standard for simple TTL in-memory caching in Python without requiring external dependencies like Redis.
- **Alternatives considered**: Redis (rejected to keep dependencies simple and follow constitution constraint against unnecessary external infra).

**Unknown**: "Handling of timezone sync between frontend and backend"
- **Decision**: The frontend will read device timezone using `Intl.DateTimeFormat().resolvedOptions().timeZone` on startup, compare against persisted `user_settings.timezone`, and issue an API update if they differ.
- **Rationale**: This guarantees a single source of truth (the device OS) for timezone while persisting it for backend use.
- **Alternatives considered**: Backend IP-based timezone inference (rejected due to privacy and inaccuracy).

**Unknown**: "Weather Status Values & Enums"
- **Decision**: Define enums in Python backend and mirror in TypeScript frontend: `WeatherCondition` (CLEAR, CLOUDY, OVERCAST, RAIN, THUNDERSTORM) and `WeatherStatus` (OK, STALE, UNAVAILABLE, DISABLED), along with `SceneSeason` (AUTO, SPRING, SUMMER, AUTUMN, WINTER).
- **Rationale**: Aligns with the explicit five-condition model and prevents implicit untyped states.
- **Alternatives considered**: String literals (rejected due to lack of type safety).

## Patterns & Best Practices

- **Debouncing**: Frontend location search will use a 500ms debounce to prevent rate-limiting Open-Meteo API.
- **Cache Eviction**: `TTLCache` will have a `maxsize` of 100 for forecasts and 1000 for geocoding to bound memory usage.
- **Stale Fallback**: Weather service will implement a custom `get_weather` function that catches `httpx.HTTPError`, checks the cache for an entry within the last 2 hours, and returns `STALE` instead of `UNAVAILABLE` if found.
