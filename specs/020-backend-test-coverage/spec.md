# Feature Specification: Blooming Backend Test Coverage

**Feature Branch**: `020-backend-test-coverage`

**Created**: 2026-09-18

**Status**: Draft

**Input**: User description: Create a new specification for Blooming Backend Test Coverage.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Safe PostgreSQL test infrastructure (Priority: P1)

As a developer, I want a safe and repeatable backend test suite running against an isolated PostgreSQL database, so that I can write tests relying on PostgreSQL-specific features without modifying the normal development or production database.

**Why this priority**: Testing infrastructure is a prerequisite for all other tests. Safety mechanisms prevent destructive data loss during test runs.

**Independent Test**: Can be verified by running the test command and verifying that tests execute against the test database (ephemeral container or explicit `TEST_DATABASE_URL`) and that the development database is untouched.

**Acceptance Scenarios**:

1. **Given** a development database with existing data, **When** I run the backend test suite, **Then** the tests execute successfully, and the development database is unaffected.
2. **Given** an explicit test command, **When** tests execute, **Then** the database schema is initialized from authoritative SQL files under `database/migrations/` (no new Alembic migrations).

---

### User Story 2 - Daily Plan replacement regression tests (Priority: P1)

As a developer, I want service-level integration tests for Daily Plan creation and replacement to prevent regressions on core planning logic.

**Why this priority**: Protects against regressions on the critical functionality of having only one active Daily Plan per user per local date.

**Independent Test**: Can be verified by running the daily plan service test suite.

**Acceptance Scenarios**:

1. **Given** a user with no plan for a date, **When** `save_daily_plan` is called, **Then** a plan is created successfully.
2. **Given** a user with an active plan for a date, **When** `save_daily_plan(replace_existing=False)` is called, **Then** the operation is rejected.
3. **Given** a user with an active plan for a date, **When** `save_daily_plan(replace_existing=True)` is called, **Then** the old plan is archived, its original `plan_date` is preserved, a replacement plan is created/confirmed, no `IntegrityError` is raised, and exactly one active plan remains for that user/date.
4. **Given** a user's plan, **When** another user attempts to replace or access it, **Then** the operation is rejected.

---

### User Story 3 - Scheduler Unit Tests (Priority: P1)

As a developer, I want unit tests for the `DeterministicScheduler` to ensure that dependency, overlap, splitting, and deadline behaviors remain deterministic.

**Why this priority**: The scheduler is the heart of Blooming's task management system. Its logic must be correct and deterministic.

**Independent Test**: Can be run purely as unit tests without database access.

**Acceptance Scenarios**:

1. **Given** identical input parameters, **When** the scheduler runs, **Then** it produces deterministic output.
2. **Given** overlapping fixed tasks, **When** scheduling, **Then** it detects the overlap and marks invalid intervals.
3. **Given** tasks with dependencies, **When** scheduling, **Then** prerequisites are scheduled before dependent tasks.
4. **Given** a task with a direct or multi-task dependency cycle, **When** scheduling, **Then** it detects the cycle.
5. **Given** a splittable task and minimum split duration, **When** scheduling, **Then** it splits the task appropriately within available continuous slots.

---

### User Story 4 - `CREATE_PLAN` Reminder Tests (Priority: P1)

As a developer, I want service-level tests for the `CREATE_PLAN` reminder action to protect timezone logic and draft-creation workflow.

**Why this priority**: Reminders rely heavily on timezones. Bugs here directly affect user notification accuracy.

**Independent Test**: Verified by the reminders service test suite.

**Acceptance Scenarios**:

1. **Given** a user near the UTC date boundary, **When** `CREATE_PLAN` executes, **Then** the plan date is calculated using their local timezone from `UserSettings`.
2. **Given** a user with a missing or invalid timezone, **When** `CREATE_PLAN` executes, **Then** it falls back to the established UTC behavior.
3. **Given** no existing plan, **When** `CREATE_PLAN` executes, **Then** it creates the expected draft, task (with intended 30-minute reminder behavior), and plan block.
4. **Given** an existing `CONFIRMED` or `ACTIVE` plan, **When** `CREATE_PLAN` executes, **Then** no duplicate plan/task/block is created, the reminder is marked `COMPLETED`, and the action succeeds.

---

### User Story 5 - Garden Reward Idempotency Tests (Priority: P1)

As a developer, I want service-level integration tests for resource awards to prevent users from accidentally receiving duplicate resources.

**Why this priority**: Prevents economy exploitation and balances corruption.

**Independent Test**: Verified by the garden service test suite.

**Acceptance Scenarios**:

1. **Given** a valid Water or Leaves reward, **When** awarded, **Then** the respective balance increases exactly once.
2. **Given** the same `idempotency_key`, **When** `award_resources()` is called twice, **Then** resources are awarded only once.
3. **Given** an invalid reward input, **When** awarded, **Then** balances are not corrupted and never become negative.
4. **Given** a watering action, **When** executed, **Then** `last_watered_at` updates and vitality is restored correctly without modifying plant growth points or unlocked plants.

---

### User Story 6 - Focus Service Lifecycle Tests (Priority: P2)

