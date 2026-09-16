---
description: "Task list for Frontend Architecture Cleanup and UI Consistency"
---

# Tasks: Frontend Architecture Cleanup and UI Consistency

**Input**: Design documents from `/specs/011-frontend-architecture-cleanup/`

**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md, quickstart.md

**Tests**: Vitest tests where behavior can be validated without e2e browser frameworks. Manual verification instructions provided in quickstart.md for layout persistence.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure
*Since this is an existing codebase, setup tasks revolve around verifying baseline health before refactoring.*

- [x] T001 Verify existing app builds and tests pass in `frontend/` — current-branch verification ran successfully in the final correction pass; historical pre-refactor baseline was not captured. Exact commands and exit codes are recorded in `plan.md`.
- [x] T002 [P] Create `(app)` directory structure inside `frontend/src/routes/`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [x] T003 Setup SvelteKit layout route `frontend/src/routes/(app)/+layout.svelte`
- [x] T004 Define and implement the `DesktopAppShell` and `AppSidebar` container in `frontend/src/routes/(app)/+layout.svelte`

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - App Navigation and Shell Persistence (Priority: P1) 🎯 MVP

**Goal**: Navigate between main application pages without the sidebar or overall application shell remounting or flashing.

**Independent Test**: Can be tested by manually loading routes and navigating in the UI, ensuring Sidebar remains mounted (SC-002, SC-007).

### Implementation for User Story 1

- [x] T005 [US1] Move `today` route directory to `frontend/src/routes/(app)/today`
- [x] T006 [US1] Move `goals` route directory to `frontend/src/routes/(app)/goals`
- [x] T007 [US1] Move `mr-bloom` route directory to `frontend/src/routes/(app)/mr-bloom`
- [x] T008 [US1] Move `settings` route directory to `frontend/src/routes/(app)/settings`
- [x] T009 [US1] Move `statistics` route directory to `frontend/src/routes/(app)/statistics`
- [x] T010 [US1] Move `garden-selection` route directory to `frontend/src/routes/(app)/garden-selection`
- [x] T011 [US1] Remove redundant `DesktopAppShell` and `AppSidebar` instantiations from the migrated child pages

**Checkpoint**: At this point, User Story 1 should be fully functional and testable independently

---

## Phase 4: User Story 2 - Garden Panel Stability (Priority: P1)

**Goal**: Ensure Garden panel on Today and Goals screens persists seamlessly between them without visual glitches.

**Independent Test**: Navigate from Today to Goals and visually verify the Garden panel is not remounted and has no exposure/stretching bugs.

### Implementation for User Story 2

- [x] T012 [US2] Lift Garden panel state/visibility to `frontend/src/routes/(app)/+layout.svelte` or create shared right-rail mechanism
- [x] T013 [US2] Update `frontend/src/routes/(app)/today/+page.svelte` to use the shared Garden panel architecture
- [x] T014 [US2] Update `frontend/src/routes/(app)/goals/+page.svelte` to use the shared Garden panel architecture
- [x] T015 [US2] Fix Garden background CSS for exposed strip and invalid crop issues in `frontend/src/lib/shared/components/organisms/GardenPanel.svelte`

**Checkpoint**: At this point, User Stories 1 AND 2 should both work independently

---

## Phase 5: User Story 3 - Visual and Thematic Consistency (Priority: P2)

**Goal**: Consistent colors and accurate icons throughout the application, eliminating hardcoded palette duplicates.

**Independent Test**: Visually verify no empty rounded squares exist, run tests for AppIcon fallbacks, and verify UI components against standard atoms.

### Tests for User Story 3

- [x] T016 [P] [US3] Create regression test for icon rendering in `frontend/src/lib/shared/components/atoms/AppIcon.test.ts` (ensuring no fallback squares)

### Implementation for User Story 3

