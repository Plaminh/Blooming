# Validation guide and corrective cleanup record

## Database setup

The authoritative installer is `psql -v ON_ERROR_STOP=1 -f database/install.sql` against a fresh disposable database. The three CREATE TABLE changes are category VARCHAR(50) NULL (Learning/Work/Personal or NULL), growth_points INTEGER NOT NULL DEFAULT 0 (>=0), and milestone_reminder_lead_time_minutes INTEGER NOT NULL DEFAULT 1440 (0-43200).

No feature Alembic migration exists. Do not run a feature migration or edit the historical baseline. CREATE TABLE IF NOT EXISTS does not update existing tables. The developer database and volume were not modified or recreated.

### Existing local databases

For an existing database that already has the authoritative Water/Leaves reward schema, run the following additive SQL manually with `psql -v ON_ERROR_STOP=1` against the intended database. The transaction adds no unrelated objects and removes no data. If the database still has only the older heart_events/total_heart schema, these three additions alone are insufficient; reconcile that older baseline separately before starting this implementation. No automatic reset or recreation is provided.

```sql
BEGIN;
ALTER TABLE public.user_settings
  ADD COLUMN IF NOT EXISTS milestone_reminder_lead_time_minutes INTEGER NOT NULL DEFAULT 1440;
ALTER TABLE public.tasks
  ADD COLUMN IF NOT EXISTS category VARCHAR(50) NULL;
ALTER TABLE public.garden_states
  ADD COLUMN IF NOT EXISTS growth_points INTEGER NOT NULL DEFAULT 0;

DO $$
BEGIN
  IF NOT EXISTS (SELECT 1 FROM pg_constraint
    WHERE conrelid = 'public.user_settings'::regclass
      AND conname = 'user_settings_milestone_reminder_lead_time_minutes_valid') THEN
    ALTER TABLE public.user_settings
      ADD CONSTRAINT user_settings_milestone_reminder_lead_time_minutes_valid
      CHECK (milestone_reminder_lead_time_minutes BETWEEN 0 AND 43200);
  END IF;
  IF NOT EXISTS (SELECT 1 FROM pg_constraint
    WHERE conrelid = 'public.tasks'::regclass AND conname = 'tasks_category_valid') THEN
    ALTER TABLE public.tasks ADD CONSTRAINT tasks_category_valid
      CHECK (category IS NULL OR category IN ('Learning', 'Work', 'Personal'));
  END IF;
  IF NOT EXISTS (SELECT 1 FROM pg_constraint
    WHERE conrelid = 'public.garden_states'::regclass
      AND conname = 'garden_states_growth_points_valid') THEN
    ALTER TABLE public.garden_states ADD CONSTRAINT garden_states_growth_points_valid
      CHECK (growth_points >= 0);
  END IF;
END;
$$;
COMMIT;
```

`IF NOT EXISTS` preserves any already-present definition; inspect existing columns/constraints if a local database previously received different definitions. Invalid existing values cause validation to fail without dropping or rewriting them. Fresh installations receive these definitions directly from `01_users_and_auth.sql`, `04_tasks_and_dependencies.sql`, and `08_heart_and_garden.sql`; this final pass preserves those files unchanged.

## Checks performed (2026-09-17)

| Check | Result |
| --- | --- |
| `python -m compileall .` from backend | Passed |
| `uvx ruff check` on all changed backend production files | Passed; no repository dependency added |
| `uvx ruff format --check` on garden_service.py and Goals/Reminders routes | Passed, 3 files; baseline formatting retained in unrelated AST-identical definitions |
| Optional `uvx ruff check backend --output-format json` from root | 136 pre-existing findings in 35 unchanged files; verified none occur in this pass's modified files. Not reported as passing |
| FastAPI import, TestClient lifespan/startup/shutdown, OpenAPI and HTTP health checks | Passed; 34 registered paths, including Today/Goals/Reminders; health and database health HTTP 200 |
| SQLAlchemy / PostgreSQL schema inspection | 22 mapped tables/columns, all 96 explicitly named constraints, 29 explicit indexes, 13 triggers; invalid values rejected by all three new checks |
| Python type checker / backend pytest | No configured checker and no historical backend tests remain; not claimed as passed |
| Direct SQL installer, PostgreSQL 17 disposable tmpfs container | Passed |
| `psql -v ON_ERROR_STOP=1 -f database/tests/00_schema_smoke_test.sql` | Passed; historical test corrected to reward_events and water_balance, sample data rolled back |
| Prettier + Svelte plugin check on changed production frontend files | Passed; temporary npm cache tooling, no dependency or formatter config added |
| Frontend linter | No repository ESLint configuration/script exists; Svelte/TypeScript check used |
| `npm run check` | Passed: zero errors and warnings |
| Full `npm run test` | Passed: 22 files, 154 tests; no exclusions, skips or suppressed failures |
| `npm run build` | Passed |
| `cargo fmt --check` | Passed |
| `cargo clippy --all-targets --all-features -- -D warnings` | Passed |
| `cargo build` | Passed; no installer or app launch |
| `cargo test` | Passed: 0 tests in library, binary and doc-test targets; not native runtime verification |

