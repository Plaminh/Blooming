---
description: "Task list template for feature implementation"
---

# Tasks: Pomodoro and Re-planning

**Input**: Design documents from `specs/014-pomodoro-replanning/`

**Prerequisites**: plan.md, spec.md, data-model.md, contracts/focus-api.md, quickstart.md

**Organization**: Tasks are grouped by user story in dependency order to enable independent verification.

## Phase 1: Setup and Schema Prerequisites

**Purpose**: Database and domain foundation verification. Ensure existing models cover the required state and timestamps.

 - [X] T001 Verify `FocusRun` and `FocusRunEvent` models in `backend/app/db/models/focus.py` meet data-model requirements (status, outcomes, timestamps).
 - [X] T002 [P] Verify `Task` and `PlanBlock` fields required for Pomodoro replanning in `backend/app/db/models/tasks.py` and `backend/app/db/models/daily_plans.py`.
 - [X] T003 Verify database migration state matches the approved schema using `alembic check` (or equivalent migration tool command).

---

## Phase 2: Foundational Session Lifecycle/Domain Logic

**Purpose**: Setup the base request/response schemas and repository logic before executing the user stories.

 - [X] T004 Create or verify `FocusSessionStart`, `FocusSessionFinish`, and `FocusRunResponse` schemas in `backend/app/schemas/focus.py`.
 - [X] T005 Implement/verify active session fetching (`get_active_session`) and event logging (`add_event`) in `backend/app/crud/crud_focus.py`.
 - [X] T006 Initialize `FocusService` in `backend/app/services/focus_service.py` to handle core logic separation.
 - [X] T007 Register the `/focus` router in `backend/app/api/main.py` if not already present.

---

## Phase 3: User Story 1 - Start and Restore a Focus Session (Priority: P1)

**Goal**: A user can start a focus session, and it restores safely.
**Independent Test**: API endpoint `/focus/start` creates a running session and rejects duplicate starts. `/focus/active` retrieves it.

 - [X] T008 [US1] Implement `start_session` in `backend/app/services/focus_service.py` verifying no concurrent sessions and returning correct UTC timestamps.
 - [X] T009 [US1] Implement `POST /focus/start` and `GET /focus/active` routes in `backend/app/api/routes/focus.py`.
 - [X] T010 [US1] Implement unit test for starting and retrieving active sessions in `backend/tests/api/routes/test_focus.py`.

---

## Phase 4: User Story 2 - Pause and Resume (Priority: P1)

**Goal**: A running session can be paused and a paused session can be resumed.
**Independent Test**: API endpoints correctly transition states and aggregate `total_paused_seconds`.

 - [X] T011 [US2] Implement `pause_session` in `backend/app/services/focus_service.py`, verifying transition from FOCUSING only.
 - [X] T012 [US2] Implement `resume_session` in `backend/app/services/focus_service.py`, calculating paused duration and updating `expected_end_at`.
 - [X] T013 [US2] Implement `POST /focus/pause` and `POST /focus/resume` routes in `backend/app/api/routes/focus.py`.
 - [X] T014 [US2] Implement unit test for pause/resume lifecycle in `backend/tests/api/routes/test_focus.py`.

---

## Phase 5: User Story 3 - Finish with Outcomes (Priority: P2)

**Goal**: A session can end with DONE, NEED_MORE_TIME, SKIP, or FINISHED_EARLY, updating the task status accurately.
**Independent Test**: The finish API processes the outcome idempotently and modifies the linked task exactly once.

 - [X] T015 [US3] Implement `finish_session` in `backend/app/services/focus_service.py`, tracking actual duration and enforcing correct outcome values.
 - [X] T016 [US3] Update linked `Task` status based on the exact outcome rules within `finish_session` (`backend/app/services/focus_service.py`).
 - [X] T017 [US3] Implement `POST /focus/finish` route in `backend/app/api/routes/focus.py`.
 - [X] T018 [US3] Implement unit tests for all four outcome variants in `backend/tests/api/routes/test_focus.py`.

---

## Phase 6: User Story 4 - Re-plan Remaining Flexible Tasks (Priority: P2)

