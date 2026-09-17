# Tasks: goals-milestones-reminders

**Input**: Design documents from `/specs/015-goals-milestones-reminders/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/api.md, quickstart.md

## Phase 1: Setup and repository alignment

**Purpose**: Initial project verification and scaffolding.

- [x] T001 Inspect current Goal, Milestone, Reminder, and Plan database constraints in `backend/app/db/models/` to ensure safe operation.
- [x] T002 Inspect `frontend/src/lib/api.ts` to confirm the API client works for the new endpoints.

---

## Phase 2: Shared foundations

**Purpose**: Core backend routing and schema setup needed across multiple stories.

- [x] T003 Create `backend/app/schemas/goals.py` with `GoalCreate`, `GoalUpdate`, `GoalResponse` Pydantic models.
- [x] T004 Create `backend/app/schemas/reminders.py` with `ReminderResponse` and `ReminderActionRequest` Pydantic models.
- [x] T005 [P] Create `backend/app/api/routes/reminders.py` and register it in `backend/app/api/main.py`.
- [x] T006 [P] Create `frontend/src/lib/features/goals/stores/goalsStore.ts` to manage goals, milestones, and reminders.

---

## Phase 3: Manual Goal CRUD (Priority: P1) [US1]

**Goal**: Implement backend and frontend to support creating, updating, listing, and deleting goals.
**Independent Test**: Can manually create, edit, and delete a goal via the Goals/Roadmap UI, and verify changes persist after reload.

- [x] T007 [US1] Create `backend/app/services/goals_service.py` with Goal CRUD methods enforcing `user_id` ownership.
- [x] T008 [US1] Implement endpoints in `backend/app/api/routes/goals.py` for Goal CRUD operations.
- [x] T009 [P] [US1] Create `backend/tests/api/routes/test_goals.py` with Goal CRUD and ownership tests. (Removed during cleanup)
- [x] T010 [US1] Update `frontend/src/lib/features/goals/stores/goalsStore.ts` with API calls for Goal CRUD.
- [x] T011 [US1] Refactor `frontend/src/routes/(app)/goals/+page.svelte` to load real goals from `goalsStore` instead of `FIXTURE_GOALS`.
- [x] T012 [US1] Wire up Goal edit and delete actions in `frontend/src/lib/features/goals/components/organisms/GoalDetailsPanel.svelte` and `GoalsRightRail.svelte`.

---

## Phase 4: Manual Milestone CRUD (Priority: P1) [US2]

**Goal**: Manage milestones within a goal, including status and date updates.
**Independent Test**: Can add a milestone to a goal, edit its status and target date, and see changes immediately on the UI.

- [x] T013 [P] [US2] Add `MilestoneCreate`, `MilestoneUpdate`, `MilestoneResponse` schemas to `backend/app/schemas/goals.py`.
- [x] T014 [US2] Implement Milestone CRUD methods in `backend/app/services/goals_service.py` (enforce goal ownership, validate milestone position).
- [x] T015 [US2] Implement Milestone endpoints in `backend/app/api/routes/goals.py` (`POST`, `PUT`, `DELETE`).
- [x] T016 [US2] Add Milestone tests to `backend/tests/api/routes/test_goals.py`. (Removed during cleanup)
- [x] T017 [US2] Add Milestone API methods to `frontend/src/lib/features/goals/stores/goalsStore.ts`.
- [x] T018 [US2] Update `frontend/src/lib/features/goals/components/organisms/GoalDetailsPanel.svelte` (or appropriate sub-component) to handle milestone creation, status updates, and deletion using the store.

---

## Phase 5: Due reminders (Priority: P2) [US3]

**Goal**: Load and display currently due reminders for the authenticated user.
**Independent Test**: `GET /reminders/due` returns only reminders matching the time criteria and the UI renders them gracefully.

- [x] T019 [US3] Create `backend/app/services/reminders_service.py` and implement `get_due_reminders(user_id)` (filters: status IN `SCHEDULED`, `DUE`; `due_at` <= now()).
- [x] T020 [US3] Implement `GET /reminders/due` in `backend/app/api/routes/reminders.py`.
- [x] T021 [P] [US3] Create `backend/tests/api/routes/test_reminders.py` testing due filtering and boundary times. (Removed during cleanup)
- [x] T022 [US3] Create `frontend/src/lib/features/goals/components/organisms/DueRemindersPanel.svelte` mimicking the style of `NextMilestonePanel`.
- [x] T023 [US3] Add `loadDueReminders` to `goalsStore.ts` and integrate `DueRemindersPanel.svelte` into `frontend/src/lib/features/goals/components/organisms/GoalsRightRail.svelte`.

---

## Phase 6: Reminder actions (Priority: P2) [US4]

**Goal**: Execute actions on due reminders (Create Plan, Mark Completed, Move Milestone, Remind Later) safely and idempotently.
**Independent Test**: Clicking an action successfully updates backend state (e.g. milestones/plans) and removes the reminder from the due list.

- [x] T024 [US4] Add `execute_action` logic to `backend/app/services/reminders_service.py` handling `CREATE_PLAN`, `MARK_COMPLETED`, `MOVE_MILESTONE`, and `REMIND_LATER`. Ensure transactional behavior.
- [x] T025 [US4] Implement `POST /reminders/{reminder_id}/actions` in `backend/app/api/routes/reminders.py`.
- [x] T026 [US4] Add action idempotency, rollback, and duplication tests to `backend/tests/api/routes/test_reminders.py`. (Removed during cleanup)
- [x] T027 [US4] Add `executeReminderAction` to `frontend/src/lib/features/goals/stores/goalsStore.ts`.
- [x] T028 [US4] Wire up the four action buttons in `DueRemindersPanel.svelte`, disabling buttons while pending and updating local state upon success.

---

## Phase 7: Integration and demo readiness

**Purpose**: Confirm all flows work together and eliminate mock dependencies from the execution path.

- [x] T029 Remove the `FIXTURE_GOALS` variable from `frontend/src/routes/(app)/goals/+page.svelte` so the application runs strictly on real data.
- [ ] T030 Perform manual end-to-end checklist defined in `quickstart.md` (Create goal, edit milestone, handle reminder action, verify persistence after restart).

---

## Phase 8: Final validation

**Purpose**: Ensure CI/CD requirements are met and no regressions are introduced.

- [ ] T031 [P] Run backend validation: `poe check` (lint/type) and `poe test` (pytest).
- [ ] T032 [P] Run frontend validation: `npm run lint` and `npm run check`.
- [ ] T033 [P] Build frontend to verify Tauri compilation: `npm run build`.

---

## Dependencies & Execution Order

- **Setup & Foundations (Phase 1-2)**: Must be completed first.
- **Manual Goal CRUD (Phase 3)**: Unblocks Milestone CRUD.
- **Manual Milestone CRUD (Phase 4)**: Must follow Phase 3.
- **Due Reminders (Phase 5)**: Can be started in parallel with Phase 4, but depends on basic Goal/Milestone domain knowledge.
- **Reminder Actions (Phase 6)**: Must follow Phase 5 and relies on Phase 4's Milestone endpoints.
- **Integration & Validation (Phase 7-8)**: Executed after all features are implemented.

### Parallel Opportunities

- **T003, T004, T005, T006** can be performed concurrently.
- **T009, T013, T021** (tests/schemas) can be written alongside service logic.
- **Phase 8** tasks (validation) can be run concurrently.

### Implementation Strategy

- Implement Phase 3 (Goal CRUD) and test manually before starting Milestone CRUD.
- Implement Phase 4 (Milestone CRUD) and verify the Goals UI looks perfect with real data.
- Then tackle the Reminders backend and frontend, ensuring Reminder Actions gracefully modify the state of Milestones.