The complete unfiltered suite passes after correcting TodayView's obsolete Work expectation to Uncategorized. Existing jsdom canvas warnings remain; no new dependencies or test exclusions suppress them. An earlier exploratory browser command used an incorrect Replan selector; the corrected exercise passed. No repository lint/formatter configuration exists; Ruff uses available tooling/user defaults, and Prettier was invoked from its existing npm cache.

## Final corrective exercises

Executed ad hoc against a separate PostgreSQL 17 container (`blooming-corrective-audit-20260917`, tmpfs storage, loopback port 15439), with no developer volume mounted:

- GardenState created by a read persists across sessions. A reward-created state and ledger/balances roll back together. Reward helpers issue no commits.
- Unlock, select, water and an idempotent repeated unlock each commit exactly once. Repeated and five simultaneous original-key awards produce one award.
- All authoritative SQL files install; the historical smoke test passes and rolls back its sample data. Schema names and the three new constraint rejection paths pass.
- The exact additive SQL documented above was applied twice to a separate disposable pre-feature schema. Existing task/garden/settings rows and balances survived, default values were backfilled, and the repeated application succeeded.
- Repository-wide search finds no remaining complete_milestone imports/calls. Startup exposed broken get_db imports in Goals/Reminders; both now use the shared SessionDep/CurrentUser dependencies and startup passes.

Executed in headless Chromium with in-memory API/native failure injection, with no test/helper files retained:

- Task save updates local state and closes the editor despite event failure. API failure keeps the editor and draft open and emits no event.
- Replan updates from its API response and shows a synchronization warning on native failure. Focus remains started and Start is disabled when event emission and widget display fail.
- One mutation and one event attempt per action; exactly two Today GETs across initial load, save, Replan and Focus (initial load and Focus refresh).
- Garden unlock/select/water update local balances/selection/vitality and retain success with separate warnings when native events fail.
- Failed Settings API save restores both previous native values and shows no success. Post-save local preference failure retains success with a separate warning.

These checks do not establish real native IPC, tray appearance, OS autostart or window lifecycle behavior.

The temporary frontend server was stopped and the disposable PostgreSQL container removed itself on stop (`--rm`). The existing blooming-postgres container and its volume remain untouched.

## Earlier implementation database exercises

These were ad hoc calls against the disposable schema, not new test files:

- Category and notes save and explicitly clear to NULL.
- Task completion and repeated original idempotency key award one Leaves event and one growth increment. Five simultaneous award calls also awarded once.
- All growth_stage boundaries: 0/99, 100/299, 300/699, 700.
- Milestone creation, deadline edits, zero lead time, settings changes, completion and reopening reuse the same reminder and preserve the real deadline.
- Quiet-hour same-day/overnight boundaries, configured timezone, invalid timezone fallback and enable/disable behavior; suppressed reminders retain status.
- Replan preserves completed block ID, position, timestamps and completion timestamp. Capacity failure honors edited duration and leaves existing blocks intact.
- Focus start/finish works against the direct schema; completion reuses task reward keys and awards Water once. Empty focus/reminder action payloads are JSON objects, satisfying existing SQL constraints.

## Earlier implementation browser exercises

Headless Chromium against the running frontend with in-memory HTTP responses (no fixture or test files retained):

- Save failure shows an accessible error and retains the open edit draft.
- Clearing category sends NULL and Notes send the edited description.
- Replan failure is visible; the action sends one request.
- Authoritative selected sunflower with BLOOMING and full vitality renders atlas frame 7.
- Missing garden data renders the neutral Plant unavailable state.
- Expired countdown enters ending state; three immediate Done clicks result in one finish request.

All five sprite atlases and the tray red-dot asset were visually inspected. Browser checks do not establish native Tauri behavior or full live API/UI integration.

## Manual native checks still pending

