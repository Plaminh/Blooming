# Implementation Plan: Corrective Bug Fixes and Technical Cleanup

Frontend: SvelteKit / Svelte 5 / TypeScript. Backend: FastAPI / Pydantic / SQLAlchemy / PostgreSQL.

## Scope and Governance

This plan addresses a specific set of critical bug fixes for the Daily Plan replacement constraint, the `CREATE_PLAN` reminder action, frontend testing, and dead-code removal for garden vitality.

**Testing restrictions for this feature:**
- NO backend testing (unit, integration, API) will be implemented in this phase. Do not create test files, `conftest.py`, or configure SQLite/Testcontainers.

## Implementation Order

### 1. Database Migrations and Models (Daily Plan)
1. Edit `database/migrations/05_daily_planning.sql` directly to remove the `UNIQUE (user_id, plan_date)` constraint and replace it with a partial unique index on `(user_id, plan_date)` where status is `DRAFT`, `CONFIRMED`, or `ACTIVE`.
2. Do not add an Alembic revision for this fix. Existing databases require manual recreation or a separately executed manual schema update. Never recreate or delete the developer’s database automatically.
3. Update `backend/app/db/models/daily_plans.py` to remove `UniqueConstraint` and add `Index` with `postgresql_where`.

### 2. Services: Planning and Reminders
1. **Planning Service**: Ensure `save_daily_plan` naturally archives the old plan and persists the new one. The new partial unique index will resolve the `IntegrityError`. No extra cleanup code should be needed if the state changes correctly.
2. **Reminders Service**: Refactor `CREATE_PLAN` action in `backend/app/services/reminders_service.py`.
   - Read user's timezone from `UserSettings`.
   - Resolve local date accurately using `now.astimezone(tz).date()`.
   - Replace `db.add(DailyPlan(...))` with `crud_daily_plan.create_draft(...)`.
   - Catch `PlanAlreadyExistsError` to return a user-friendly message redirecting them to the Today screen and mark the action COMPLETED. Keep the current 30-minute task logic.

### 3. Economy Constants (Garden)
1. Remove `VITALITY_WATERING_EFFECT` from `backend/app/core/economy.py`.
2. Remove any dead references or imports of this constant.
3. Verify `water_plant()` in `backend/app/services/garden_service.py` functions correctly by updating `last_watered_at` and does not refer to the deleted constant.

### 4. Frontend Testing
1. Update `frontend/src/lib/features/today/TodayView.test.ts`.
2. Refactor the MSW (or local SvelteKit mock) network handler for `/today` to correctly match the bare `/today` request and the `/today?date=...` request.
3. Verify that `TodayView.test.ts` passes without altering `+page.svelte`.

## Affected Files

### Backend
- `backend/app/db/models/daily_plans.py`
- `backend/app/services/reminders_service.py`
- `backend/app/core/economy.py`
- `backend/app/services/garden_service.py` (if imports exist)
- `database/migrations/05_daily_planning.sql`

### Frontend
- `frontend/src/lib/features/today/TodayView.test.ts`

## Error-Handling Behavior
- `PlanAlreadyExistsError` during `CREATE_PLAN`: Handled gracefully. Converted to a success response directing the user to the Today page, not a 500 server error.
- Invalid or missing Timezone: Should fallback to UTC when resolving the date for `CREATE_PLAN`.

## Validation
- **Backend checks**: `ruff check`, `ruff format`, `pytest` (only running existing unaffected tests, DO NOT write new backend tests).
- **Database checks**: Confirm the direct SQL edits are correct. Existing instances must be manually recreated.
- **Frontend checks**: `npm run test` for the Today feature to verify the fix.
