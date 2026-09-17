---
description: "Task list for API Integration feature"
---

# Tasks: API Integration

**Input**: Design documents from `/specs/018-api-integration/`

**Prerequisites**: plan.md, spec.md, data-model.md, quickstart.md

**Organization**: Tasks are grouped by the requested phases and mapped to user stories.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel
- **[Story]**: Which user story this task belongs to (e.g., [US1], [US2])

---

## Phase 1: Setup and contract verification

**Purpose**: Initial project verification and mismatch recording

- [x] T001 Verify backend `alembic` commands and frontend `npm run dev` in `backend/` and `frontend/`
- [x] T002 Identify and update `PUBLIC_API_BASE_URL` in `frontend/.env` to point to `http://127.0.0.1:8000/api/v1`
- [x] T003 Inventory all mock locations identified in `specs/018-api-integration/data-model.md`

---

## Phase 2: Shared integration foundation

**Purpose**: Establish a robust, shared authenticated API client

- [x] T004 Update `frontend/src/lib/api.ts` to automatically strip redundant `/api/v1`, `/v1`, or `/api` prefixes from endpoints
- [x] T005 Update `frontend/src/lib/api.ts` to normalize typed API errors using `APIError` and Pydantic validation details
- [x] T006 Ensure `frontend/src/lib/api.ts` correctly handles 401 Unauthorized by clearing `authStore`
- [x] T007 [P] Create `frontend/src/lib/api.test.ts` to test client prefix stripping and error handling

---

## Phase 3: Authentication and session [US1]

**Purpose**: Integrate sign-in and registration

- [x] T008 [US1] Remove mock loading and replace `fetch('/api/v1/me')` in `frontend/src/lib/shared/stores/authStore.ts` with `api.get('/me')`
- [x] T009 [US1] Implement `register` using `api.post('/auth/register')` in `authStore.ts`
- [x] T010 [US1] Implement `login` using `api.post('/auth/login')` in `authStore.ts`
- [x] T011 [US1] Update `frontend/src/routes/auth/+page.svelte` to consume `authStore.login`/`register` and handle duplicate submission prevention
- [x] T012 [P] [US1] Update `frontend/src/lib/features/authentication/AuthenticationView.test.ts` for real API mocking

---

## Phase 4: Onboarding [US1]

**Purpose**: Replace onboarding preview with actual state saving

- [x] T013 [US1] Update `frontend/src/routes/(app)/onboarding-preview/+page.svelte` to submit data to `api.put('/me/settings')`
- [x] T014 [US1] Map frontend onboarding payload (`mrBloomName`, `focusPreset`, etc.) to backend schema (`mr_bloom_display_name`, `default_focus_minutes`, etc.) before submission
- [x] T015 [US1] Implement pending state and disable submission buttons during API call
- [x] T016 [P] [US1] Update `frontend/src/lib/features/onboarding-setup/OnboardingSetupView.test.ts`

---

## Phase 5: Today [US2]

**Purpose**: Replace hardcoded reference tasks with backend data

- [x] T017 [US2] Remove `referenceTasks` fallback from `frontend/src/routes/(app)/today/+page.svelte`
- [x] T018 [US2] Ensure `updateSchedule` in `today/+page.svelte` calls `api.get('/today?date=...')` without prefix duplication
- [x] T019 [US2] Implement task status mutation calling `api.patch('/today/tasks/{id}/status')` when users complete a task
- [x] T020 [P] [US2] Update `frontend/src/lib/features/today/TodayView.test.ts` to mock `api.get('/today')`

---

## Phase 6: Pomodoro [US3]

**Purpose**: Persist focus sessions natively

- [x] T021 [US3] Update `handleStartFocus` in `frontend/src/routes/(app)/today/+page.svelte` to securely call `api.post('/focus/start')`
- [x] T022 [US3] Implement stop/cancel logic targeting `api.post('/focus/finish')` without disrupting local timer tick
- [x] T023 [US3] Reconcile local state seamlessly on failure of `/focus/finish`

---

## Phase 7: Goals and milestones [US4]

**Purpose**: Tie goals explicitly to API endpoints

- [x] T024 [US4] Remove duplicate slashes from `api.get('/goals/')` calls in `frontend/src/lib/features/goals/stores/goalsStore.ts`
- [x] T025 [US4] Update `executeReminderAction` in `goalsStore.ts` to handle errors gracefully without assuming successful cache invalidation

---

## Phase 8: Garden [US5]

**Purpose**: Tie unlocks and currency to actual backend logic

- [x] T026 [US5] Update `frontend/src/lib/features/garden-selection/model/state.svelte.ts` to use `api.get('/garden')` instead of `/api/garden`
- [x] T027 [US5] Update `unlockSelectedPlant` and `waterSelectedPlant` in `state.svelte.ts` to trap 409 Conflicts or insufficient currency exceptions
- [x] T028 [US5] Remove `INITIAL_GARDEN_STATE` mock fallbacks from `frontend/src/lib/features/garden-selection/model/fixtures.ts`
- [x] T029 [P] [US5] Update `frontend/src/lib/features/garden-selection/model/state.test.ts`

---

## Phase 9: Settings [US7]

**Purpose**: Connect the user profile and preferences accurately

- [x] T030 [US7] Update `frontend/src/lib/features/settings/model/SettingsState.svelte.ts` to map `mrBloomName` to `mr_bloom_display_name` and drop unsupported fields
- [x] T031 [US7] Remove artificial `setTimeout` simulation in `SettingsState.svelte.ts`'s `save()` method
- [x] T032 [US7] Propagate saved settings updates to `authStore.ts` if user identity is affected

---

## Phase 10: Statistics [US6]

**Purpose**: Show real historical data

- [x] T033 [US6] Update `frontend/src/lib/features/statistics/api/statistics.api.ts` to strip `/v1/` from `api.get('/v1/statistics/...')`
- [x] T034 [US6] Ensure empty arrays returned from `getPlanHistory` render as empty states rather than throwing rendering errors
- [x] T035 [P] [US6] Update `frontend/src/lib/features/statistics/StatisticsView.test.ts` to remove static mock references

---

## Phase 11: Cross-feature consistency and mock cleanup

**Purpose**: Ensure the application performs cleanly without leftover technical debt

- [x] T036 Ensure `logout()` in `SettingsState.svelte.ts` and `authStore.ts` forcefully clears all active feature stores (goals, garden, today)
- [x] T037 Delete `frontend/src/lib/features/garden-selection/model/fixtures.ts` entirely if no longer used by tests
- [x] T038 Confirm the Companion Widget in `frontend/src/routes/(app)/widget/+page.svelte` is not broken by `api.ts` prefix changes

---

## Phase 12: Final validation

**Purpose**: QA and build readiness

- [x] T039 Run frontend formatter: `cd frontend && npm run format` (Omitted, no script)
- [x] T040 Run frontend linter: `cd frontend && npm run lint` (Omitted, no script)
- [x] T041 Run frontend type checking: `cd frontend && npm run check`
- [x] T042 Run frontend unit tests: `cd frontend && npm run test`
- [x] T043 Run production frontend build: `cd frontend && npm run build`
- [ ] T044 Execute Authentication and Session smoke test (Quickstart Scenario 1)
- [ ] T045 Execute Onboarding to Today flow (Quickstart Scenario 2)
- [ ] T046 Execute Pomodoro Focus consistency check (Quickstart Scenario 3)
- [ ] T047 Execute Garden transactions check (Quickstart Scenario 5)
