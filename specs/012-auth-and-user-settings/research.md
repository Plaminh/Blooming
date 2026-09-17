# Research: Auth and User Settings

## Topic 1: Password Hashing in FastAPI
- **Decision**: Use `bcrypt` library directly for password hashing.
- **Rationale**: `passlib` has been the traditional choice but is currently unmaintained and raises deprecation warnings on newer Python versions. Using the `bcrypt` library directly provides a secure, modern, and maintained approach for hashing passwords.
- **Alternatives considered**: `passlib[bcrypt]` (rejected due to lack of maintenance), `argon2-cffi` (excellent, but `bcrypt` is standard and very widely supported in Python).

## Topic 2: JWT Authentication in FastAPI
- **Decision**: Use `PyJWT` for JWT generation and validation.
- **Rationale**: It is the standard, actively maintained library for JWTs in Python. It does not require complex cryptographic C-extensions compared to `python-jose` (which has also seen less maintenance recently).
- **Alternatives considered**: `python-jose` (rejected due to inactivity).

## Topic 3: Settings Schema Updates
- **Decision**: Add new boolean/string columns to `user_settings` in a new forward-only Alembic migration based on the `6ebc3e7e2e0e` baseline.
- **Rationale**: The product requires web-local desktop settings (`widget_visibility`, `widget_always_on_top`, `launch_on_startup`, `weather_enabled`, `weather_location`) that do not yet exist in the schema.
- **Alternatives considered**: Storing them in a JSON column. Rejected because the existing `user_settings` table uses explicit typed columns (e.g. `reminders_enabled`). Keeping explicit columns maintains consistency and type safety.

## Topic 4: Active Plant Reference
- **Decision**: Postpone `active_plant` reference.
- **Rationale**: The models do not yet have a `plants` or `unlocked_plants` table. The spec dictates that we should not invent Garden logic and should defer it. We will simply omit `active_plant` from the current update payload or allow it as optional and ignore it safely.
- **Alternatives considered**: Create a mock `plants` table (rejected as out of scope and violating constitution).


