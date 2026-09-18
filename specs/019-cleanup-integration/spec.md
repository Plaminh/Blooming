# Feature Specification: Corrective Bug Fixes and Technical Cleanup

**Feature Branch**: `[019-cleanup-integration]`

**Created**: 2026-09-18

**Status**: Planning

**Input**: User explicit bug-fix instructions for Daily Plan, Reminder action, Frontend tests, and Garden vitality.

## Overview and Problem Statement

The current system has several critical integration bugs and technical debt that must be resolved:
1. **Daily Plan Replace Error**: `save_daily_plan(replace_existing=True)` fails due to a `UNIQUE(user_id, plan_date)` constraint when archiving the old plan and inserting a new one for the same date.
2. **Reminder Action CREATE_PLAN Bug**: Reminders to create plans evaluate dates in UTC instead of the user's local timezone and insert directly into `DailyPlan` instead of using the robust `create_draft` logic, leading to duplicate plans or 500 errors.
3. **TodayView Frontend Test Failures**: Tests in `TodayView.test.ts` are failing because they mock `/today?date=YYYY-MM-DD` but the application intentionally requests `/today` (no date query parameter) on initial load to allow backend timezone handling.
4. **Dead Constant VITALITY_WATERING_EFFECT**: The system uses a simple `last_watered_at` calculation for vitality, making the `VITALITY_WATERING_EFFECT` constant obsolete and confusing.

## Scope

### In-Scope
- Correcting the Daily Plan replace constraint with a partial unique index.
- Fixing the timezone and draft creation logic in `CREATE_PLAN` reminder action.
- Updating `TodayView.test.ts` to mock `/today` properly without modifying production code.
- Removing `VITALITY_WATERING_EFFECT`.
- Edit `database/migrations/05_daily_planning.sql` directly and synchronize the SQLAlchemy model. Do not add an Alembic revision. Existing databases require manual recreation or a separately executed manual schema update.

### Out-of-Scope
- No backend tests (unit, integration, API, testcontainers, sqlite/aiosqlite) will be written. All backend testing is deferred to a future spec.
- No general refactoring outside the targeted bug fixes.
- No changes to GardenState schema, vitality decay logic, or reminder/planning chat redesign.
- No changes to `+page.svelte` in `TodayView` just to pass tests.
- No deletion of old plans or alteration of history during migration.

## Functional Requirements

- **FR-01**: The system MUST allow only one active daily plan (DRAFT, CONFIRMED, or ACTIVE) per user per local date.
- **FR-02**: The system MUST allow multiple non-active daily plans (ARCHIVED, COMPLETED) per user per local date.
- **FR-03**: The `CREATE_PLAN` reminder action MUST evaluate the current date using the user's configured timezone.
- **FR-04**: The `CREATE_PLAN` reminder action MUST use `crud_daily_plan.create_draft()` and gracefully handle `PlanAlreadyExistsError` without throwing a 500.
- **FR-05**: If a plan already exists, the `CREATE_PLAN` reminder MUST be marked as COMPLETED and instruct the user to view their Today page.
- **FR-06**: Frontend tests in `TodayView.test.ts` MUST pass by properly mocking both `/today` and `/today?date=YYYY-MM-DD`.
- **FR-07**: The system MUST NOT rely on the `VITALITY_WATERING_EFFECT` constant for garden vitality.

## Technical Design

### 1. Daily Plan Replacement
- **Constraint Changes**: Replace `UNIQUE (user_id, plan_date)` with a partial unique index:
  ```sql
  CREATE UNIQUE INDEX daily_plans_one_active_per_local_date
  ON daily_plans (user_id, plan_date)
  WHERE status IN ('DRAFT', 'CONFIRMED', 'ACTIVE');
  ```
- **ORM Model**: Replace `UniqueConstraint` in `backend/app/db/models/daily_plans.py` with SQLAlchemy `Index(..., postgresql_where=...)`.

### 2. CREATE_PLAN Reminder
- **Timezone Resolution**: Retrieve user timezone from `UserSettings` and convert `datetime.now(timezone.utc)` to the local date.
- **Draft Creation**: Call `crud_daily_plan.create_draft(...)`.
- **Error Handling**: Catch `PlanAlreadyExistsError`. Treat it as a successful business outcome (return specific message routing user to Today, and complete the action).

### 3. TodayView.test.ts
- **Mock Update**: Intercept `GET /today` (no query params) and provide the initial today state. Differentiate from `GET /today?date=...`.

### 4. VITALITY_WATERING_EFFECT Cleanup
- **Constant Removal**: Delete `VITALITY_WATERING_EFFECT` from `backend/app/core/economy.py`.
- **Logic Verification**: Ensure `water_plant()` continues updating `last_watered_at` without attempting to add vitality explicitly.

## Acceptance Criteria

1. **Daily Plan**: User can replace a plan; old plan transitions to `ARCHIVED`, new plan takes its place with the same date, without `IntegrityError`.
2. **Reminder Action**: `CREATE_PLAN` creates a draft accurately for the user's timezone; if a plan exists, it gracefully responds "A plan already exists for today. Open Today to view it." and does not 500.
3. **Frontend Tests**: `npm run test` passes all `TodayView.test.ts` suites; `+page.svelte` is unchanged.
4. **Garden**: `VITALITY_WATERING_EFFECT` is removed; watering a plant successfully restores its vitality using `last_watered_at`.
