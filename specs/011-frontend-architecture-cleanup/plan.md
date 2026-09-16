# Implementation Plan: Frontend Architecture Cleanup

**Branch**: `011-frontend-architecture-cleanup` | **Date**: 2026-09-16 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `/specs/011-frontend-architecture-cleanup/spec.md`

**Note**: Executed via `/speckit-implement`. See `.specify/templates/plan-template.md` for the workflow.

## Summary

Refactor the SvelteKit routing architecture to introduce a persistent layout group `(app)` for primary screens, ensuring the application shell, sidebar, and shared Garden panel do not unnecessarily remount during navigation. Standardize shared components (`AppIcon`, `TextInput`, `StatusBadge`) and theme tokens to eliminate UI duplication and visual defects (missing icons, chat spacing, image cropping) while strictly preserving the approved design and avoiding backend modifications.

## Technical Context

**Language/Version**: TypeScript, Node.js (frontend)

**Primary Dependencies**: SvelteKit, Tauri 2, Vite, Svelte

**Storage**: Local state (Svelte stores), potentially Tauri local storage (if existing). No new storage introduced.

**Testing**: Vitest, Testing Library Svelte

**Target Platform**: Desktop App (Tauri - Windows/Linux MVP) and Web Preview

**Project Type**: Desktop App Frontend (SvelteKit)

**Performance Goals**: Instantaneous route transitions without layout repaints/remounts.

**Constraints**: Frontend-only change; must preserve Tauri window behavior; no backend/API changes; no new E2E frameworks.

**Scale/Scope**: Refactoring ~10 feature screens and ~10 shared atoms/molecules.

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
specs/011-frontend-architecture-cleanup/
├── plan.md              # This file
├── research.md          # Phase 0 output
├── data-model.md        # Phase 1 output
├── quickstart.md        # Phase 1 output
└── tasks.md             # Phase 2 output
```

### Source Code (repository root)

```text
frontend/
├── src/
│   ├── lib/
│   │   └── shared/
│   │       ├── components/
│   │       │   ├── atoms/
│   │       │   │   ├── AppIcon.svelte          ← standardized, all icons have geometry
│   │       │   │   ├── AppIcon.test.ts         ← new: validates no fallback square
│   │       │   │   ├── TextInput.svelte        ← new shared atom
│   │       │   │   ├── TextInput.test.ts       ← new
│   │       │   │   ├── StatusBadge.svelte      ← shared: tag/pill for MrBloom+Stats only
│   │       │   │   └── StatusBadge.test.ts     ← new
│   │       │   └── organisms/
│   │       │       ├── GardenPanel.svelte      ← shared Garden; browser checks below
│   │       │       └── GardenPanel.test.ts     ← new: smoke test
│   │       └── styles/
│   │           └── theme.css                  ← standardized tokens, no new fallback hex
│   └── routes/
│       └── (app)/
│           ├── +layout.svelte                 ← new: persistent shell + Garden panel
│           ├── today/
│           ├── goals/
│           ├── mr-bloom/
│           ├── settings/
│           └── statistics/
└── src/lib/features/
    ├── goals/components/
    │   ├── atoms/
    │   │   └── GoalStatusBadge.svelte          ← restored: MilestoneStatus specialized badge
    │   └── organisms/
    │       ├── RoadmapMilestoneCard.svelte      ← fixed: uses GoalStatusBadge
    │       └── GoalsRightRail.test.ts          ← null/goal sections, callbacks, no local Garden
    ├── today/components/
    │   ├── atoms/
    │   │   └── TaskStatusBadge.svelte          ← restored: TaskStatus specialized badge
    │   └── molecules/
    │       └── TimelineCard.svelte             ← fixed: uses TaskStatusBadge
    └── mr-bloom/components/
        └── molecules/
            ├── DraftAddButton.svelte           ← fixed: milestone variant dimensions restored
            └── ChatMessage.test.ts             ← new
