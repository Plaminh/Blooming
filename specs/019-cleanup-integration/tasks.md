# Tasks: Full-Stack Cleanup and Missing Integration Completion

**Input**: Design documents from `/specs/019-cleanup-integration/`

**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md, contracts/, quickstart.md

**Validation decision**: No new feature-specific test files. Preserve historical tests; only adapt a pre-existing test where an intentional production type change requires it. Validate with static checks, builds, unaffected tests and recorded manual flows.

**Organization**: Tasks are grouped by user story and phase to enable independent implementation and testing of each story.

## Phase 1: Baseline and safety (Shared Infrastructure)

**Purpose**: Confirm the active feature artifacts, constitution, and current state.

- [x] T001 Record the current migration head and check status in `backend/alembic/versions/` and log.
- [x] T002 [P] Search for hard-coded plant species and sprite frames in `frontend/src/`.
- [x] T003 [P] Search for hard-coded task categories and obsolete `blooming:*` events in `frontend/src/`.
- [x] T004 [P] Search for milestone-reminder localStorage keys in `frontend/src/`.
- [x] T005 [P] Audit `backend/tests/`: no historical backend tests remain after removing feature-only files; do not claim pytest passed.
- [x] T006 [P] Run and record existing frontend checks/build/tests in `frontend/`; report the unchanged TodayView expectation failure in quickstart.md.
- [x] T007 [P] Run and record Rust formatting, strict Clippy and safe build in `frontend/src-tauri/`; no historical Rust tests found.

---

## Phase 2: Contract foundations (Blocking Prerequisites)

**Purpose**: Update API/native contracts and shared typed models.

- [x] T012 [P] Update API client contracts for `Category` and `GardenState` in `frontend/src/lib/api/types.ts` (or equivalent).
- [x] T013 [P] Define `blooming:schedule-updated` Tauri event typed payload in `frontend/src/lib/platform/desktopWindow.ts` (or equivalent).

---

## Phase 3: Direct SQL schema and models

**Purpose**: Edit authoritative CREATE TABLE definitions directly and synchronize ORM models. No feature Alembic migration; preserve the baseline.

- [x] T014 Modify existing `database/migrations/01_users_and_auth.sql`, `04_tasks_and_dependencies.sql`, and `08_heart_and_garden.sql` directly for `category` in `tasks`, `growth_points` in `garden_states`, and `milestone_reminder_lead_time_minutes` in `user_settings`.
- [x] T015 Update `Task` model in `backend/app/db/models/tasks.py` with `category` field.
- [x] T016 Update `GardenState` model in `backend/app/db/models/garden.py` with `growth_points` field.
- [x] T017 Update `UserSettings` model in `backend/app/db/models/users.py` with `milestone_reminder_lead_time_minutes` field.
- [x] T018 Update Pydantic schemas in `backend/app/schemas/` to reflect model changes.
- [x] T019 Initialize the SQL schema in an isolated disposable PostgreSQL database and inspect SQLAlchemy metadata; never alter the developer volume.

---

## Phase 4: User Story 1 - Today Page Actions (Priority: P1)

**Goal**: The Edit and Replan actions on the Today page perform real operations and refresh the schedule.

**Independent Test**: Edit a block's title/notes and Replan unfinished blocks, ensuring backend updates and UI refreshes via Tauri event.

### Implementation for User Story 1

- [x] T020 [US1] Expose Replan endpoint (`POST /api/v1/today/replan`) in `backend/app/api/routes/today.py` using the deterministic scheduler.
- [x] T021 [US1] Update task update flow (`PATCH /api/v1/today/tasks/{task_id}`) to handle `description` (Notes) and `category` in `backend/app/api/routes/today.py` and `today_service.py`.
- [x] T022 [US1] Wire Today page Edit UI to map `description` to Notes and save via API in `frontend/src/routes/(app)/today/+page.svelte` and related components.
- [x] T023 [US1] Wire Today page Replan action to the real backend endpoint in `frontend/src/routes/(app)/today/+page.svelte`.
- [x] T024 [US1] Replace fake Category/Notes mappings and show `Uncategorized` for `NULL` categories in `frontend/src/lib/features/today/types.ts` and UI components.
- [ ] T025 [US1] Emit `blooming:schedule-updated` Tauri event from main window on successful Replan and Focus Start in `frontend/src/routes/(app)/today/+page.svelte`.
- [ ] T026 [US1] Listen to Tauri event `blooming:schedule-updated` in the companion widget `frontend/src/routes/widget/+page.svelte` to refresh data.

---

## Phase 5: User Story 2 - Accurate Garden State (Priority: P1)

**Goal**: Plant's actual species, growth stage, and vitality reflect in the widget and garden views based on thresholds.

**Independent Test**: Complete a task to earn points, then verify the garden and widget views display the derived valid sprite frames.

### Implementation for User Story 2

