# Implementation Plan: Goals Screen

**Branch**: `[]` | **Date**: 2026-09-14 | **Spec**: [specs/006-goals-screen/spec.md](specs/006-goals-screen/spec.md)

**Input**: Feature specification from `specs/006-goals-screen/spec.md`

## Summary

Implement the Goals screen matching `removed reference artwork`, using shared components from the Today screen where applicable, creating specific Atomic Design components for the Goals view, and ensuring responsive state synchronization with local view-model fixtures without using React/JSX or assuming backend presence.

## Technical Context

**Language/Version**: TypeScript 5, Svelte 5

**Primary Dependencies**: SvelteKit, Tauri 2

**Storage**: Local view-model fixtures (no backend persistence)

**Testing**: Existing Svelte component test infrastructure

**Target Platform**: Desktop (Tauri)

**Project Type**: Desktop app frontend

**Performance Goals**: Instant selection synchronization without visual lag

**Constraints**: Must perfectly match 1440x900 macro geometry, exact pixel-art assets, no backend APIs, typed state

**Scale/Scope**: Frontend only; 1 page route, ~10 local components

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- [x] Does the plan align with the Spec-driven development workflow?
- [x] Does the plan preserve the approved Tauri 2/Rust, SvelteKit/TypeScript/Vite, FastAPI/Python/Pydantic, and PostgreSQL/SQLAlchemy boundaries?
- [x] Does deterministic application code remain authoritative while AI output and external input are validated at trust boundaries?
- [x] Are explicit contracts and type safety boundaries defined?
- [x] Is the proposed implementation the simplest that satisfies the spec?
- [x] Are testable behavior and quality gates defined?
- [x] Does the UX handle loading, partial, and failure states gracefully?
- [x] Are resource efficiency and platform scope strictly followed?
- [x] Are security and privacy principles respected?

## Project Structure

### Documentation (this feature)

```text
specs/006-goals-screen/
├── plan.md              # This file
├── research.md          # Phase 0 output
├── data-model.md        # Phase 1 output
├── quickstart.md        # Phase 1 output
└── tasks.md             # Phase 2 output
```

### Source Code (repository root)

```text
frontend/src/
├── routes/
│   └── goals/
│       └── +page.svelte
├── lib/
│   ├── shared/
│   │   └── components/
│   │       ├── organisms/
│   │       │   ├── AppSidebar.svelte (extracted from TodaySidebar)
│   │       │   ├── AppTitleBar.svelte (extracted from DesktopTitleBar/WidgetTitleBar if applicable, or just use existing)
│   │       │   └── GardenPanel.svelte (extracted from RightRail.svelte)
│   │       └── atoms/
│   │           └── (shared badges, icons, buttons)
│   └── features/
│       └── goals/
│           ├── components/
│           │   ├── atoms/
│           │   │   ├── RoadmapNode.svelte
│           │   │   ├── ProgressBar.svelte
│           │   │   ├── GoalStatusBadge.svelte
│           │   │   └── TargetDateLabel.svelte
│           │   ├── molecules/
│           │   │   ├── GoalListItem.svelte
│           │   │   ├── SelectedGoalSummary.svelte
│           │   │   ├── TargetDateBox.svelte
│           │   │   ├── MilestoneDateRow.svelte
│           │   │   ├── NextMilestoneSummary.svelte
│           │   │   └── OverallProgressSummary.svelte
│           │   └── organisms/
│           │       ├── MyGoalsPanel.svelte
│           │       ├── GoalDetailsPanel.svelte
│           │       ├── RoadmapTimeline.svelte
│           │       ├── RoadmapMilestoneCard.svelte
│           │       ├── NextMilestonePanel.svelte
│           │       ├── OverallProgressPanel.svelte
│           │       └── GoalsRightRail.svelte
│           └── models.ts
```

## Reuse Matrix

| Component | Existing Path / Source | Destination / Action |
| --- | --- | --- |
| Sidebar | `features/today/.../TodaySidebar.svelte` | Extract to `shared/components/organisms/AppSidebar.svelte`, add `activeRoute` prop |
| Sidebar Items | `features/today/.../SidebarNavigationItem.svelte` | Extract to `shared/components/molecules/SidebarNavigationItem.svelte` |
| Garden Panel | `features/today/.../RightRail.svelte` | Extract `.garden` section to `shared/components/organisms/GardenPanel.svelte` |
| Icon | `features/today/.../TodayIcon.svelte` | Extract/Rename to `shared/components/atoms/AppIcon.svelte` or use as is if semantic |
| Title Bar | `features/onboarding-setup/.../DesktopTitleBar.svelte` | Reuse existing component or extract to shared if needed |

## Asset Inventory

- `leaf-icon.png` (Goal details target date box / Garden header / Next milestone) - likely exists in `static/assets/icons/leaf-icon.png`
- `book` icon for "Read 12 books"
- `shoe` / `sneaker` icon for "Stay healthy"
- `calendar` icon for Next milestone
- Checkmark / In progress / Not started badges
- Garden scene: `default-sky.png`, `background-bushes.png` (already in use in `RightRail.svelte`)

## Interaction Plan
- Create, Edit Manually, Refine with Mr. Bloom: Will use an accessible placeholder modal dialog that says "Coming Soon" with a close button.
- Sidebar Routing: Navigates to `/goals`, `/today`, etc.
- Goal Selection: Local Svelte `$state` / `let` store that holds the `selectedGoalId` and filters the view model.

## Complexity Tracking

No violations.