As a developer, I want integration/API tests for the core focus session lifecycle to prevent regressions in focus timers and rewards.

**Why this priority**: Focus sessions interact with rewards, timing, and planning logic.

**Independent Test**: Verified by the focus service test suite.

**Acceptance Scenarios**:

1. **Given** no active session, **When** starting a focus session, **Then** it starts successfully.
2. **Given** an active session, **When** starting another focus session, **Then** it is rejected.
3. **Given** an active session, **When** finishing it (with `DONE`, `NEED_MORE_TIME`, `SKIP`, or `FINISHED_EARLY`), **Then** it finishes, calculates actual duration based on server timestamps and pauses, and awards Water exactly once if eligible.
4. **Given** a finish request, **When** retried, **Then** it does not duplicate the reward.

---

### User Story 7 - API Error-Contract Coverage (Priority: P2)

As a developer, I want minimal verification of the API error contract for focus and reminder routes to ensure consistent API behavior.

**Why this priority**: Maintains API stability and prevents data leakage.

**Independent Test**: Verified via API route tests.

**Acceptance Scenarios**:

1. **Given** an unauthenticated request, **When** accessing the routes, **Then** the request is rejected.
2. **Given** a request for another user's resources, **When** processed, **Then** it is rejected and resources are not exposed.
3. **Given** validation or conflict scenarios, **When** returning errors, **Then** the established standard error response format is used.

## Edge Cases

- **PostgreSQL Data Contamination**: Tests running locally must never connect to a developer's production or working dev database.
- **Timezone edge cases**: `CREATE_PLAN` executed precisely at midnight (UTC vs Local boundaries).
- **Concurrency**: Calling `award_resources` simultaneously with the same `idempotency_key`.
- **Focus timing**: Focus sessions finished when server time indicates the session duration has not technically passed, but paused durations were involved.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST establish a `pytest` and `pytest-asyncio` backend testing foundation with Async SQLAlchemy sessions.
- **FR-002**: System MUST use an isolated PostgreSQL database (ephemeral container or explicit `TEST_DATABASE_URL`) for integration tests, avoiding SQLite.
- **FR-003**: System MUST NOT connect to, reset, truncate, or migrate the normal development database during test execution.
- **FR-004**: System MUST initialize test schemas from existing authoritative SQL files in `database/migrations/` (no Alembic migrations created).
- **FR-005**: System MUST isolate test data via rollback, truncation, or disposable schemas.
- **FR-006**: Tests MUST mock external boundaries (e.g. LLM API, Weather API) and be deterministic, independent of local timezone or execution order.
- **FR-007**: System MUST provide unit tests covering `DeterministicScheduler` rules and edge cases (overlap, splitting, dependencies, cycles).
- **FR-008**: System MUST provide integration tests verifying that `save_daily_plan` preserves one active plan per user/date using partial unique index behavior.
- **FR-009**: System MUST provide integration tests verifying `CREATE_PLAN` uses user timezone correctly and doesn't duplicate existing plans.
- **FR-010**: System MUST provide integration tests verifying garden reward idempotency and balance integrity.
- **FR-011**: System MUST provide integration tests verifying focus session start, pause, resume, and finish flows, including reward assignments.
- **FR-012**: System MUST organize tests mirroring the backend structure (e.g., `tests/unit/test_scheduler.py`, `tests/services/test_planning_service.py`).

### Key Entities

- **Test Infrastructure**: The `conftest.py` setup, database fixtures, authenticated client fixtures.
- **Daily Plan**: User's plan for a specific date, constrained by PostgreSQL partial unique indexes.
- **Task & Reminders**: Scheduled entities that trigger actions like `CREATE_PLAN`.
- **Garden State**: User's resource balances (Water, Leaves) and plant vitality.
- **Focus Session**: A timed, stateful block of focused work that awards resources upon completion.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Backend tests run with a single documented command.
- **SC-002**: The test suite guarantees safety by being fundamentally incapable of modifying the normal development or production database.
- **SC-003**: Tests pass both independently and when run as a full suite.
- **SC-004**: The Daily Plan replacement regression is reproducibly covered.
- **SC-005**: PostgreSQL enforces one active plan per user and local date during testing.
- **SC-006**: Reminder timezone behavior is covered across a UTC date boundary.
- **SC-007**: Duplicate reward attempts do not increase balances twice.
- **SC-008**: Core scheduler edge cases produce deterministic blocks and reason codes.
- **SC-009**: Focus completion cannot award Water twice.
- **SC-010**: The suite requires no live external API or frontend runtime.
- **SC-011**: Test setup and execution steps are documented for local development and CI.
- **SC-012**: No new Alembic migration or unrelated product behavior is introduced.

## Assumptions

- Assumes existing project conventions for HTTP client testing with FastAPI (`httpx` AsyncClient).
- Assumes the existing deterministic scheduler logic can be tested without a database or with minimal test db fixtures.
- The choice between ephemeral test containers vs `TEST_DATABASE_URL` will be decided during the planning phase by inspecting existing project tools.
- Minimal production-code changes will only be made if necessary to support testability, without altering the business behavior.
- Out of scope: Frontend tests, snapshot tests, UI tests, new features, and redesigns of existing services.
