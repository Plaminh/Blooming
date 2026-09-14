# Implementation Tasks: Today Screen

## Phase 1: Setup and Foundation
- [x] T001 [P] Create typed domain models in `frontend/src/lib/features/today/types.ts` defining `Task`, `TaskStatus`, and `FocusPreset`.
- [x] T002 [P] Establish root page `frontend/src/routes/today/+page.svelte` and integrate the existing `DesktopTitleBar.svelte` with responsive overflow scrolling (no clipping).

## Phase 2: Atomic Components Extraction
- [x] T003 [P] [US1] Create `frontend/src/lib/features/today/components/atoms/TaskStatusBadge.svelte` to display visual state for in-progress, completed, and upcoming tasks.
- [x] T004 [P] [US1] Create `frontend/src/lib/features/today/components/atoms/TimelineHourLabel.svelte` for the left axis of the timeline.
- [x] T005 [P] [US4] Create `frontend/src/lib/features/today/components/atoms/FocusPresetOption.svelte` ensuring semantic button behavior and outline states.
- [x] T006 [P] [US2] Create `frontend/src/lib/features/today/components/atoms/DateNavigation.svelte` with typed action callbacks.
- [x] T007 [P] [US3] Create `frontend/src/lib/features/today/components/molecules/NextSessionSummary.svelte`.
- [x] T008 [P] [US1] Create `frontend/src/lib/features/today/components/molecules/SidebarNavigationItem.svelte` with proper semantic states.
- [x] T009 [P] [US1] Create `frontend/src/lib/features/today/components/atoms/ComfortIndicator.svelte` for the timeline header.
- [x] T010 [P] [US1] Create `frontend/src/lib/features/today/components/molecules/TimelineCard.svelte` using semantic `<button>` without selection ring deviations.

## Phase 3: Organism Composition
- [x] T011 [US1] Implement `frontend/src/lib/features/today/components/organisms/TodaySidebar.svelte` reusing `PlantSprite.svelte` for the monstera plant and composing navigation items.
- [x] T012 [US1] Implement `frontend/src/lib/features/today/components/organisms/TodayTimeline.svelte` to render exactly 4 scheduled tasks, utilizing the extracted atoms and handling empty states.
- [x] T013 [US3] Implement `frontend/src/lib/features/today/components/organisms/RightRail.svelte` managing Task Details, Next Session, Focus Setup, and Garden panels.
- [x] T014 [US5] Implement `frontend/src/lib/features/today/components/organisms/BottomActions.svelte` wiring Edit Manually and Replan buttons to typed event dispatchers.

## Phase 4: Integration and Polish
- [x] T015 Run `npm run check` and `npx prettier` to ensure code formatting and type safety.
- [x] T016 Visually compare `http://localhost:5173/today` against `design-assets/references/today.png` at 1440x900 viewport to verify exact geometric constraints and asset alignment.
