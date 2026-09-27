---
description: "Task list for compact desktop companion widget implementation"
---

# Tasks: Compact Desktop Companion Widget

**Input**: Design documents from `/specs/001-companion-widget/`

**Prerequisites**: [plan.md](./plan.md), [spec.md](./spec.md), [research.md](./research.md), [data-model.md](./data-model.md), [contracts/ui-presentation.md](./contracts/ui-presentation.md), [quickstart.md](./quickstart.md)

**Tests**: Required by the constitution and spec (SC-006, SC-008, SC-009, SC-011). The installed stack is `vitest@^5`, `jsdom`, `@testing-library/svelte@^5`, `@testing-library/user-event@^14`, `@testing-library/jest-dom@^6`, and `axe-core@^4`. Automated gates are `npm run check`, `npm run test`, and `npm run build`. jsdom/axe do not prove real rendered color contrast. **Do not** add Playwright, Storybook, a UI kit, an icon pack, a CSS framework, or an app-wide store.

**Organization**: Setup → Foundational (assets, tokens, atlas, character, icons, atoms, molecules, shell) → user stories (Paused, Behind Schedule, Offline, Reminders) → preview → Tauri → tests → polish. Offline (US4) is sequenced before Reminders (US3) so all four fixtures exist before the preview route.

**Constraints**: Product and asset constraints are the requirements in [spec.md](./spec.md) (FR-007 no backend, VR-008 runtime assets, VR-014 bounded presentation animation, VR-015 source-only reference). Structural constraints from [plan.md](./plan.md): do not introduce `frontend/src/lib/components/widget/`, do not put `src-tauri` under `frontend/src/`, and do not modify authoritative source PNGs. Deterministically generated runtime atlases may be replaced.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no incomplete dependencies)
- **[Story]**: User story label (`[US1]` … `[US4]`) on story-phase tasks only
- Every implementation task includes exact file paths

## Path Conventions

- Feature UI: `frontend/src/lib/features/companion-widget/`
- Routes: `frontend/src/routes/widget/`, `frontend/src/routes/widget-preview/`
- Tauri: `frontend/src-tauri/`
- Runtime PNGs: `frontend/static/assets/widget/`
- Source-only visual reference: `removed reference artwork`

## Completion criteria

Feature status: **Implemented — manual acceptance pending**. Success Criteria are SC-001 … SC-014 in [spec.md](./spec.md). Automated criteria are covered by T035–T038 and T043; manual criteria by T039–T042 with results recorded in [checklists/visual-acceptance.md](./checklists/visual-acceptance.md).

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Confirm assets and the `companion-widget` feature module inside the SvelteKit + Tauri app.

- [x] T001 Validate runtime assets exist at `frontend/static/assets/widget/environment/daytime/morning.png` (1880×837, RGB), `frontend/static/assets/widget/environment/season/spring.png` (1881×836, RGBA), normalized `frontend/static/assets/mr-bloom/mr-bloom-spritesheet.png` (1152×1152, RGBA), `frontend/static/assets/icons/leaf-icon.png`, and the five normalized plant atlases; confirm source-only artwork is not under `frontend/static/`; classify roles in `removed reference artwork`
- [x] T002 Create `frontend/src/lib/features/companion-widget/` (`components/atoms/`, `components/molecules/`, `components/organisms/`, `fixtures/`, `types/`, `styles/`, `model/`, `index.ts`) and point `frontend/src/routes/widget/+page.svelte` at the feature export; do not introduce `src/lib/components/widget/`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Tokens, typed model, atlas mapping, character, icons, atoms, molecules, and shared shell. **No user-story fixture work until this phase is complete.**

**⚠️ CRITICAL**: User story implementation cannot begin until this phase is complete