- [x] T017 [P] [US3] Provide vector geometry for missing `AppIcon` values and remove fallback square in `frontend/src/lib/shared/components/atoms/AppIcon.svelte`
- [x] T018 [P] [US3] Create shared `TextInput` in `frontend/src/lib/shared/components/atoms/TextInput.svelte`
- [x] T019 [P] [US3] Create shared `StatusBadge` in `frontend/src/lib/shared/components/atoms/StatusBadge.svelte`
- [x] T020 [US3] Refactor `mr-bloom`, `settings`, and `statistics` components to consume the shared `TextInput` and `StatusBadge` atoms
- [x] T021 [US3] Create shared `theme.css` tokens for semantic colors in `frontend/src/lib/shared/styles/theme.css` to fix hardcoded values in chat and garden components (goals, today, mr-bloom, statistics, settings, garden-selection)

**Checkpoint**: All user stories should now be independently functional

---

## Phase 6: User Story 4 - Chat Message Legibility (Priority: P3)

**Goal**: Read Mr. Bloom chat messages without excessive blank space.

**Independent Test**: Send short and long messages to Mr. Bloom in Web Preview or Desktop to ensure content-driven height.

### Implementation for User Story 4

- [x] T022 [US4] Update CSS in `frontend/src/lib/features/mr-bloom/components/molecules/ChatMessage.svelte` to use content-driven height and align timestamps correctly

**Checkpoint**: All user stories are functionally complete.

---

## Phase 7: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories (Dead code, responsibility boundaries, validation)

- [x] T023 [P] Remove obsolete/duplicate implementations of `TextInput` and `StatusBadge` (FR-011)
- [x] T024 [P] Remove unused components and stale exports identified during refactor (FR-011)
- [x] T025 Reduce draft preview duplication and improve responsibility boundaries in large affected components (FR-012, FR-013)
- [x] T026 Execute configured checks (`npm run check`, `npm run test`, `npm run build` from `frontend/`, and `git diff --check` from the repository root) (SC-005) — all exited 0; see `plan.md` for results and warnings. No separate formatting/lint script is configured.
- [ ] T027 Perform manual validation per `quickstart.md` procedures to verify layout persistence, standalone isolation, and visual regression (SC-006, SC-007) — **NOT VERIFIED MANUALLY** for the full checklist. Partial Edge browser checks and screenshot inspection are recorded in `plan.md`; Tauri, frame-by-frame flashing and reference screenshot parity remain unverified.

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS US1 and US2, but US3/US4 could technically proceed in parallel as they touch independent components.
- **User Stories (Phase 3+)**: US1 depends on Phase 2. US2 depends on Phase 2. US3 and US4 are largely independent UI adjustments.
- **Polish (Final Phase)**: Depends on all user stories being complete.

### User Story Dependencies

- **User Story 1 (P1)**: Depends on Foundational route layout.
- **User Story 2 (P1)**: Depends on US1 (routes must be moved first) and Foundational Layout.
- **User Story 3 (P2)**: Independent atom updates.
- **User Story 4 (P3)**: Independent CSS update.

### Parallel Opportunities

- **T017, T018, T019, T016 (US3)** can be executed simultaneously in parallel as they edit separate atomic components and tests.
- **User Story 3** and **User Story 4** can be assigned to different developers to execute in parallel with **User Story 1 / 2**, as long as they resolve file paths carefully after routes are moved.

---

## Parallel Example: User Story 3

```bash
# Developer A builds shared atoms:
Task: "Create shared TextInput in frontend/src/lib/shared/components/atoms/TextInput.svelte"
Task: "Create shared StatusBadge in frontend/src/lib/shared/components/atoms/StatusBadge.svelte"

# Developer B fixes icons and adds tests:
Task: "Create regression test for icon rendering in frontend/tests/components/AppIcon.test.ts"
Task: "Provide vector geometry for missing AppIcon values..."
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational (CRITICAL)
3. Complete Phase 3: User Story 1
4. **STOP and VALIDATE**: Verify route persistence and standalone boundaries via manual test.

### Incremental Delivery

1. Complete Setup + Foundational
2. Add US1 (Routing architecture) → Validate
3. Add US2 (Garden Panel UI persistence) → Validate
4. Add US3 (Shared atoms and tokens) → Validate
5. Add US4 (Chat message UI bug) → Validate
6. Polish and remove dead code.
