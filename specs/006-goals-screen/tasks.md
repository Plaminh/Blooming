# Implementation Tasks: Goals Screen

**Feature**: Goals Screen
**Spec**: [spec.md](spec.md) | **Plan**: [plan.md](plan.md)

## Negative Checks (Rules)
- **NO React/JSX**: Use SvelteKit and existing vanilla/Svelte pipelines.
- **NO speculative APIs**: Do not write backend or CRUD handlers.
- **NO invented asset paths**: Ensure every asset exists before referencing it.
- **NO title-based icon inference**: Icon/status must be explicit in data models.
- **NO CSS classes stored in domain data**.
- **NO duplicated shared shell/theme**: Extract and reuse.
- **NO dead console-only actions**: Provide functioning fallback modal.
- **NO git branch/commit/push operations**: The user manages git state.

## Phase 1: Setup & Foundation

**Goal**: Prepare the route, layout geometry, shared asset inventory, and refactor shared app shell components.
**MVP slice starts here**.

- [X] T001 Confirm the Goals route and runtime styling/font pipeline in `frontend/src/routes/goals/+page.svelte`.
- [X] T002 Inventory and validate every asset path and sprite-frame mapping required by the reference in `frontend/static/assets`.
- [X] T003 Define typed Goals fixture/view-model data with explicit icon/status/variant fields in `frontend/src/lib/features/goals/models.ts`.
- [X] T004 [P] Extract the shared sidebar navigation items into `frontend/src/lib/shared/components/molecules/SidebarNavigationItem.svelte` without regressing Today.
- [X] T005 [P] Extract the shared AppSidebar into `frontend/src/lib/shared/components/organisms/AppSidebar.svelte` and verify on Today screen.
- [X] T006 [P] Extract the Garden panel `.garden` section from `RightRail.svelte` into `frontend/src/lib/shared/components/organisms/GardenPanel.svelte`.
- [X] T007 Match the 1440 × 900 macro geometry layout shell (three columns, sidebar) in `frontend/src/routes/goals/+page.svelte`.

## Phase 2: User Story 1 - View Goals Layout and Shared Shell

**Goal**: Implement the basic shell integration, Tauri controls, and structural skeleton.
**Story Labels**: `[US1]`

- [X] T008 [US1] Implement the shared title bar and Tauri controls integration in `frontend/src/routes/goals/+page.svelte`.
- [X] T009 [US1] Place the `AppSidebar` in the Goals layout with `activeRoute` set to Goals.
- [X] T010 [US1] Place the `GardenPanel` in the right rail section, bottom-aligned with intentional whitespace above it.
- [X] T011 [US1] Validate macro geometry at 1440x900 viewport.

## Phase 3: User Story 2 - View My Goals List

**Goal**: Implement the "My Goals" panel and its list.
**Story Labels**: `[US2]`

- [X] T012 [P] [US2] Implement minimum useful atoms: `GoalStatusBadge.svelte`, `TargetDateLabel.svelte`, `ProgressBar.svelte` in `frontend/src/lib/features/goals/components/atoms/`.
- [X] T013 [P] [US2] Implement `GoalListItem.svelte` molecule in `frontend/src/lib/features/goals/components/molecules/`.
- [X] T014 [US2] Implement `MyGoalsPanel.svelte` organism displaying the local goals fixtures.
- [X] T015 [US2] Add the `MyGoalsPanel` to the left content column in `frontend/src/routes/goals/+page.svelte`.
- [X] T016 [US2] Implement visually distinguishing the selected goal.

## Phase 4: User Story 3 - Select a Goal and View Details

**Goal**: Implement the Goal Details, Roadmap, Next Milestone, and Overall Progress panels, and synchronize them on selection.
**Story Labels**: `[US3]`

- [X] T017 [P] [US3] Implement `RoadmapNode.svelte` atom in `frontend/src/lib/features/goals/components/atoms/`.
- [X] T018 [P] [US3] Implement `SelectedGoalSummary.svelte`, `TargetDateBox.svelte`, `MilestoneDateRow.svelte`, `MilestoneStatusRow.svelte` in `frontend/src/lib/features/goals/components/molecules/`.
- [X] T019 [US3] Implement `RoadmapMilestoneCard.svelte` and `RoadmapTimeline.svelte` organisms.
- [X] T020 [US3] Implement `GoalDetailsPanel.svelte` using the above components in `frontend/src/lib/features/goals/components/organisms/`.
- [X] T021 [US3] Implement `NextMilestoneSummary.svelte` and `OverallProgressSummary.svelte` molecules.
- [X] T022 [US3] Implement `NextMilestonePanel.svelte` and `OverallProgressPanel.svelte` organisms.
- [X] T023 [US3] Add the details and right rail progress panels to `frontend/src/routes/goals/+page.svelte`.
- [X] T024 [US3] Implement goal selection state synchronization across every dependent panel.

## Phase 5: User Story 4 - Interact with Goal Actions

**Goal**: Implement accessible, interactive fallback actions and verify keyboard interactions.
**Story Labels**: `[US4]`

- [X] T025 [P] [US4] Implement a reusable fallback accessible dialog ("Coming Soon") in `frontend/src/lib/shared/components/molecules/FallbackDialog.svelte`.
- [X] T026 [US4] Implement `GoalsRightRail.svelte` and `GoalsActionGroup` using primary/secondary action buttons.
- [X] T027 [US4] Wire Create, Edit, Refine actions to the fallback dialog (since no corresponding flows exist).
- [X] T028 [US4] Ensure existing sidebar navigation works correctly.
- [X] T029 [US4] Verify keyboard navigation, focus states, button semantics, and accessible selected-state communication across the Goals screen.

## Phase 6: Integration & Polish

**Goal**: Apply visual polish, asset checks, tests, and regressions.

- [X] T030 Tune typography, colors, borders, spacing, icons, status treatments, progress bar, and pixel rendering to precisely match the reference.
- [X] T031 Add or update unit/component/integration tests with existing tooling (e.g. Vitest/Playwright).
- [ ] T032 Validate that all assets load and no blank/broken placeholder appears.
- [ ] T033 Perform screenshot comparison against `design-assets/references/goal.png` at 1440 × 900, record mismatches, and iterate to defined tolerance.
- [ ] T034 Re-run Today/shared-shell regression checks to ensure extraction didn't break anything.
- [ ] T035 Run existing formatter, type/check, lint, tests, build, and applicable Tauri validation.
- [ ] T036 Review `git diff` and `git status`, removing temporary debug code, screenshots, scripts, and unused changes.