- [ ] Start the actual Tauri app against a manually updated local database. Confirm exactly one tray icon; left click and Open Blooming show/unminimize/focus main; Show companion opens/focuses the companion.
- [ ] Close main and companion separately: both hide and the app remains available. Close an auxiliary window: it closes normally. Tray Quit exits the whole process, including with auxiliary windows open; no tray remains.
- [ ] Save a Today task and Replan: UI updates once and the widget receives one event. Force event rejection after API success: save editor closes, Replan stays successful, and a non-fatal warning appears. Force API failure: draft stays open and no event fires.
- [ ] Start Focus successfully while widget show/focus or event emission fails: session remains started, Start cannot repeat it, and a warning appears. API rejection shows a real failure. Complete the session in the widget and confirm main refreshes once and allows the next start.
- [ ] Unlock/select/water once: local garden updates once and widget receives one event. Force native failure after each API success: balances/selection/vitality retain the successful result and warnings do not invite a retry.
- [ ] Snapshot actual autostart/always-on-top; change both and fail the Settings API save: both native values restore and no success appears. Exercise partial native failure/failed compensation and verify accessible warnings. Verify successful settings persist and actual OS login/autostart works.
- [ ] With main hidden, verify one reminder polling owner in companion, including when hidden. Due reminders set the red dot; clearing/dismissing clears it; quiet hours suppress it without completing reminders. Main/auxiliary windows must not add reminder polls.
- [ ] Induce root native errors and verify transparent widget dimensions/layout do not shift or expand; main warnings remain accessible via status/alert regions. Exercise countdown completion through sleep/wake and rapid Done clicks without duplicate events/mutations.

Native runtime checks were not performed: this session has command execution and headless Chromium but no interactive native UI inspection/control, and the developer database was intentionally left unchanged. The corresponding tasks remain open; cargo build/test are not substitutes.

## Cleanup audit

The preceding pass removed fix.py, both feature Alembic revisions, three new backend test files, spriteMapper.test.ts and unused platform/events.ts, and restored editor files/root package-lock churn. This pass removes only the three leftover generated test bytecode files under backend/tests: test_reminder_service, test_garden_service and test_tasks (`cpython-310-pytest-7.4.3.pyc`). No production source file or historical test was deleted.

TodayView.test.ts now expects Uncategorized when its API fixture has no category and no longer prints mock debug output. SettingsState.test.ts retains its existing numeric lead-time adaptation. No new test files, fixtures, helper scripts, dependencies or migrations were added. AST-identical backend definitions were restored to their original formatting; functional edits were preserved.

The previously unused api/types.ts is now the consumed shared contract; it is no longer a duplicate unused file. The red-dot asset remains because it is valid, referenced by Rust and included in bundle resources. Repository searches found no new any/as-any, feature migrations/tests, production GROWTH currency events, obsolete reminder-time keys, browser CustomEvent transport or sensitive verification-link output. Plant species names remain only in canonical types/atlas maps and explicit preview fixtures; the production live-draft placeholder uses a neutral document icon. The existing Mr. Bloom animation's frame zero is a character animation, not a hard-coded plant.

No commit, push, reset, developer database recreation or Docker volume deletion was performed by this agent. No before/after implement extension hooks are configured.

## Files changed in this final pass

Paths are relative to the repository root; earlier implementation changes remain preserved.

| Purpose | Files |
| --- | --- |
| Garden persistence/transactions | `backend/app/services/garden_service.py` |
| Startup/session dependencies | `backend/app/api/routes/goals.py`, `backend/app/api/routes/reminders.py` |
| Today success/warnings and category test | `frontend/src/routes/(app)/today/+page.svelte`, `frontend/src/lib/features/today/components/organisms/RightRail.svelte`, `frontend/src/lib/features/today/TodayView.test.ts` |
| Garden success/warnings | `frontend/src/lib/features/garden-selection/model/state.svelte.ts`, `frontend/src/lib/features/garden-selection/components/organisms/GardenSelectionContent.svelte` |
| Settings compensation/warnings | `frontend/src/lib/features/settings/model/SettingsState.svelte.ts`, `frontend/src/lib/features/settings/components/molecules/SettingsActionGroup.svelte` |
| Native settings/events, tray/lifecycle, root layout | `frontend/src/lib/platform/desktopWindow.ts`, `frontend/src-tauri/src/lib.rs`, `frontend/src/routes/+layout.svelte` |
| Historical SQL smoke test | `database/tests/00_schema_smoke_test.sql` |
| Remove formatting-only churn from unchanged definitions | `backend/app/api/routes/today.py`, `backend/app/crud/crud_daily_plan.py`, `backend/app/crud/crud_task.py`, `backend/app/db/models/garden.py`, `backend/app/db/models/users.py`, `backend/app/schemas/planning.py`, `backend/app/services/focus_service.py`, `backend/app/services/goals_service.py`, `backend/app/services/user_settings_service.py` |
| Documentation | `backend/README.md`, `database/README.md`, `specs/019-cleanup-integration/contracts/api.md`, `specs/019-cleanup-integration/data-model.md`, `specs/019-cleanup-integration/plan.md`, `specs/019-cleanup-integration/tasks.md`, `specs/019-cleanup-integration/quickstart.md` |

The three authoritative SQL definition files remain the feature's only schema changes: `database/migrations/01_users_and_auth.sql`, `database/migrations/04_tasks_and_dependencies.sql`, `database/migrations/08_heart_and_garden.sql`. No additional SQL definition changes were needed in this final pass.
