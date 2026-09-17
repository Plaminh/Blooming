# Implementation Plan: Corrective integration cleanup

Frontend: SvelteKit / Svelte 5 / TypeScript. Backend: FastAPI / Pydantic / SQLAlchemy / PostgreSQL. Desktop: Tauri 2 / Rust.

## Scope and governance

The user's corrective decision overrides the constitution's new-test requirement for this feature: remove feature-specific tests, retain historical tests, and validate through static checks, builds, unaffected tests and manual exercises. No commit or push. Never recreate the developer database volume automatically.

## Implementation order

1. Audit the diff, remove the two feature Alembic revisions, test-only additions, rewrite scripts and unused event contracts; restore editor files and unrelated root lockfile churn.
2. Edit the authoritative CREATE TABLE files in `database/migrations/` directly: `01_users_and_auth.sql`, `04_tasks_and_dependencies.sql`, `08_heart_and_garden.sql`. No feature Alembic migration and no baseline revision edits. Keep existing currency, plants, ownership and legacy stage intact.
3. Synchronize ORM and Pydantic contracts. Task category is Learning, Work, Personal or NULL. Growth points are nonnegative; expose `growth_stage` separately from persisted `stage`: SPROUTING 0-99, GROWING 100-299, BLOOMING 300-699, FLOURISHING 700+. Reminder lead time is 0-43200 minutes, default 1440.
4. Repair `PATCH /api/v1/today/tasks/{task_id}` and `POST /api/v1/today/replan`. Use the deterministic scheduler, preserve completed/active/locked/fixed blocks and surface failures. Emit Tauri schedule events only following successful API operations.
5. Award task growth (10) or milestone growth (50) directly with the eligible Leaves ledger entry, reusing original completion keys. Serialize balance updates and never commit in reward helpers. No GROWTH currency.
6. Synchronize milestone reminders on creation, deadline/title/status edits and lead-time changes. Preserve `original_due_at` as deadline; `due_at` is deadline minus lead time. Quiet hours use UserSettings timezone and enable flag, inclusive start/exclusive end, same-day/overnight, invalid-zone UTC fallback, without status mutation on suppression.
7. Share typed API contracts and atlas-backed species/stage/vitality mapping. Unknown/unavailable garden data renders a neutral fallback. Task edit drafts survive errors; title, duration, category and notes use one request contract. Countdown transition is guarded in an effect, never derived computation.
8. Extend the existing typed `platform/desktopWindow.ts` wrapper for events, autostart, always-on-top and tray state. Reconcile actual native state, propagate failures. Poll from the root application layout in the companion window; keep it alive when hidden. Rust creates one clickable tray and propagates command errors. No native notification popup or Rust reminder scheduler.

## Validation

Use Python compile, Ruff lint on changed production files and format checks on substantially edited files, FastAPI import/lifespan/route checks, SQLAlchemy metadata inspection, disposable PostgreSQL initialization and direct service exercises. Preserve baseline formatting in unchanged backend definitions. No backend test files remain; no Python type checker is configured. Frontend: `npm run check`, the complete unfiltered `npm run test`, production build; no repository formatter/linter script is configured. Rust: `cargo fmt --check`, `cargo clippy --all-targets --all-features -- -D warnings`, `cargo build`, and `cargo test` (zero tests is not native runtime evidence).

Record actual results and manual runtime gaps in quickstart.md. Native runtime tasks stay open until exercised. Existing local databases must be manually updated or recreated for direct SQL-file changes to take effect; CREATE TABLE IF NOT EXISTS does not alter existing tables.
