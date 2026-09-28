# Tasks: Repository-Wide Architectural Refactor

**Input**: Design documents from `/specs/030-repo-wide-refactor/`

**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md, contracts/

**Tests**: Tests are required where mandated by the Constitution or feature specification. Every user story still requires an independently verifiable acceptance method.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3, US4)
- Include exact file paths in descriptions

## Phase 1: Setup & Pre-Refactor Baseline (Phase 0 in Spec)

**Purpose**: Capture the current state and perform baseline checks

- [x] T001 Run and record backend automated test baseline (unit, integration, api) in `specs/030-repo-wide-refactor/pre-refactor-baseline.md`
- [x] T002 Run and record frontend automated test baseline (Vitest, Svelte checks, TS checks) in `specs/030-repo-wide-refactor/pre-refactor-baseline.md`
- [x] T003 Manually document the known-bugs register in `specs/030-repo-wide-refactor/known-bugs.md`
- [x] T004 Define the initial architecture map (before state) in `specs/030-repo-wide-refactor/architecture-before.md`

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

- [x] T005 Verify fresh database initialization using `database/install.sql` and note any current issues
- [x] T006 Audit and clean up stale repository artifacts (build folders, caches, unused packages)
- [x] T007 Set up `specs/030-repo-wide-refactor/refactor-decisions.md` to track any minor structural deviations

---

## Phase 3: User Story 4 - Database Bootstrap and Alignment (Priority: P3)

**Goal**: Ensure database bootstrap and ORM parity are clean. (Doing this early as a foundational DB step)

**Independent Test**: Can run SQL installer against fresh postgres and compare against SQLAlchemy models.

### Implementation for User Story 4

- [x] T008 [US4] Remove artificial filename ordering hacks from `database/install.sql` and `database/init/` scripts where safe
- [x] T009 [US4] Consolidate reference data (e.g., plant presets) away from development seed data in `database/reference_data/`
- [x] T010 [US4] Verify schema parity between SQL and `backend/app/db/models/` and document discrepancies
- [ ] T011 [US4] Remove proven unused database tables (requires explicit documentation in `refactor-decisions.md`)

**Checkpoint**: At this point, the database initializes cleanly and ORM matches.

---

## Phase 4: User Story 2 - Backend Separation of Concerns (Priority: P2)

**Goal**: Clear boundaries for routing, services, and repositories.

**Independent Test**: API tests still pass.

### Implementation for User Story 2

- [x] T012 [P] [US2] Reorganize AI package under `backend/app/ai/` into (llm, nlu, drafting, coach, handlers) preserving prompt logic
- [ ] T013 [US2] Extract Today query and task mutation logic out of API routes and into `backend/app/services/plans/`
- [ ] T014 [US2] Extract re-plan and draft editing logic into cohesive services
- [ ] T015 [US2] Extract database persistence from services into `backend/app/repositories/`
- [ ] T016 [US2] Ensure services explicitly own the transaction boundary (commit/rollback) rather than routes or repositories

**Checkpoint**: Backend architectural layers are correctly separated and existing automated tests pass.

---

## Phase 5: User Story 3 - Frontend Architectural Consolidation (Priority: P2)

**Goal**: Centralize state and components, removing circular dependencies.

**Independent Test**: Frontend tests and static checks pass.

### Implementation for User Story 3

- [ ] T017 [US3] Create a canonical token layer for theme (colors, typography) in `frontend/src/lib/shared/styles/`
- [ ] T018 [US3] Consolidate duplicated UI primitives (Button, Input, etc.) into `frontend/src/lib/shared/ui/`
- [ ] T019 [US3] Extract API client fetch logic and endpoints into `frontend/src/lib/shared/api/` and `frontend/src/lib/shared/api/endpoints/`
- [ ] T020 [US3] Consolidate duplicate type definitions into `frontend/src/lib/shared/types/`
- [ ] T021 [US3] Migrate feature-specific state out of `+page.svelte` files into corresponding `frontend/src/lib/features/*/`
- [ ] T022 [US3] Ensure `frontend/src/lib/shared/` has NO dependencies on `frontend/src/lib/features/`

**Checkpoint**: Frontend architecture is clean and component/type duplication is minimized.

---

## Phase 6: User Story 1 - Maintain Core Baseline (Priority: P1)

**Goal**: Final verification that the refactor hasn't changed observable business behavior.

**Independent Test**: Baseline and Regression Report.

### Implementation for User Story 1

- [ ] T023 [US1] Run final automated regression suite (backend and frontend) and compare to baseline
- [ ] T024 [US1] Run final manual regression scenarios and compare to baseline
- [ ] T025 [US1] Audit codebase for any remaining dead code/unused scripts and remove them
- [ ] T026 [US1] Generate `specs/030-repo-wide-refactor/architecture-after.md` mapping the final state
- [ ] T027 [US1] Generate final `specs/030-repo-wide-refactor/regression-report.md` comparing before and after

**Checkpoint**: Master refactor is verified complete and equivalent.

---

## Phase 7: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories

- [ ] T028 Update test file names (e.g. `test_plan_creation_flow.py`) instead of historical names like `block_7`
- [ ] T029 Clean up contract DTO redundancies between frontend types and Pydantic schemas
- [ ] T030 Ensure `quickstart.md` commands still run smoothly for future development
