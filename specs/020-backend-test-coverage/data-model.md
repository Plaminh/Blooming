# Data Model (Testing Fixtures)

## Core Testing Entities

The testing framework requires robust factories/fixtures for these entities to ensure they can be composed without leaking state.

### Async Session & Client
- **Entity**: `db_session`
  - **Type**: Async SQLAlchemy Session
  - **Lifecycle**: Function-scoped, points to the test database.
- **Entity**: `async_client`
  - **Type**: `httpx.AsyncClient`
  - **Lifecycle**: Function-scoped, overrides `get_db_session` to use `db_session`.

### Users & Auth
- **Entity**: `test_user`
  - **Fields**: ID, email, hashed password, timezone, status="ACTIVE", email_verified_at.
- **Entity**: `auth_headers`
  - **Type**: Dict with `Authorization: Bearer <token>`
  - **Dependency**: Generated from `test_user`.

### Planning & Scheduling
- **Entity**: `test_daily_plan`
  - **Fields**: user_id, plan_date, status.
- **Entity**: `test_task`
  - **Fields**: user_id, title, duration, dependency_id, splittable.
  - **Constraint**: Needs a `test_user`.
- **Entity**: `availability_window`
  - **Fields**: start_time, end_time.

### Focus & Garden
- **Entity**: `test_focus_session`
  - **Fields**: user_id, status, started_at, paused_at, actual_duration_seconds.
- **Entity**: `test_garden_state`
  - **Fields**: user_id, water_balance, leaves_balance, last_watered_at, growth_points.

## Fixture Relationships & Isolation

- **Isolation**: Each test runs against a uniquely cloned PostgreSQL database created via `CREATE DATABASE ... TEMPLATE blooming_template`. This guarantees 100% isolation for explicit `commit()` calls while preserving reference data (e.g. `plants`).
- **Dependencies**: Factories should automatically provision required parent entities (e.g. `test_task` should create a `test_user` if one isn't provided).
