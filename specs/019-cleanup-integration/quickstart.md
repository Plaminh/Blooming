# Validation guide and corrective cleanup record

## Database setup

The authoritative installer is `psql -v ON_ERROR_STOP=1 -f database/install.sql` against a fresh disposable database. The three CREATE TABLE changes are category VARCHAR(50) NULL (Learning/Work/Personal or NULL), growth_points INTEGER NOT NULL DEFAULT 0 (>=0), and milestone_reminder_lead_time_minutes INTEGER NOT NULL DEFAULT 1440 (0-43200).

No feature Alembic migration exists. Do not run a feature migration or edit the historical baseline. Existing local databases must be manually updated or recreated before these fields take effect. CREATE TABLE IF NOT EXISTS does not update existing tables. The developer volume was not modified or recreated.

## Checks performed (2026-09-17)

| Check | Result |
| --- | --- |
| Python `compileall -q backend/app` | Passed |
| Ruff check and format --check on changed backend production files | Passed; temporary tool installation, no repository dependency added |
| SQLAlchemy metadata inspection | 22 tables loaded; three added columns, defaults and checks present |
| Python type checker / backend pytest | No configured checker and no historical backend tests remain; not claimed as passed |
| Direct SQL installer, PostgreSQL 17 disposable tmpfs container | Passed |
| Existing SQL smoke test | Failed: it expects pre-existing legacy heart_events, already absent from the authoritative SQL before this feature; preserved unchanged |
| Prettier + Svelte plugin check on changed production frontend files | Passed; temporary npm cache tooling, no dependency or formatter config added |
| Frontend linter | No repository ESLint configuration/script exists; Svelte/TypeScript check used |
| `npm run check` | Passed: zero errors and warnings |
| Full existing `npm run test` | One failure: unchanged TodayView test expects fabricated Work for a block with no category |
| `npm run test -- --exclude src/lib/features/today/TodayView.test.ts --maxWorkers=2` | 21 files, 150 tests passed; includes minimally adapted SettingsState numeric-field checks |
| `npm run build` | Passed |
| `cargo fmt --check` | Passed |
| `cargo clippy --all-targets --all-features -- -D warnings` | Passed |
| `cargo build` | Passed; no installer or app launch |
| `cargo test` | No historical Rust tests found; not claimed as runtime verification |

An initial concurrent frontend subset run timed out in an unchanged onboarding test while Rust compiled. Repeating with two workers passed all 150 tests. Existing jsdom canvas warnings remain; no new test dependencies were installed to suppress them.

## Direct database exercises completed

These were ad hoc calls against the disposable schema, not new test files:

- Category and notes save and explicitly clear to NULL.
- Task completion and repeated original idempotency key award one Leaves event and one growth increment. Five simultaneous award calls also awarded once.
- All growth_stage boundaries: 0/99, 100/299, 300/699, 700.
- Milestone creation, deadline edits, zero lead time, settings changes, completion and reopening reuse the same reminder and preserve the real deadline.
- Quiet-hour same-day/overnight boundaries, configured timezone, invalid timezone fallback and enable/disable behavior; suppressed reminders retain status.
- Replan preserves completed block ID, position, timestamps and completion timestamp. Capacity failure honors edited duration and leaves existing blocks intact.
- Focus start/finish works against the direct schema; completion reuses task reward keys and awards Water once. Empty focus/reminder action payloads are JSON objects, satisfying existing SQL constraints.

## Browser exercises completed

Headless Chromium against the running frontend with in-memory HTTP responses (no fixture or test files retained):

- Save failure shows an accessible error and retains the open edit draft.
- Clearing category sends NULL and Notes send the edited description.
- Replan failure is visible; the action sends one request.
- Authoritative selected sunflower with BLOOMING and full vitality renders atlas frame 7.
- Missing garden data renders the neutral Plant unavailable state.
- Expired countdown enters ending state; three immediate Done clicks result in one finish request.

All five sprite atlases and the tray red-dot asset were visually inspected. Browser checks do not establish native Tauri behavior or full live API/UI integration.

## Manual native checks still pending

1. Run the actual Tauri application using a manually updated local database. Confirm a main-window schedule edit/Replan/focus start refreshes the widget through Tauri events, and focus-start failures are visible.
2. Toggle always-on-top and verify both the actual window flag and visible error recovery when native access fails.
3. Toggle Start at login; confirm reconciliation with OS state, error handling, persistence and a real login cycle.
4. With the main window closed/hidden, confirm application-root polling continues; due reminders show the red dot, clearing/dismissing them clears it, and quiet hours suppress it without completing reminders.
5. Click the tray icon and confirm main is shown, unminimized and focused. Confirm exactly one tray.
6. Exercise timer completion during sleep/wake and real window events; browser duplicate-click validation is complete but desktop lifecycle verification is pending.

## Cleanup audit

Removed fix.py, both feature Alembic revisions, three new backend test files, spriteMapper.test.ts and unused platform/events.ts. Restored TodayView.test.ts exactly, restored both frontend/.vscode files and root package-lock.json. SettingsState.test.ts retains only the required adaptation from obsolete string reminder time to numeric lead time, preserving its historical cases. No replacement tests, fixtures, test helpers or dependencies were added.

The previously unused api/types.ts is now the consumed shared contract; it is no longer a duplicate unused file. The red-dot asset remains because it is valid, referenced by Rust and included in bundle resources. Repository searches found no new any/as-any, feature migrations/tests, production GROWTH currency events, obsolete reminder-time keys, browser CustomEvent transport or sensitive verification-link output. Plant species names remain only in canonical types/atlas maps and explicit preview fixtures; the production live-draft placeholder uses a neutral document icon. The existing Mr. Bloom animation's frame zero is a character animation, not a hard-coded plant.

No commit or push was performed. No before/after implement extension hooks are configured.