- [x] T003 Split styling per [plan.md](./plan.md) → *Design tokens & chrome*: shared visual tokens (canvas size, 3px outer strips, radius 4, stroke 4, title-bar band, palette, font, `image-rendering: pixelated`) in `frontend/src/lib/features/companion-widget/styles/widget-theme.css`, and per-state geometry in `frontend/src/lib/features/companion-widget/model/layout.ts` emitted as CSS custom properties; read values from the reference metrics without importing the SVG or pasting path `d` data
- [x] T004 [P] Add the discriminated union (`kind`: `paused` | `behindSchedule` | `offline` | `reminders`), optional `timeText`, optional state-relevant callbacks, and `ReminderItem` in `frontend/src/lib/features/companion-widget/types/presentation.ts` per `specs/001-companion-widget/data-model.md`
- [x] T005 [P] Normalize the irregular source character sheet into a `1152×1152`, 4×8 runtime atlas with `288×144` cells, removing centered adjacent-row bleed while retaining detached effects; add state rows plus permitted columns (`paused [0,1,2,3]`, `behindSchedule [0,2]`, `offline [0,1,2,3]`, `reminders [1]`) and the shared scene box in `model/atlas.ts`
- [x] T006 [P] Implement layered sky/bushes in `frontend/src/lib/features/companion-widget/components/molecules/WidgetSceneBackground.svelte` (shared 1880×837 wrapper, bottom-left alignment, uniform scale, `aria-hidden`, pixelated rendering; do not `object-fit` the two images independently)
- [x] T007 [P] Implement reusable atlas-backed Mr. Bloom in `frontend/src/lib/features/companion-widget/components/atoms/MrBloomCharacter.svelte` (one normalized cell viewport at `220×110`, `overflow: hidden`, sequence reset/reduced motion, preserve alpha, no per-state duplicate component)
- [x] T008 [P] Render the supplied `/assets/icons/leaf-icon.png` in `WidgetTitleBar.svelte` (`40×40` image in a `28×31` logo slot); do not add a leaf-balance badge or custom leaf SVG
- [x] T009 Paused uses the cyan sleep effects baked into its four supplied frames; do not add a separate sleep overlay component
- [x] T010 [P] Implement orange schedule alerts in `frontend/src/lib/features/companion-widget/components/atoms/ScheduleAlerts.svelte`
- [x] T011 [P] Implement pink reminder alerts in `frontend/src/lib/features/companion-widget/components/atoms/ReminderAlerts.svelte`
- [x] T012 [P] Implement Wi-Fi + red `×` in `frontend/src/lib/features/companion-widget/components/atoms/OfflineStatus.svelte`
- [x] T013 [P] Implement bell icon in `frontend/src/lib/features/companion-widget/components/atoms/BellIcon.svelte`
- [x] T014 [P] Implement play icon in `frontend/src/lib/features/companion-widget/components/atoms/PlayIcon.svelte`
- [x] T015 [P] Implement stop icon in `frontend/src/lib/features/companion-widget/components/atoms/StopIcon.svelte`
- [x] T016 Implement pixel widget button (primary green / secondary cream, semantic `<button>`, visible focus) in `frontend/src/lib/features/companion-widget/components/atoms/WidgetButton.svelte` using `PlayIcon.svelte` / `StopIcon.svelte` when needed
- [x] T017 [P] Implement window-control button with custom min / max-restore / close SVG and accessible names in `frontend/src/lib/features/companion-widget/components/atoms/WindowControlButton.svelte`
- [x] T018 [P] Implement pixel status wrapper in `frontend/src/lib/features/companion-widget/components/atoms/PixelStatus.svelte`
- [x] T019 Implement title bar (logo, `BLOOMING`, three controls, `data-tauri-drag-region` excluding buttons; no Tauri API in `load`) in `frontend/src/lib/features/companion-widget/components/molecules/WidgetTitleBar.svelte`
- [x] T020 [P] Implement cream speech bubble with tail toward the character in `frontend/src/lib/features/companion-widget/components/molecules/SpeechBubble.svelte`
- [x] T021 [P] Implement reminder panel (bell, heading singular/plural, two-line max, ellipsis with full `label` as accessible name, `+N more` without growing height) in `frontend/src/lib/features/companion-widget/components/molecules/ReminderPanel.svelte`
- [x] T022 [P] Implement lower-right action group (state-driven order, primary then secondary) in `frontend/src/lib/features/companion-widget/components/molecules/ActionGroup.svelte`
- [x] T023 Implement shared `CompanionWidget` organism in `frontend/src/lib/features/companion-widget/components/organisms/CompanionWidget.svelte` importing `widget-theme.css`: outer border, title bar, scene, one character, non-paused semantic overlays (`ScheduleAlerts` / `ReminderAlerts` / `OfflineStatus` via `PixelStatus`), speech, optional timer, reminder panel, actions; invoke optional callbacks only when present; omit timer when `timeText` is absent; no fixture strings hard-coded in the organism
- [x] T024 Export the public feature surface from `frontend/src/lib/features/companion-widget/index.ts` (`CompanionWidget` and presentation types only; fixtures must remain importable by routes but must not be required by the organism)

