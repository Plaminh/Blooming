# Tasks: 016-garden-rewards

**Input**: Design documents from `/specs/016-garden-rewards/`

**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/api.md, quickstart.md

**Organization**: Tasks are grouped by user story and execution phases as specified in the plan.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

---

## Phase 1: Repository and schema alignment

**Goal**: Establish baseline understanding and dependencies without generating arbitrary architecture.

- [x] T001 Verify the active feature is `016-garden-rewards` and inspect current Git state.
- [x] T002 Confirm locations of Garden models (`backend/app/db/models/garden.py`) and routers (`backend/app/api/routes/garden.py`).
- [x] T003 Identify mock-only paths in `frontend/src/lib/features/garden-selection/model/fixtures.ts`.
- [x] T004 Confirm SQL schema update is required for modifying `GardenState` and introducing new tables.

---

## Phase 2: Shared economy and vitality rules

**Goal**: Centralize magic numbers and core calculations.

- [x] T005 Create `backend/app/core/economy.py` to define WATER, LEAVES, and Vitality constants.
- [x] T006 Implement pure timezone-aware vitality calculation function in `backend/app/core/economy.py`.

---

## Phase 3: Database and idempotency foundation

**Goal**: Prepare the database schema for the new feature without breaking existing data.

- [x] T007 Extend `backend/app/db/models/garden.py` to add `Plant` and `PlantOwnership` models with unique constraints.
- [x] T008 Update `GardenState` model in `backend/app/db/models/garden.py` adding `water_balance`, `leaves_balance`, `selected_plant_id`, `last_watered_at` with check constraints for >= 0.
- [x] T009 Refactor `HeartEvent` to `RewardEvent` in `backend/app/db/models/garden.py`, adding `resource_type`, mapping to `amount`, preserving idempotency checks.
- [x] T010 Generate SQL schema update in `backend/alembic/versions/` and verify upgrade/downgrade consistency. (Blocked from running `alembic upgrade head` locally due to no Postgres environment, but migration written.)

---

## Phase 4: Garden state and plant catalog [US1]

**Goal**: Display real persisted state in the UI.

- [x] T011 [US1] Create request/response schemas for Garden and Catalog in `backend/app/schemas/garden.py`.
- [x] T012 [US1] Add `get_garden_state` logic with safe initialization to `backend/app/services/garden_service.py`.
- [x] T013 [US1] Implement `GET /api/garden` in `backend/app/api/routes/garden.py`.
- [x] T014 [US1] Update `frontend/src/lib/features/garden-selection/model/state.svelte.ts` to call the backend instead of `INITIAL_GARDEN_STATE`.
- [x] T015 [US1] Update `GardenSelectionContent.svelte` and `CurrencyBalance.svelte` to bind real Water and Leaves balances and catalog.
- [ ] T016 [US1] Independent Test: An authenticated user can open Garden, view persisted resources, catalog entries, ownership, selected plant, and correctly derived vitality.

---

## Phase 5: Unlock plant [US2]

**Goal**: Allow users to spend Leaves to unlock new plants safely.

- [x] T017 [P] [US2] Add unlock schema in `backend/app/schemas/garden.py`.
- [x] T018 [US2] Implement `unlock_plant` transactional logic in `backend/app/services/garden_service.py`.
- [x] T019 [US2] Add `POST /api/garden/plants/{id}/unlock` route in `backend/app/api/routes/garden.py`.
- [x] T020 [US2] Update `UnlockPanel.svelte` to trigger unlock API and handle pending/success/failure states.
- [ ] T021 [US2] Independent Test: A user can unlock an affordable plant exactly once, while retries do not deduct resources again.

---

## Phase 6: Select plant [US3]

**Goal**: Allow users to switch their active companion plant.

- [x] T022 [US3] Implement `select_plant` logic in `backend/app/services/garden_service.py` to persist active plant.
- [x] T023 [US3] Add `POST /api/garden/plants/{id}/select` route in `backend/app/api/routes/garden.py`.
- [x] T024 [US3] Update carousel controls in `GardenSelectionContent.svelte` to call select API and update main display immediately.
- [ ] T025 [US3] Independent Test: A user can select an owned plant, reload the app, and see the same plant selected everywhere it is displayed.

---

## Phase 7: Water selected plant [US4]

**Goal**: Enable users to spend Water to increase plant vitality.