```

**Structure Decision**: A standard SvelteKit layout with a new route group `(app)` to isolate the persistent application shell from standalone routes. The shared UI components are consolidated within the existing atomic design directory `src/lib/shared/components/`.

## Route Migration Map

| Old Route | New Route | Notes |
|-----------|-----------|-------|
| `routes/today/` | `routes/(app)/today/` | Moved into (app) layout group |
| `routes/goals/` | `routes/(app)/goals/` | Moved into (app) layout group |
| `routes/mr-bloom/` | `routes/(app)/mr-bloom/` | Moved into (app) layout group |
| `routes/settings/` | `routes/(app)/settings/` | Moved into (app) layout group |
| `routes/statistics/` | `routes/(app)/statistics/` | Moved into (app) layout group |
| `routes/garden-selection/` | `routes/(app)/garden-selection/` | Moved into (app) layout group |
| `routes/auth/` | `routes/auth/` | Unchanged — outside (app), own shell without sidebar |
| `routes/onboarding-preview/` | `routes/onboarding-preview/` | Unchanged — standalone |
| `routes/widget/` | `routes/widget/` | Unchanged — companion widget |

## Component Scoping: What the Shared StatusBadge Serves

| Context | Component | Status values |
|---------|-----------|---------------|
| Mr. Bloom draft/review | Shared `StatusBadge`, tag variant | `Core`, `Optional` |
| Statistics plan history | Shared `StatusBadge`, pill variant | `Completed`, `Unfinished` |
| Goals roadmap | `GoalStatusBadge` | `Completed`, `In progress`, `Not started` |
| Today timeline | `TaskStatusBadge` | `in-progress`, `completed`, `upcoming` |

## Final Correction Verification (T001/T026/T027)

These are current-branch results from the final correction pass. A historical pre-refactor baseline was not captured. No separate formatting or lint script is configured in `frontend/package.json`.

The commands below were rerun successfully after the `/garden-selection` visibility correction. Garden visibility now derives directly from the pathname (`/today` or `/goals`), independently of the sidebar's fallback active route.

| Working directory | Exact command | Exit code | Result | Warnings / limits |
|-------------------|---------------|-----------|--------|-------------------|
| `frontend/` | `npm run check` | 0 | PASS | 0 errors, 0 warnings |
| `frontend/` | `npm run test` | 0 | PASS | 21 files, 150 tests passed. Eight JSDOM `HTMLCanvasElement.getContext()` not-implemented warnings: canvas rendering is not verified by this suite. Vitest also emitted environment performance advice. |
| `frontend/` | `npm run build` | 0 | PASS | Static site generated. Vite emitted a `PLUGIN_TIMINGS` performance warning; no build correctness error. |
| Repository root | `git diff --check` | 0 | PASS | Git emitted LF-to-CRLF conversion notices; no whitespace errors. |

### Restored values

- `GoalStatusBadge`: inline-flex, centered alignment, minimum height 30px, padding 3px 10px, radius 4px, body font 14px/500. Background/text pairs: Completed `#4e9d67`/`#ffffff`; In progress `#e4f4ed`/`#438f61`; Not started `#e5edf5`/`#557fa6`.
- `TaskStatusBadge`: grid with centered content, minimum width 112px, height 34px, radius 5px, body font 14px/500, nowrap. Labels: In progress, Completed, Upcoming. Background/text pairs: `#c8ead8`/`#087846`, `#d9eed8`/`#167d4a`, `#ece9e2`/`#0750ad` respectively.
- `DraftAddButton` task: 184×48px, flex 0 0 48px, gap 12px, padding 0 18px, font 18px, plus `--bloom-icon-control` (18px).
- `DraftAddButton` milestone: 226×46px, flex 0 0 46px, gap 12px, top margin 1px, padding 0 22px, font 18px, plus 31px.
- Both draft variants: border 2px solid `#9e9a8f`, radius 5px, background `#fffaf0`, text `#064b91`, weight 800, tracking -0.055em, hover `#eef8f6`, focus outline 2px solid `#00aeea` with 2px offset. Exact palette literals live in `theme.css`; components use semantic tokens without fallbacks. These values were checked in Edge, including forced hover/focus-visible states. This is value preservation, not a claim of screenshot parity.
- Loading-bubble changes remove token fallbacks only: the existing 1px border, 8px radius, square top-left corner, 48px height, 12px 16px padding, and arrow coordinates remain unchanged.
- Goals Garden: 278px grid row, explicit 270px Garden height, 8px bottom margin. Browser measurements confirmed 270px content allocation and 8px spacing inside the grid, separate from its 10px outer padding.

### Browser evidence and manual limits

After the visibility correction, Edge checked the production preview at `http://127.0.0.1:4173/garden-selection` (1440×1000). The route had zero sidebar, Garden-layer and shared Garden elements. Hit tests confirmed the plant content and controls were unobstructed. An actual pointer click on Unlock changed the button to Selected and the fixture balance from 124 to 4. Previous/Next remained intentionally disabled because the fixture contains one plant. This targeted check does not change T027's incomplete status.

An existing Edge installation loaded `npm run dev` at `http://127.0.0.1:1420`, with a 1440×1000 viewport. Checks used inline DevTools commands; no dependencies, audit scripts, or repository assets were added.

- Today → Goals → Today kept the same sidebar and Garden DOM nodes; a MutationObserver recorded no removals. This verifies DOM persistence for that sequence, not absence of flashing between every frame.
- Today Garden measured x=959, y=661, 390×227px. Goals Garden measured x=1020, y=610, 328×270px, with 8px bottom spacing. Today and Goals screenshots were visually inspected: no exposed bright strip or obvious image stretching was observed at this viewport. Exact crop/reference parity is still unverified.
- All Goal and Task badge labels, colors, font sizes and dimensions matched the requested values in browser computed styles. The Add Task and Add Milestone computed styles matched the values above.
- Goals Edit opened the dialog, Close dismissed it, Refine reopened it, and navigation to Today removed it. This exercises the Goals page lifecycle; `GoalsRightRail.test.ts` only covers its own sections and callbacks.
- Browser fixtures covered short, newline-containing and long messages for both roles. Long text wrapped; user timestamps remained children of the bubble with static positioning. Newlines are retained in the DOM but collapse to spaces visually under the accepted CSS. Short assistant bubbles also stretch to the avatar column height. Neither existing behavior was changed in this pass.
- `/auth`, `/onboarding-preview`, `/widget` and `/widget-preview` rendered without the persistent `(app)` layer, sidebar or Garden. Authentication and onboarding retain their own existing desktop shells without sidebars; the widget routes have no desktop shell.

T027 remains unchecked: **NOT VERIFIED MANUALLY** for the full checklist. Limited screenshot inspection and the browser checks above were performed, but Tauri validation, frame-by-frame flash checks and approved-reference screenshot parity were not. GardenPanel unit tests cover rendering, heading, link and footer only; they do not establish persistence, crop or dimensions. ChatMessage unit tests cover DOM structure and actual CSS rules, not pixel measurements.

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| — | — | — |