**Checkpoint**: Shell can render a typed `CompanionWidgetPresentation` in the browser with aligned backgrounds and a single atlas cell. Fixture modules are still empty.

---

## Phase 3: User Story 1 - View Paused Timer State (Priority: P1) 🎯 MVP

**Goal**: Paused fixture: sleeping Mr. Bloom on row 7 columns `[0, 1, 2, 3]` with baked cyan sleep effects, speech `Paused. Take your time.`, timer `18:42`, **RESUME** then **END**. Production `/widget` shows this fixture with no selector.

**Independent Test**: Open `http://127.0.0.1:1420/widget` after `npm run dev` in `frontend/`. Confirm exact copy, timer, button order, the four sleeping frames and their baked cyan effects, and that clicking RESUME/END does not throw (mock callbacks).

### Implementation for User Story 1

- [x] T025 [US1] Add `pausedFixture` in `frontend/src/lib/features/companion-widget/fixtures/paused.ts` (`kind: "paused"`, speech `Paused. Take your time.`, `timeText: "18:42"`, optional mock `onResume` / `onEnd`)
- [x] T026 [US1] Prerender and wire production `/widget` in `frontend/src/routes/widget/+page.ts` (`export const prerender = true`) and `frontend/src/routes/widget/+page.svelte` (thin page: `CompanionWidget` + `pausedFixture` only; no fixture selector; keep the page isolated)

**Checkpoint**: Paused widget is independently viewable at `/widget`

---

## Phase 4: User Story 2 - View Behind Schedule State (Priority: P1)

**Goal**: Behind-schedule fixture: atlas row 6 columns `[0, 2]`, orange alerts, exact delay speech, **no timer**, **REPLAN** / **LATER** / **OPEN**.

**Independent Test**: Pass `behindScheduleFixture` into `CompanionWidget` (temporarily on `/widget` if preview is not built yet). Confirm exact speech, no timer, button order, orange overlays, and callbacks do not throw. Restore paused as the production `/widget` default.

### Implementation for User Story 2

- [x] T027 [P] [US2] Add `behindScheduleFixture` in `frontend/src/lib/features/companion-widget/fixtures/behindSchedule.ts` (`kind: "behindSchedule"`, speech `We are 35 minutes behind. Adjust the remaining plan?`, no `timeText`, optional `onReplan` / `onLater` / `onOpen`)

**Checkpoint**: Behind-schedule data is typed and renderable without a timer

---

## Phase 5: User Story 4 - View Offline State (Priority: P2)

**Goal**: Offline fixture: atlas row 3 columns `[0, 1, 2, 3]`, Wi-Fi + red `×`, speech `Offline – changes will sync later.`, time `14:06`, **no action buttons**. Sequenced before Reminders so preview can switch all four states.

**Independent Test**: Render `offlineFixture`. Confirm happy pose, offline status (not color-only), exact speech and `14:06`, and **zero** action buttons. Missing callbacks cannot apply (variant has none). Restore paused on `/widget`.

### Implementation for User Story 4

- [x] T028 [P] [US4] Add `offlineFixture` in `frontend/src/lib/features/companion-widget/fixtures/offline.ts` (`kind: "offline"`, speech `Offline – changes will sync later.`, `timeText: "14:06"`, no callback fields)

**Checkpoint**: Offline presentation renders with no buttons and no backend connectivity check

---

## Phase 6: User Story 3 - View Reminders State (Priority: P2)

**Goal**: Reminders fixture: atlas row 4 column `[1]`, pink alerts, bell + `2 REMINDERS`, `Start Database` / `Review milestone`, **VIEW** then **DISMISS**.

**Independent Test**: Render `remindersFixture`. Confirm pink overlays, panel copy, two labels (full accessible text if ellipsized), button order, and callbacks. No reminder API.

### Implementation for User Story 3

- [x] T029 [P] [US3] Add `remindersFixture` in `frontend/src/lib/features/companion-widget/fixtures/reminders.ts` (`kind: "reminders"`, items `Start Database` and `Review milestone`, optional `onView` / `onDismiss`)
- [x] T030 [US3] Export all four fixtures from `frontend/src/lib/features/companion-widget/fixtures/index.ts` without importing that barrel from `CompanionWidget.svelte`

**Checkpoint**: All four fixtures exist; production `/widget` still defaults to paused

