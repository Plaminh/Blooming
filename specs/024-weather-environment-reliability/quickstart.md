# Quickstart Validation Guide

The authoritative fresh schema is `database/install.sql`, which includes
`database/migrations/01_users_and_auth.sql`. Run it only against a disposable
empty PostgreSQL database with `psql -v ON_ERROR_STOP=1 -f database/install.sql`.
Editing bootstrap SQL does not alter an existing database; existing databases
need a reviewed additive SQL update or a new empty database.

## Existing databases

The following additive SQL is for manual review and execution against an
existing database. It is not run by the application or the fresh installer.
It preserves legacy `weather_location` values and leaves new coordinates null
until a user selects a place.

```sql
BEGIN;
ALTER TABLE user_settings
  ADD COLUMN weather_location_name VARCHAR(255),
  ADD COLUMN weather_lat NUMERIC(5, 2),
  ADD COLUMN weather_lon NUMERIC(6, 2),
  ADD COLUMN scene_season VARCHAR(20) NOT NULL DEFAULT 'AUTO',
  ADD CONSTRAINT user_settings_weather_lat_valid
    CHECK (weather_lat IS NULL OR weather_lat BETWEEN -90.00 AND 90.00),
  ADD CONSTRAINT user_settings_weather_lon_valid
    CHECK (weather_lon IS NULL OR weather_lon BETWEEN -180.00 AND 180.00),
  ADD CONSTRAINT user_settings_scene_season_valid
    CHECK (scene_season IN ('AUTO', 'SPRING', 'SUMMER', 'AUTUMN', 'WINTER')),
  ADD CONSTRAINT user_settings_weather_coordinate_pair
    CHECK ((weather_lat IS NULL AND weather_lon IS NULL)
       OR (weather_lat IS NOT NULL AND weather_lon IS NOT NULL)),
  ADD CONSTRAINT user_settings_weather_name_not_blank
    CHECK (weather_location_name IS NULL OR BTRIM(weather_location_name) <> ''),
  ADD CONSTRAINT user_settings_weather_coordinates_named
    CHECK ((weather_lat IS NULL AND weather_lon IS NULL)
       OR (weather_location_name IS NOT NULL AND BTRIM(weather_location_name) <> ''));
COMMIT;
```

For a disposable fresh database, run:

```bash
psql "$DATABASE_URL" -v ON_ERROR_STOP=1 -f database/install.sql
psql "$DATABASE_URL" -v ON_ERROR_STOP=1 -f database/tests/00_schema_smoke_test.sql
```

## 1. Validating Place Search & Selection

**Setup**:
1. Run backend tests or start backend server.
2. Open frontend to the Onboarding or Settings screen.

**Steps**:
- Type "London" into the location search field.
- Verify that a maximum of 5 candidates are returned.
- Select "London, United Kingdom".
- Check backend database or API response to confirm `weather_lat` and `weather_lon` are saved with maximum 2 decimal places.

## 2. Validating Stale Fallback

**Setup**:
- In the backend `.env` or configuration, set the Open-Meteo endpoint to an invalid URL to simulate an outage.

**Steps**:
- Trigger a weather fetch (e.g. initial load).
- If the cache has valid data from the last 2 hours, the UI should show the last known condition and `STALE` status.
- If the cache has no data or it's older than 2 hours, the UI should handle `UNAVAILABLE` without flashing or logging spurious errors.

## 3. Validating Deterministic Preview

**Setup**:
- Launch the widget/frontend.

**Steps**:
- Navigate to `/widget-preview?time=NIGHT&season=WINTER&weather=RAIN`.
- Verify the scene renders as Winter at Night with Rain, completely overriding live settings and live weather without mutating the database.

## 4. Validating Shared Environment Store

**Setup**:
- Launch the main application window and open the Garden Panel.
- Also open the widget if testing in desktop mode.

**Steps**:
- Manually change the backend weather condition to `THUNDERSTORM`.
- Verify both the widget and the Garden Panel update to the thunderstorm scene simultaneously upon the next polling interval, with no duplicate polling loops.
