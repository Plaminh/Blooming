---
description: "Task list template for feature implementation"
---

# Tasks: 013-manual-planning-today

**Input**: Design documents from `/specs/013-manual-planning-today/`

**Prerequisites**: plan.md (required), spec.md (required for user stories)

**Organization**: Tasks are grouped by user story to enable independent implementation.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Phase 1: Setup and verification

**Purpose**: Verify the active Feature 013 context.

- [x] T001 Verify the active Feature 013 context in `specs/013-manual-planning-today`
- [x] T002 Confirm affected backend paths and current reusable entities in `backend/app/db/models/tasks.py` and `backend/app/db/models/daily_plans.py`

---

## Phase 2: Foundational work

**Purpose**: Shared structures, DB modifications, error codes, blocking prerequisites.

- [x] T003 Define shared typed domain structures (input/output) in `backend/app/schemas/planning.py`
- [x] T004 [P] Add machine-readable planning error codes to error registry in `backend/app/core/errors.py`
- [x] T005 Update SQLAlchemy `Task` model and synchronize the existing SQL migration file in `database/migrations/04_tasks_and_dependencies.sql` with splittability fields

**Checkpoint**: Foundation ready - database supports splittability, schemas are defined.

---

## Phase 3: Manual Task Drafts (US1)

**Goal**: Create and Edit Manual Task Drafts

- [x] T006 [US1] Create Task Draft schemas for create/update/read in `backend/app/schemas/planning.py`
- [x] T007 [US1] Implement Task Draft repository methods in `backend/app/crud/crud_task.py`
- [x] T008 [US1] Implement Task Draft application service in `backend/app/services/planning_service.py`
- [x] T009 [US1] Implement FastAPI routes (create, update, list) in `backend/app/api/routes/planning.py` using existing auth
- [x] T010 [US1] Add stable error responses for cycle detection and ownership in `backend/app/api/routes/planning.py`

**Checkpoint**: Manual Task Draft workflow implemented.

---

## Phase 4: Deterministic Timeline generation (US2)

**Goal**: Generate Deterministic Timeline Draft

- [x] T011 [US2] Implement deterministic scheduling engine in `backend/app/core/scheduler.py`
- [x] T012 [US2] Implement Timeline generation application service in `backend/app/services/planning_service.py`
- [x] T013 [US2] Implement Timeline Draft response schemas in `backend/app/schemas/planning.py`
- [x] T014 [US2] Implement Timeline generation endpoint `POST /api/v1/planning/timeline/generate` in `backend/app/api/routes/planning.py`

---

## Phase 5: Reality Check (US2 Cont.)

**Goal**: Reality Check Evaluator

- [ ] T015 [US2] Implement Reality Check evaluator
- [x] T016 [US2] Integrate Reality Check into Timeline Draft generation in `backend/app/services/planning_service.py`

**Checkpoint**: MVP checkpoint! Manual Task Drafts → deterministic Timeline Draft → Reality Check verified.

---

## Phase 6: Save Timeline Draft as Daily Plan (US3)

**Goal**: Save Timeline Draft as Daily Plan

- [x] T017 [US3] Implement Daily Plan and plan-block atomic persistence in `backend/app/services/planning_service.py`
- [ ] T018 [US3] Add database constraints/indexes required for idempotency
- [x] T019 [US3] Implement save endpoint `POST /api/v1/planning/daily-plans` in `backend/app/api/routes/planning.py`

---

## Phase 7: Today retrieval (US4)

**Goal**: Load Today Screen

- [x] T020 [US4] Implement Today query/repository method in `backend/app/crud/crud_daily_plan.py`
- [x] T021 [US4] Implement Today response schemas in `backend/app/schemas/today.py`
- [x] T022 [US4] Implement Today application service in `backend/app/services/today_service.py`
- [x] T023 [US4] Implement `GET /api/v1/today` route in `backend/app/api/routes/today.py`

---

## Phase 8: Today task edit and status update (US5)

**Goal**: Edit Task and Update Status from Today

- [x] T024 [US5] Implement Edit application service and Status transition service in `backend/app/services/today_service.py`
- [ ] T025 [US5] Implement Repository update methods maintaining Task and PlanBlock consistency
- [x] T026 [US5] Implement Edit endpoint and Status endpoint in `backend/app/api/routes/today.py` with stable errors

**Checkpoint**: Save Daily Plan → Today retrieval → task edit/status update completed.

---

## Final phase: Cleanup and readiness review

**Purpose**: Final polish.

- [x] T027 Remove temporary or duplicate code introduced by this feature.
- [x] T028 Check that no unrelated files were modified.
- [x] T029 Verify all task checkboxes correspond to concrete work.
- [x] T030 Verify all error cases use stable machine-readable codes.
- [x] T031 Verify the feature works without AI configuration.
- [x] T032 Produce a final implementation-readiness summary.

---

## Post-demo refinement

- [ ] Full stale-draft detection.
- [ ] Complete status-transition matrix.
- [ ] Complex dependency propagation.
- [ ] Split-segment edge cases.
- [ ] Multiple plan versions/re-planning.
- [ ] Performance and production testing.

---

## Dependency requirements

### Phase Dependencies
- **Phase 1-2**: Blocking prerequisites for all stories.
- **Phase 3**: Depends on Phase 2.
- **Phase 4-5**: Depends on Phase 3 (needs Task Drafts to generate timeline).
- **Phase 6**: Depends on Phase 4-5 (needs Timeline Drafts to save).
- **Phase 7**: Depends on Phase 6 (needs Saved Plans to render).
- **Phase 8**: Depends on Phase 7.
- **Phase 9-Final**: Depends on all stories completed.

### User Story Dependencies
- **US1 (Task Drafts)**: No dependencies.
- **US2 (Timeline + Reality Check)**: Depends on US1.
- **US3 (Save Plan)**: Depends on US2.
- **US4 (Today Screen)**: Depends on US3.
- **US5 (Today Edits)**: Depends on US4.