- [x] T026 [US4] Implement `water_plant` transactional logic in `backend/app/services/garden_service.py`.
- [x] T027 [US4] Add `POST /api/garden/water` route in `backend/app/api/routes/garden.py`.
- [x] T028 [US4] Update watering animation in `frontend/src/lib/features/garden-selection/components/...` to call API and update `last_watered_at` / vitality without reloading.
- [ ] T029 [US4] Independent Test: Watering deducts the correct amount once, updates `last_watered_at`, changes vitality correctly, and persists after reload.

---

## Phase 8: Pomodoro Water rewards [US5]

**Goal**: Issue Water rewards when work is completed.

- [x] T030 [US5] Update `finish_focus_run` in `backend/app/services/focus_service.py` to award `WATER_PER_POMODORO` for valid completions.
- [x] T031 [US5] Enforce idempotency using `FOCUS_COMPLETED` and `source_focus_run_id`.
- [ ] T032 [US5] Independent Test: A valid Pomodoro completion increases Water by exactly `WATER_PER_POMODORO`, but reopening or retrying does not.

---

## Phase 9: Task Leaves rewards [US6]

**Goal**: Issue Leaves rewards when tasks are completed.

- [x] T033 [US6] Update `update_task_status_from_today` in `backend/app/services/today_service.py` to award `LEAVES_PER_TASK` when transitioning to `COMPLETED`.
- [x] T034 [US6] Enforce idempotency using `TASK_COMPLETED` and `source_task_id`.
- [ ] T035 [US6] Independent Test: A Task completion increases Leaves by exactly `LEAVES_PER_TASK`, but reopening and recompleting does not.

---

## Phase 10: Milestone Leaves rewards [US7]

**Goal**: Issue Leaves rewards when major goals are met.

- [x] T036 [US7] Update Milestone completion logic in `backend/app/services/goals_service.py` or equivalent to award `LEAVES_PER_MILESTONE`.
- [x] T037 [US7] Enforce idempotency using `MILESTONE_COMPLETED` and `source_milestone_id`.
- [x] T039 [US1] Update `AppSidebar.svelte` to bind real Water and Leaves balance.
- [x] T040 [US5] Update `frontend/src/lib/features/companion-widget/model/presentation.ts` (or equivalent) to refresh Garden resources upon Pomodoro completion.
- [x] T041 [US6] Update Today screen task completion action to refresh Garden resources in the background without blocking the UI.
- [x] T042 [US7] Update Milestone completion in Goals or Roadmap view to refresh Garden resources.

---

## Phase 12: Error handling and edge cases

**Goal**: Make the implementation robust against failures.

- [ ] T043 Add tests for unlocking a locked plant with insufficient Leaves (402).
- [ ] T044 Add tests for selecting an unowned plant (403).
- [ ] T045 Add tests for concurrent/duplicate Pomodoro and Task completion to verify idempotency.

---

## Phase 13: Final verification

**Goal**: Confirm the feature works correctly end-to-end.

- [x] T046 Run full backend test suite: `pytest backend/tests/`
- [x] T047 Run frontend type check and lint: `npm run check && npm run lint`
- [x] T048 Verify manual demo flow described in `plan.md`. to confirm viability: `npm run build`
- [x] T044 Run SQL verification: `database recreation`
- [x] T045 Check for unrelated or dirty changes: `git diff --check`

---

## Dependencies & Execution Order

### Phase Dependencies

- **Phases 1-3**: Must be completed first in order (Foundation).
- **Phase 4 (US1)**: Must be completed to display real Garden state.
- **Phases 5-10 (US2-US7)**: Can be worked on in parallel once Phase 4 is complete.
- **Phases 11-13**: Dependent on all User Stories finishing.

### Parallel Opportunities

- `T017` can be implemented in parallel with `T018`.
- Pomodoro, Task, and Milestone integrations (Phases 8, 9, 10) can be implemented completely independently of each other.

### Recommended MVP Execution Strategy

1. Complete Foundation (Phases 1-3).
2. Complete US1 (Phase 4) and verify state loads correctly.
3. Complete US5 and US6 (Phases 8-9) to allow manual testing of resource accumulation.
4. Complete US2 (Phase 5) to test spending Leaves.
5. Complete US4 (Phase 7) to test spending Water.
6. Polish with US3, US7, and final checks (Phases 6, 10-13).