---

## Phase 7: Development-only preview

**Purpose**: FR-005 local fixture selector **outside** the production widget. Not loaded by the Tauri widget window.

- [x] T031 Add `frontend/src/routes/widget-preview/+page.ts` (`export const prerender = true`) and `frontend/src/routes/widget-preview/+page.svelte`: one `CompanionWidget`, selector **outside** the `680 × 289` box, switches `paused` | `behindSchedule` | `offline` | `reminders` one at a time; do not put the selector in `CompanionWidget.svelte` or `frontend/src/routes/widget/+page.svelte`; do not embed `widget-reference.svg`

---

## Phase 8: Tauri widget window

**Purpose**: Static single `companion-widget` window per `contracts/ui-presentation.md` and `quickstart.md`. `npm run tauri dev` opens only that window.

- [x] T032 Declare only `companion-widget` (`url: "/widget"`, **680×289**, `decorations: false`, `transparent: false`) in `frontend/src-tauri/tauri.conf.json`; do not add a runtime `WebviewWindow` constructor
- [x] T033 [P] Set `windows` to `["companion-widget"]` and only `core:default`, `core:window:allow-minimize`, `core:window:allow-toggle-maximize`, `core:window:allow-close`, `core:window:allow-start-dragging` in `frontend/src-tauri/capabilities/default.json`; do not add `core:webview:allow-create-webview-window`
- [x] T034 Wire `getCurrentWindow()` from `@tauri-apps/api/window` in `onMount` of `frontend/src/lib/features/companion-widget/components/molecules/WidgetTitleBar.svelte` for minimize, toggleMaximize, and close; keep drag on the title bar excluding controls; never call Tauri from `+page.ts` `load`

**Checkpoint**: `npm run tauri dev` from `frontend/` opens only the companion widget; `/widget` is `http://localhost:1420/widget` in dev

---

## Phase 9: Component and interaction tests

**Purpose**: Keep the installed Vitest stack covering atlas, layout, copy, callbacks, automated a11y, and source-only exclusion.

- [x] T035 Install `vitest@^5.0.0`, `jsdom`, `@testing-library/svelte@^5`, `@testing-library/user-event@^14`, `@testing-library/jest-dom@^6`, and `axe-core@^4` in `frontend/package.json`; add `"test": "vitest run"`; configure `sveltekit()` + `svelteTesting()` and `environment: "jsdom"` in `frontend/vite.config.js`; do not add Playwright
- [x] T036 [P] Test the cell mapping, in-grid and whole-pixel offsets, translate-before-scale order, and single-cell clipping in `frontend/src/lib/features/companion-widget/atlas.test.ts`
- [x] T037 [P] Test `CompanionWidget` in `frontend/src/lib/features/companion-widget/CompanionWidget.test.ts`: exact text and button order for all four fixtures; callbacks fire; actions stay visible and inert when callbacks are omitted; omitted `timeText` renders no timer; behind-schedule has no timer; offline has no buttons; reminder labels stay fully readable; keyboard activation; window controls survive a missing Tauri host; shared scene box; per-state layout config; axe-core on all four fixtures
- [x] T038 [P] Assert no runtime load of source-only art in `frontend/src/lib/features/companion-widget/assets.test.ts`: scan the whole frontend source tree plus rendered `img[src]` and inline styles for `removed reference artwork`, `widget-reference`, and base64 images; confirm the active runtime `mr-bloom-spritesheet.png` remains allowed while atlas tests enforce `1152×1152` metadata

---

## Phase 10: Polish & Cross-Cutting Concerns

**Purpose**: Manual visual/OS verification and quality gates. T039–T042 are outstanding; do **not** mark them from file existence or from passing automated tests.

