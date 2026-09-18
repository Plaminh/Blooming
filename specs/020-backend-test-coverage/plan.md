# Implementation Plan: Blooming Backend Test Coverage

## Technical Context

- **Backend Framework**: FastAPI, Pydantic
- **Database ORM**: Async SQLAlchemy
- **Database Engine**: PostgreSQL
- **Migrations**: Direct authoritative SQL files (`database/migrations/`), no Alembic.
- **Dependencies**: Uses `httpx` for API tests, requires `pytest`, `pytest-asyncio`, and `testcontainers[postgres]`.
- **Existing Behaviors**: `garden_service` and others explicitly call `await db.commit()`, which prevents the use of simple rollback-based isolation for tests.
- **Auth**: JWT-based, decoded via `decode_access_token`.
- **Test DB**: `testcontainers-postgres` will serve as the primary database for the test suite, falling back to `TEST_DATABASE_URL` if testcontainers is disabled/unavailable.

## Constitution Check

- **Spec-driven development**: Validated against `specs/020-backend-test-coverage/spec.md`.
- **Planning correctness and deterministic ownership**: This feature strictly adds test coverage to ensure the deterministic ownership of scheduling, conflicts, reminders, and economy are preserved.
- **Clear architectural boundaries**: The tests interact with the modular monolith via decoupled unit, service, and API layers.
- **Type safety and explicit contracts**: Mocking will be minimal; integration tests will use explicit validation on models.
- **Testable behavior and quality gates**: Directly satisfies Principle 6 (Critical domain invariants require automated tests).

## Database Isolation Strategy

To provide bulletproof isolation against tests that explicitly commit transactions (e.g., `garden_service`), while keeping execution fast and preserving seed data (`plants`), we will use the **Template Database Strategy**:

1. **Session Scope Setup**:
   - Start `testcontainers-postgres` (or connect to `TEST_DATABASE_URL`).
   - Create a database named `blooming_template`.
   - Run the authoritative migrations (`00` to `10`) exactly once on `blooming_template`.
2. **Function Scope (Per Test)**:
   - Execute `CREATE DATABASE test_db_<uuid> TEMPLATE blooming_template;`.
   - The test runs connected to `test_db_<uuid>`.
   - Execute `DROP DATABASE test_db_<uuid>;` after the test.

*Why this is safe and reliable*: It guarantees 100% isolation (even if the application calls `COMMIT` or `ROLLBACK`) while providing millisecond-level reset speeds because `TEMPLATE` cloning is handled natively by PostgreSQL file copying.

## Execution Phases

### Phase 1: Test Infrastructure and Safety Guard
1. Add `pytest`, `pytest-asyncio`, `testcontainers[postgres]`, and `httpx` to test dependencies.
2. Implement `conftest.py` with the safety guard:
   - Ensure the selected test database URL never points to `settings.database_url`.
   - Ensure the selected test database is an ephemeral testcontainer or explicitly ends with `_test`.
3. Implement the `TEMPLATE` schema initialization logic in the session-scoped fixture.

### Phase 2: Shared Fixtures
1. Create function-scoped async engine and session fixtures pointing to the per-test cloned database.
2. Create `get_db_session` override for FastAPI's dependency injection.
3. Build `async_client` fixture for route testing.
4. Build entity factories (User, Task, DailyPlan, GardenState) using deterministic values and avoiding wall-clock time dependency.

### Phase 3: Scheduler Unit Tests (Pure)
1. Create `tests/unit/test_scheduler.py`.
2. Test `DeterministicScheduler` core logic without the database (overlap, cycle detection, splitting, deadlines).

### Phase 4: Service-Level Integration Tests
1. Create `tests/services/test_planning_service.py` verifying replacement rules and partial index enforcement.
2. Create `tests/services/test_reminders_service.py` verifying timezone fallback and duplicate avoidance for `CREATE_PLAN`.
3. Create `tests/services/test_garden_service.py` verifying idempotent resource awards.
4. Create `tests/services/test_focus_service.py` verifying lifecycle state transitions.

### Phase 5: API Route Tests
1. Create `tests/api/test_focus_routes.py` and `tests/api/test_reminder_routes.py`.
2. Verify HTTP 401/403 for auth failure, and error formatting for 404/409 conflicts.

### Phase 6: Documentation and Final Verification
1. Run the full suite with `pytest`.
2. Update local `quickstart.md`.

## Verification Commands

- **Unit tests**: `pytest tests/unit/test_scheduler.py`
- **Service integration tests**: `pytest tests/services/`
- **Full Backend Suite**: `pytest tests/`
- **Formatting check**: `ruff check tests/`

## Production-Code Changes

No production logic changes are required. The only change involves adding testing dependencies (`pytest`, `httpx`, `testcontainers`) to the repository and explicitly typing or importing existing modules if required for fixtures.
