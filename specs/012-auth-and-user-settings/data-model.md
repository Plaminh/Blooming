# Data Model: Auth and User Settings

## Entity Updates

### `UserSettings` (Existing Table)

We will add the following columns via Alembic migration:

- `widget_visibility` (`Boolean`, default: `TRUE`, non-nullable)
- `widget_always_on_top` (`Boolean`, default: `FALSE`, non-nullable)
- `launch_on_startup` (`Boolean`, default: `FALSE`, non-nullable)
- `weather_enabled` (`Boolean`, default: `FALSE`, non-nullable)
- `weather_location` (`String(100)`, nullable)

These additions support the onboarding and settings UI preferences for the web-local phase of the application.

## New Pydantic Models (Internal / Domain)

### `UserCreate` (Schema)
- `email`: `str` (EmailStr)
- `password`: `str`
- `display_name`: `str | None`

### `UserResponse` (Schema)
- `id`: `UUID`
- `email`: `str`
- `display_name`: `str | None`
- `created_at`: `datetime`

### `TokenResponse` (Schema)
- `access_token`: `str`
- `token_type`: `str` (e.g., "bearer")

### `UserSettingsUpdate` (Schema)
- `timezone`: `str | None`
- `default_focus_minutes`: `int | None`
- `default_break_minutes`: `int | None`
- `quiet_hours_enabled`: `bool | None`
- `quiet_hours_start`: `time | None`
- `quiet_hours_end`: `time | None`
- `mr_bloom_display_name`: `str | None`
- `widget_visibility`: `bool | None`
- `widget_always_on_top`: `bool | None`
- `launch_on_startup`: `bool | None`
- `weather_enabled`: `bool | None`
- `weather_location`: `str | None`

### `UserSettingsResponse` (Schema)
Same fields as `UserSettingsUpdate`, but all are strictly typed to their database nullability (e.g. non-nullable fields are strictly returned as their type).