- [ ] T039 Manually confirm in browser/Tauri network inspection that no `removed reference artwork/` path is ever requested; record the result in `specs/001-companion-widget/checklists/visual-acceptance.md`
- [ ] T040 Capture four screenshots at the spec canvas from `http://127.0.0.1:1420/widget-preview` (paused, behindSchedule, offline, reminders) into a scratch directory outside the repository; inspect every permitted animation frame and confirm no placeholders, no scrollbars/clipping/overlap, aligned backgrounds, exactly one normalized character cell, one far-left plant, and no leaf-balance pill; record gaps in `specs/001-companion-widget/checklists/visual-acceptance.md`
- [ ] T041 Compare the finished **reminders** fixture to the reference SVG at the spec canvas (side by side or overlay in an external viewer, not inside the app): proportions, component placement, spacing, border thickness, corner radii, colors, panel shape, title-bar layout, button dimensions, typography scale, and character position; confirm live Svelte chrome rather than SVG rasters/text paths; record the result in `specs/001-companion-widget/checklists/visual-acceptance.md`
- [ ] T042 Verify minimize, maximize/restore, close, and title-bar dragging on Windows via `npm run tauri dev`; repeat on Linux or explicitly document **unverified** in `specs/001-companion-widget/checklists/visual-acceptance.md`
- [x] T043 From `frontend/`, run `npm run check`, `npm run test`, and `npm run build`; confirm `frontend/build/widget.html` (and `widget-preview.html`) exist; fix failures without adding backend code

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: Start immediately (T001 then T002)
- **Foundational (Phase 2)**: Depends on Setup — **BLOCKS all user stories**
- **US1 (Phase 3)**: Depends on Foundational
- **US2 / US4 / US3 (Phases 4–6)**: Depend on Foundational; fixture files do not depend on each other
- **Preview (Phase 7)**: Depends on T026 and T025/T027/T028/T029/T030
- **Tauri (Phase 8)**: Depends on `/widget` (T026) and title bar (T019)
- **Tests (Phase 9)**: Depend on fixtures + `CompanionWidget` (T023+)
- **Polish (Phase 10)**: Depends on preview, Tauri, and tests

### User Story Dependencies

- **User Story 1 (P1, paused)**: After Phase 2; wires `/widget`
- **User Story 2 (P1, behind schedule)**: After Phase 2; fixture-only vs the shared organism
- **User Story 4 (P2, offline)**: After Phase 2; sequenced before Reminders per this task list
- **User Story 3 (P2, reminders)**: After Phase 2; barrel export T030 after the four fixture files

### Within Foundational

- T003 before styled components
- T004 and T005 before T006/T007/T023
- T008–T015 before atoms that consume those icons (T016, T018, T019, T021)
- T016–T018 before molecules T019–T022
- T019–T022 before T023
- T023 before any fixture wiring

### Parallel Opportunities

- T004 and T005 after T003
- T006, T007, T008–T015 after T005 (icons after T003)
- T017 and T018 with T016 after icons
- T020, T021, T022 with T019 after atoms
- T027, T028, T029 with T025 (four fixture files)
- T032 and T033
- T036, T037, T038 after T035

---

## Parallel Example: Foundational icons

```text
T008 WidgetTitleBar.svelte + leaf-icon.png
T009 paused baked cyan sleep effects (no overlay)
T010 ScheduleAlerts.svelte
T011 ReminderAlerts.svelte
T012 OfflineStatus.svelte
T013 BellIcon.svelte
T014 PlayIcon.svelte
T015 StopIcon.svelte
```

## Parallel Example: Fixtures after the shell

```text
T025 fixtures/paused.ts
T027 fixtures/behindSchedule.ts
T028 fixtures/offline.ts
T029 fixtures/reminders.ts
```

## Parallel Example: Tests after Vitest install

```text
T036 atlas.test.ts
T037 CompanionWidget.test.ts
T038 assets.test.ts
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Phase 1 Setup (asset check + feature folder)
2. Phase 2 Foundational shell
3. Phase 3 US1 paused `/widget`
4. **STOP and VALIDATE** at `http://127.0.0.1:1420/widget`

### Incremental Delivery

1. Setup + Foundational → shared widget chrome
2. US1 paused → `/widget` MVP
3. US2 behind schedule → second fixture
4. US4 offline → third fixture
5. US3 reminders → fourth fixture + barrel
6. Preview selector → all four without a backend
7. Static Tauri window → native controls
8. Vitest/Testing Library/axe-core → automated gates
9. Quality gates (`check` / `test` / `build`) then manual visual and per-OS verification

### Parallel Team Strategy

1. Together: Phase 1–2
2. Then: one person US1 `/widget`; others write T027/T028/T029 in parallel
3. Together: preview, Tauri, tests, polish

---

## Notes

- `[P]` only when files differ and dependencies are already done
- `[USn]` maps to spec stories: US1 paused, US2 behind schedule, US3 reminders, US4 offline
- Commit only when explicitly authorized
- Do not claim network-inspection, screenshot, reference-comparison, or per-OS verification passed until T039–T042 are executed
