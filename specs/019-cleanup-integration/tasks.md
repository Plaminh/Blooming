# Implementation Tasks: Corrective Bug Fixes and Technical Cleanup

**Input**: Design documents from `/specs/019-cleanup-integration/`

**Prerequisites**: plan.md, spec.md

## Phase 1: Database Migration and Models (Daily Plan Replace Fix)

- [ ] T001: Edit `database/migrations/05_daily_planning.sql` directly to drop the `daily_plans_one_per_local_date` constraint and add a partial unique index `daily_plans_one_active_per_local_date` on `(user_id, plan_date)` where status is `DRAFT`, `CONFIRMED`, or `ACTIVE`. Do not add an Alembic revision for this fix.
- [ ] T002: Update `backend/app/db/models/daily_plans.py` to replace `UniqueConstraint` with an SQLAlchemy `Index(..., postgresql_where=...)`.

## Phase 2: Reminder Service (CREATE_PLAN Fix)

- [ ] T004: Update `backend/app/services/reminders_service.py` to retrieve `UserSettings.timezone`, fallback to UTC, and determine `local_date` correctly using `now.astimezone(tz).date()`.
- [ ] T005: Update the `CREATE_PLAN` logic in `reminders_service.py` to call `crud_daily_plan.create_draft(...)` instead of inserting a `DailyPlan` instance directly.
- [ ] T006: Add try-except logic in the `CREATE_PLAN` block to catch `PlanAlreadyExistsError`. Upon catching, mark the action as COMPLETED and return a user-friendly message: "A plan already exists for today. Open Today to view it."

## Phase 3: Dead Code Removal (Garden Vitality)

- [ ] T007: Remove the `VITALITY_WATERING_EFFECT` constant from `backend/app/core/economy.py`.
- [ ] T008: Search the backend codebase and remove any unused imports of `VITALITY_WATERING_EFFECT` (e.g., in `garden_service.py`).

## Phase 4: Frontend Testing (TodayView Fix)

- [ ] T009: Update `frontend/src/lib/features/today/TodayView.test.ts` to properly intercept both `/today` (no date query param) and `/today?date=YYYY-MM-DD`. Ensure the mock returns correct initial data when no date query is provided.
- [ ] T010: Run frontend tests to ensure `TodayView.test.ts` passes successfully without modifying `+page.svelte`.

## Verification Instructions

- Verify `database/migrations/05_daily_planning.sql` and `backend/app/db/models/daily_plans.py` have the correct unique index and lack the old unique constraint. Existing instances require manual database recreation.
- Ensure `save_daily_plan(replace_existing=True)` works by mocking or calling the planning service manually.
- Run `npm run test` in the frontend directory.
- Verify `CREATE_PLAN` no longer generates `DailyPlan` without `create_draft` and handles the existing plan error gracefully.
- Run `ruff check` and `ruff format` on backend to ensure compliance.