- [x] T027 [US2] Centralize growth point thresholds (`SPROUTING`, `GROWING`, `BLOOMING`, `FLOURISHING`) and reward amounts in `backend/app/services/garden_service.py`.
- [x] T028 [US2] Implement atomic growth award logic for eligible task/milestone completion in `backend/app/services/garden_service.py`.
- [x] T029 [US2] Update Garden API response to expose `growth_points` and derived `growth_stage` in `backend/app/api/routes/garden.py`.
- [x] T030 [US2] Add shared sprite-frame mapping utility in `frontend/src/lib/features/garden/utils/spriteMapper.ts` that maps species and growth stage to exact frames based on actual sprite atlas dimensions.
- [x] T031 [US2] Update widget view (`frontend/src/routes/widget/+page.svelte`) and garden view to load authoritative selected-plant state and use the sprite-frame mapping, removing hardcoded `monstera` and frame `0`.

---

## Phase 6: User Story 3 - Milestone Reminders & Quiet Hours (Priority: P2)

**Goal**: Milestone reminders trigger at correct lead times and respect quiet hours.

**Independent Test**: Set lead time to 1 day before, configure quiet hours to an overnight range, and verify reminder evaluation correctly offsets time and suppresses notification.

### Implementation for User Story 3

- [x] T033 [P] [US3] Add a pure local-time interval helper for quiet hours in `backend/app/core/time_utils.py`.
- [x] T034 [US3] Implement quiet hours suppression logic using IANA timezone in `backend/app/services/reminders_service.py` during polling evaluation.
- [x] T035 [US3] Implement milestone reminder lead time calculation without modifying milestone deadlines in `backend/app/services/reminders_service.py` and `backend/app/services/goals_service.py`.
- [x] T036 [US3] Persist and load milestone reminder lead time in Settings UI (`frontend/src/lib/features/settings/components/organisms/NotificationsPanel.svelte`), presenting clear choices (e.g., 24h).
- [x] T037 [US3] Remove obsolete milestone-reminder localStorage keys and compatibility state from frontend stores/utils.

---

## Phase 7: User Story 4 - Desktop Integrations (Priority: P2)

**Goal**: Implement Start at login, Always-on-top, and a tray icon indicator.

**Independent Test**: Toggle autostart/always-on-top to verify behavior, and create a due reminder to verify the tray icon changes to a red-dot variant.

### Implementation for User Story 4

- [x] T038 [US4] Add `tauri-plugin-autostart` dependency in `frontend/src-tauri/Cargo.toml` and register plugin in `lib.rs`.
- [x] T039 [US4] Add Tauri capabilities/permissions for always-on-top and autostart in `frontend/src-tauri/tauri.conf.json` or `capabilities/`.
- [ ] T040 [US4] Add frontend native wrapper in `frontend/src/lib/platform/desktopWindow.ts` to sync Settings UI toggles (Always-on-top, Start at login) with Tauri APIs.
- [ ] T041 [US4] Create exactly one tray instance using `tauri` tray API in `frontend/src-tauri/src/lib.rs`, reusing the Blooming leaf icon.
- [ ] T042 [US4] Add centralized Rust tray-state command in `lib.rs` to toggle normal and red-dot tray assets.
- [ ] T043 [US4] Call tray-state command from frontend reminder evaluation loop to set red-dot when reminders are due and clear when empty.

---

## Phase 8: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories and final cleanup.

- [ ] T044 [P] Ensure focus-session start errors surface via `aria-live` or toast in `frontend/src/routes/(app)/today/+page.svelte`.
- [x] T045 [P] Prevent repeated widget countdown transitions and completion calls; verify in browser (native sleep/wake remains a manual gate) in `frontend/src/routes/widget/+page.svelte`.
- [x] T046 [P] Suppress verification links and sensitive values in backend production output (`backend/app/core/logging.py` or equivalent).
- [x] T047 [P] Remove obsolete `blooming:*` CustomEvent dispatch/listener logic entirely from the frontend.
- [x] T048 [P] Remove dead imports, stale comments, and unreachable code across the repository.
- [ ] T049 Run full verification checks: Python compile and available lint/format checks, unaffected tests, `npm run check`, frontend build, `cargo fmt --check`, strict Clippy, safe Tauri build, and manual native flows.
- [x] T050 Update any API, migration, setup, and architecture documentation that has changed.

---

## Dependencies and validation status

SQL definitions and contracts precede production integrations. No new feature tests or migrations are permitted by the corrective scope decision. Completion boxes are reopened until applicable implementation and validation pass. Native runtime tasks remain open until manually exercised in Tauri; compilation alone is insufficient.

The current validation evidence and outstanding checks are recorded in quickstart.md.


## Completion evidence

All 50 original boxes were reopened during the audit. T008-T011 and T032 were removed because the user prohibits new feature tests. Production/static/direct-database/browser evidence completes the checked tasks above; detailed results are in quickstart.md.

Still open: T025-T026 (real cross-window events), T040-T043 (native settings, tray and background polling), T044 (real focus-start failure flow), and T049 (full verification, including native runtime and historical check failures). Implementations exist, but their required end-to-end evidence is incomplete. Do not mark them complete based only on compilation.
