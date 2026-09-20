# Data Model: Weather Environment Reliability

## Core Entities

### UserSettings (Update)
The existing `UserSettings` SQLAlchemy model will be updated.

**New Fields:**
- `weather_location_name`: `String` (Nullable, max length 255) - The human-readable selected name.
- `weather_lat`: `NUMERIC(5, 2)` (Nullable) - Approximate latitude, rounded to 2 decimal places.
- `weather_lon`: `NUMERIC(6, 2)` (Nullable) - Approximate longitude, rounded to 2 decimal places.
- `scene_season`: `Enum` (AUTO, SPRING, SUMMER, AUTUMN, WINTER) - Default: AUTO.

**Validation Rules:**
- `weather_lat` must be between -90.00 and 90.00.
- `weather_lon` must be between -180.00 and 180.00.
- Both coordinates must be rounded to exactly 2 decimal places before persistence.

**Legacy Handling:**
- Existing `weather_location` (free-text) remains in the canonical SQL schema and is never converted to confirmed coordinates.

### Enums

#### WeatherCondition
- `CLEAR`
- `CLOUDY`
- `OVERCAST`
- `RAIN`
- `THUNDERSTORM`

#### WeatherStatus
- `OK`: Fetch successful, fresh data (within 15 min TTL).
- `STALE`: Provider fetch failed, using last known good data (within 2 hours).
- `UNAVAILABLE`: Provider fetch failed, no usable recent data.
- `DISABLED`: Weather is disabled in settings.

#### SceneSeason
- `AUTO`: Determined by hemisphere/month based on `weather_lat`.
- `SPRING`
- `SUMMER`
- `AUTUMN`
- `WINTER`

## Frontend State Model

### EnvironmentStore (Svelte Store)
A single shared store for the widget and main app context.

**Fields:**
- `condition`: `WeatherCondition | null`
- `status`: `WeatherStatus`
- `updatedAt`: `string` (ISO datetime)
- `effectiveTimezone`: `string`
- `effectiveSeason`: `SceneSeason`
- `isAnimationEnabled`: `boolean`
- `isLoading`: `boolean`
- `lastAttempt`: `number` (Timestamp)

**State Transitions:**
- Initialization reads initial settings.
- Updates occur on a 15-minute polling interval or explicit focus refresh (with a 5-minute debounce).
- Dispatches state uniformly to `<WidgetSceneBackground>`, `<GardenPanel>`, and `<RainLayer>`.