**Goal**: Upon finishing a session, flexibly shift remaining incomplete tasks.
**Independent Test**: Replanning executes without overlapping, leaves fixed/completed blocks untouched, and handles overflow correctly.

 - [X] T019 [US4] Implement logic to isolate preserved vs flexible tasks in `TodayService.replan_today` (`backend/app/services/today_service.py`).
 - [X] T020 [US4] Feed flexible tasks and constraints to the `DeterministicScheduler` in `TodayService.replan_today` (`backend/app/services/today_service.py`).
 - [X] T021 [US4] Apply new schedule blocks to the database and safely omit overflow tasks without deletion (`backend/app/services/today_service.py`).
 - [X] T022 [US4] Update `finish_session` in `backend/app/services/focus_service.py` to conditionally invoke `replan_today` inside the transaction boundary.
 - [X] T023 [US4] Implement unit test verifying re-planning behavior and protection rules in `backend/tests/services/test_today_service.py`.

---

## Phase 7: Frontend Today/Pomodoro Integration

**Goal**: Expose the backend changes in the client without per-second requests.
**Independent Test**: UI properly maps API state and countdown works autonomously.

 - [X] T024 [P] Update API client calls in `frontend/src/routes/widget/+page.svelte` to match the exact schema.
 - [X] T025 Calculate independent frontend countdown based on exact math formulas derived from `started_at` and `total_paused_seconds` in `frontend/src/routes/widget/+page.svelte`.
 - [X] T026 Wire the four outcome selections (DONE, FINISHED_EARLY, NEED_MORE_TIME, SKIP) in `frontend/src/routes/widget/+page.svelte`.
 - [X] T027 Trigger schedule updates (e.g. interval polling or callback) in `frontend/src/routes/(app)/today/+page.svelte` to reflect replanned timelines.
 - [X] T028 Fix or mock presentation fixtures for testing states in `frontend/src/routes/widget-preview/+page.svelte` and `frontend/src/lib/features/companion-widget/fixtures/`.

---

## Phase 8: End-to-End Verification and Cleanup

**Purpose**: Execute final test suites and validate constraints.

 - [X] T029 Execute all backend tests (`PYTHONPATH=backend pytest backend/tests/`).
 - [X] T030 Execute frontend checks and type validation (`npm run check --prefix frontend`).
 - [X] T031 Execute quickstart.md validation locally to prove End-to-End lifecycle mapping.

---

## Dependencies & Execution Order

### Phase Dependencies
- **Phase 1 & 2**: Foundational - BLOCKS all remaining phases.
- **Phases 3-5 (US1, US2, US3)**: Core focus lifecycle. Highly dependent on each other; implement sequentially to maintain state machine integrity.
- **Phase 6 (US4)**: Replanning depends on the finish session behavior being completed.
- **Phase 7 (Frontend)**: Integrates over the verified backend endpoints. Can be done sequentially after Phase 6.

### Parallel Opportunities
- Data model verifications (T001 and T002) can happen concurrently.
- API UI contract wiring (T024) can happen simultaneously with backend route definitions if using strict typing agreements.
- Fixture creation (T028) can run alongside core frontend timer development (T025).

### MVP Implementation Boundary
**MVP** includes up to Phase 5. Re-planning (Phase 6) operates cleanly on top of the base Pomodoro logic.

### Independent Verification Criteria
- **US1**: Backend returns 200 OK for `POST /focus/start` and accurately queries active session.
- **US2**: `POST /focus/pause` stops timer progression in logic, `POST /focus/resume` advances `expected_end_at`.
- **US3**: `POST /focus/finish` successfully updates `FocusRun` outcome and underlying `Task` status idempotently.
- **US4**: Re-planning leaves passed `PlanBlocks` intact while shifting remaining `PlanBlocks` forward deterministically.

### Definition of Done Checklist
 - [X] A user can start a Pomodoro session from a Today task.
 - [X] A user can pause or resume a session.
 - [X] Reopening the app retains active session state without per-second API requests.
 - [X] The user can finish the session with all 4 supported outcomes.
 - [X] The schedule deterministically re-plans the remaining flexible tasks without overwriting history or protected events.
