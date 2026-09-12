# Implementation Plan: Compact Desktop Companion Widget

**Branch**: `feature/ui-ux` | **Date**: 2026-09-11 | **Spec**: [specs/001-companion-widget/spec.md](./spec.md)

**Input**: Feature specification from `/specs/001-companion-widget/spec.md`

**Note**: This plan is synchronized to the current implementation. Runtime assets, frontend/Tauri layout, and packages are those in `frontend/package.json`, `frontend/package-lock.json`, and `frontend/src-tauri/`.

## Summary

Build a compact, frameless Tauri companion window (`companion-widget`) that loads the SvelteKit `/widget` route at the spec canvas (spec VR-001). Presentation is a typed four-state discriminated union (`paused` | `behindSchedule` | `offline` | `reminders`) with mock fixtures only. The scene composites two runtime background PNGs, one animated Mr. Bloom clipped from a normalized runtime atlas, and one lifecycle plant frame. The supplied leaf PNG is the title-bar logo. Layout tokens come from inspecting the source-only reference SVG under the restrictions in spec VR-015.

## Technical Context

**Language/Version**: TypeScript 6.0.3 (lockfile), Svelte 5.57.0 (lockfile; `package.json` asks `^5.56.3`), HTML/CSS. Rust edition 2021 in `frontend/src-tauri`.

**Primary Dependencies** (resolved from `frontend/package-lock.json` and `frontend/src-tauri/Cargo.lock`):
- `@sveltejs/kit` 2.70.3 (`package.json` `^2.65.1`)
- `@sveltejs/adapter-static` 3.0.10
- `@sveltejs/vite-plugin-svelte` 7.3.0
- `vite` 8.2.2 (`package.json` `^8.0.16`)
- `svelte-check` 4.7.6
- `@tauri-apps/api` 2.11.1
- `@tauri-apps/cli` 2.11.4
- Tauri crate `2.11.5`
- Vitest 5 + jsdom + Testing Library (Svelte, user-event, jest-dom) + axe-core (see Testing Decision)

**Storage**: N/A (UI presentation only; no backend, database, or persistence)

**Testing (current repo)**: `npm run check` (`svelte-check`), `npm run test` (`vitest run`), and `npm run build`. Installed: Vitest 5, jsdom, `@testing-library/svelte`, `@testing-library/user-event`, `@testing-library/jest-dom`, and axe-core. Playwright is not installed and is not added.

**Testing (this feature)**: Keep those automated gates. jsdom and axe-core cover DOM structure, names, and automated a11y rules; they do not prove real rendered color contrast. Live visual and platform checks stay in [quickstart.md](./quickstart.md).

**Target Platform**: Windows and Linux desktop via Tauri 2. macOS is out of constitution scope.

**Project Type**: Desktop UI feature inside the existing SvelteKit + Tauri frontend

**Performance Goals**: Instant fixture switching, no scrollbars at `680 × 289` and 90–110% of that size, crisp pixel rendering, and no animation work for states with one permitted frame

**Constraints**:
- Canvas, asset, and source-only rules per spec VR-001 / VR-008 / VR-015; no backend per spec FR-007
- Frameless opaque window (`decorations: false`, `transparent: false`)
- No Storybook, UI kit, icon pack, CSS framework, or app-wide store
- Do not SVG-recreate Mr. Bloom
- Mr. Bloom animates only through each state's permitted atlas columns; plants stay presentation-only

**Scale/Scope**: One widget window, one preview route, four fixtures, one character component, two background layers, custom chrome/indicators only

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-checked after Phase 1 design.*

- [x] Spec-driven workflow: Specify → Plan (this command). Tasks are explicitly deferred to `/speckit-tasks`.
- [x] Stack boundaries preserved: SvelteKit/TypeScript/Vite UI + Tauri 2/Rust shell. No FastAPI, PostgreSQL, or new backend surface.
- [x] Deterministic ownership: fixtures are development/presentation mocks, isolated from production domain state. UI does not invent timers, connectivity, or reminder scheduling.
- [x] Explicit contracts: TypeScript discriminated union in `data-model.md`; window/UI contract in `contracts/ui-presentation.md`. No HTTP API.
- [x] Simplest design that satisfies the spec: one feature module, static single window, no extra frameworks.
- [x] Testable behavior: constitution requires frontend state-transition tests. The feature uses the installed Vitest + Testing Library + axe-core stack.
- [x] UX: missing optional time text and callbacks degrade safely; offline has no actions; long reminder labels stay accessible.
- [x] Resource/platform: Windows/Linux; widget runs independently; no polling; static art only.
- [x] Security/privacy: no secrets, no network calls, decorative images excluded from the accessibility tree.

No constitution violations. Vitest satisfies Principle 6; it is not a speculative extra stack.

## Project Structure

### Documentation (this feature)

```text
specs/001-companion-widget/
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
│   └── ui-presentation.md
├── spec.md
└── checklists/
    ├── requirements.md
    └── visual-acceptance.md
```

`tasks.md` records implementation and remaining manual checks.

### Source Code (implemented)

Feature UI lives under `frontend/src/lib/features/companion-widget/`. Production route is `/widget`. Preview is `/widget-preview`. Tauri stays at `frontend/src-tauri/` (not under `src/`). Widget chrome does not use shared application-shell components.

```text
frontend/
├── package.json
├── svelte.config.js
├── vite.config.js
├── src/
│   ├── lib/
│   │   ├── features/
│   │   │   └── companion-widget/
│   │   │       ├── components/
│   │   │       │   ├── atoms/
│   │   │       │   │   ├── BellIcon.svelte
│   │   │       │   │   ├── MrBloomCharacter.svelte
│   │   │       │   │   ├── OfflineStatus.svelte
│   │   │       │   │   ├── PixelStatus.svelte
│   │   │       │   │   ├── PlantSprite.svelte
│   │   │       │   │   ├── PlayIcon.svelte
│   │   │       │   │   ├── ReminderAlerts.svelte
│   │   │       │   │   ├── ScheduleAlerts.svelte
│   │   │       │   │   ├── StopIcon.svelte
│   │   │       │   │   ├── TimerDisplay.svelte
│   │   │       │   │   ├── WidgetButton.svelte
│   │   │       │   │   └── WindowControlButton.svelte
│   │   │       │   ├── molecules/
│   │   │       │   │   ├── ActionGroup.svelte
│   │   │       │   │   ├── ReminderPanel.svelte
│   │   │       │   │   ├── SpeechBubble.svelte
│   │   │       │   │   ├── WidgetSceneBackground.svelte
│   │   │       │   │   └── WidgetTitleBar.svelte
│   │   │       │   └── organisms/
│   │   │       │       └── CompanionWidget.svelte
│   │   │       ├── fixtures/
│   │   │       ├── types/
│   │   │       │   └── presentation.ts
│   │   │       ├── styles/
│   │   │       │   └── widget-theme.css
│   │   │       ├── model/
│   │   │       │   ├── atlas.ts
│   │   │       │   ├── layout.ts
│   │   │       │   ├── actions.ts
│   │   │       │   └── plants.ts
│   │   │       ├── CompanionWidget.test.ts
│   │   │       ├── atlas.test.ts
│   │   │       ├── assets.test.ts
│   │   │       ├── plants.test.ts
│   │   │       └── index.ts
│   │   └── shared/
│   │       └── styles/global.css            # root layout CSS only; not widget chrome
│   └── routes/
│       ├── +layout.ts                       # ssr = false
│       ├── +layout.svelte                   # global CSS only
│       ├── widget/
│       │   ├── +layout.svelte               # scales the 680×289 canvas to the window
│       │   ├── +page.ts                     # prerender = true
│       │   └── +page.svelte                 # thin: CompanionWidget + paused fixture
│       └── widget-preview/
│           ├── +layout.svelte
│           ├── +page.ts                     # prerender = true
│           └── +page.svelte                 # fixture selector OUTSIDE the widget
├── src-tauri/
│   ├── tauri.conf.json                      # single companion-widget window
│   ├── capabilities/default.json            # that window + window APIs
│   └── src/
├── static/
│   └── assets/
│       └── widget/
│           ├── backgrounds/
│           │   ├── default-sky.png          # runtime, 1880×837, RGB
│           │   └── background-bushes.png    # runtime, 1881×836, RGBA
│           ├── characters/
│           │   └── mr-bloom-spritesheet.png # normalized runtime atlas, 1152×1152, 4×8, RGBA
│           ├── icons/
│           │   └── leaf-icon.png            # runtime title-bar logo
│           └── plants/
│               └── *-spritesheet.png        # normalized 8×2 plant atlases, 2304×896
└── design-assets/widget/
    └── references/
        └── widget-reference.svg                 # SOURCE-ONLY visual reference; never imported
```

**Structure Decision**: Feature module (`src/lib/features/<name>/`) plus Atomic Design **inside this feature only** (`atoms`, `molecules`, `organisms`). Keep route files thin. Do not introduce `src/lib/components/widget/`. Do not place `src-tauri` under `src/`. Layout, atlas, actions, and plant math live in `model/`.

## Runtime vs source-only assets

| Path | Role | Load at runtime? |
|---|---|---|
| `frontend/static/assets/widget/backgrounds/default-sky.png` | Opaque sky/city layer | Yes, `/assets/widget/backgrounds/default-sky.png` |
| `frontend/static/assets/widget/backgrounds/background-bushes.png` | Transparent foliage layer over sky | Yes, `/assets/widget/backgrounds/background-bushes.png` |
| `frontend/static/assets/widget/characters/mr-bloom-spritesheet.png` | Normalized animated 4×8 Mr. Bloom atlas | Yes, `/assets/widget/characters/mr-bloom-spritesheet.png` |
| `frontend/static/assets/widget/icons/leaf-icon.png` | Decorative title-bar logo beside `BLOOMING` | Yes, `/assets/widget/icons/leaf-icon.png` |
| `frontend/static/assets/widget/plants/*-spritesheet.png` | Normalized 8×2 plant atlases | Yes, one species at a time |
| `design-assets/widget/references/widget-reference.svg` | Source-only visual reference | **Never** (spec VR-015) |

Plant progression is presentation-only. Reward and garden logic stay outside this feature; the widget has no leaf-balance badge.

## Reference metrics

Read from `design-assets/widget/references/widget-reference.svg` (the composite target for **reminders**) without importing or editing it. The SVG is a hybrid export: vector shapes plus embedded rasters, with labels as outlined paths rather than `<text>`, so all copy is re-authored as real text.

Implemented geometry is the single source of truth in `model/layout.ts`. All four states share `PANEL_POSITION` `{ x: 215, y: 60 }` and `MR_BLOOM_POSITION` `{ left: 70, bottom: 4 }`. Panel size, timer, status overlay, and action-row metrics stay per-state:

| `kind` | Panel | Timer | Actions (`top`, `right`, `gap`, primary×secondary×height) |
|---|---|---|---|
| `paused` | `250 × 86` | `top: 78`, `right: 18` | `220`, `12`, `9`, `164 × 132 × 58` |
| `behindSchedule` | `366 × 90` | none | `213`, `14`, `7`, `129 × 149 × 58` |
| `offline` | `252 × 111` | `top: 78`, `right: 20` | `220`, `12`, `9`, `164 × 132 × 58` |
| `reminders` | `328 × 128` | none | `210`, `14`, `9`, `129 × 149 × 58` |

Plant slot is `{ left: -4, bottom: 4 }` in every state. The character viewport is `220 × 110`. Title-bar controls start at `left: 548`, `top: 12` (`35×33`, `33×33`, `35×33`). The leaf PNG is drawn at `40×40` inside a `28×31` logo slot. Cream fill `#FAEFD5`, radius 4, and stroke 4 match the theme tokens.

The source-only SVG remains the reminders comparison target (spec VR-015). Its traced coordinates are not the implemented layout.

## Atlas clipping strategy

The authoritative source is **1536 × 1152** with eight regular 144px rows but irregular horizontal sprite placement and up to seven centered boundary rows from the preceding sprite. `tools/widget-assets/NormalizeWidgetAssets.cs` detects the four sprite clusters in each exact row, clears that adjacent-row bleed without removing detached right-edge effects, preserves pixel dimensions, then left-aligns every frame in a row to a shared slot (the widest frame in that row) and bottom-aligns it into a **1152 × 1152** runtime atlas: **4 × 8**, **288 × 144** cells. The shared slot keeps the body still when effect art (rays, Zs, alerts) changes width. The character viewport is exactly one normalized cell with `overflow: hidden`, rendered at `220 × 110`, so neighboring frames cannot leak. State rows and permitted frame sequences live in [data-model.md](./data-model.md): `paused` row 7 `[0, 1, 2, 3]`, `behindSchedule` row 6 `[0, 2]`, `offline` row 3 `[0, 1, 2, 3]`, `reminders` row 4 `[1]`. Paused uses the cyan sleep effects baked into the supplied frames. Other states skip incompatible baked effects. Animation resets on state changes and freezes on a permitted frame for `prefers-reduced-motion: reduce`.

## Background layering

Sky is **1880 × 837** (opaque RGB); bushes are **1881 × 836** (RGBA). Both layers share one scene box equal to the sky size, both anchored bottom-left, clipped by the wrapper, and scaled as a single unit rather than per image. That keeps the 1px source mismatch from drifting: the extra bushes pixel is clipped on the right and the uncovered sky pixel sits at the top. Both images are `aria-hidden` with empty `alt`. Rationale and rejected alternatives: [research.md](./research.md).

## Tauri window lifecycle (concrete)

**Declaration**: **Static** in `frontend/src-tauri/tauri.conf.json` `app.windows`. Not created with `new WebviewWindow()` at runtime.

| Window | `label` | URL | Size | Decorations | Transparent |
|---|---|---|---|---|---|
| Companion widget | `companion-widget` | `/widget` | **680 × 289** | `false` | **`false`** |

Sky is fully opaque; no repository evidence requires transparency. Keep `transparent: false`.

**Startup** (`npm run tauri dev` and packaged app): Tauri creates only the companion widget window. This is the only launch path. Quickstart uses the same command and the same expectation.

**Duplicates**: The config is the single constructor. Implementation must not call `WebviewWindow` with label `companion-widget`. Do not add `core:webview:allow-create-webview-window`.

**Close**:
- Widget close control: `getCurrentWindow().close()` from `@tauri-apps/api/window` on the current widget window. With only this window, the process exits.
- Minimize / maximize-restore: `minimize()` and `toggleMaximize()` on the current window.
- Drag: `data-tauri-drag-region` on the title bar, excluding the three control buttons.

**Capabilities** (`frontend/src-tauri/capabilities/default.json`): `windows` is `["companion-widget"]`. Permissions:
- `core:default`
- `core:window:allow-minimize`
- `core:window:allow-toggle-maximize`
- `core:window:allow-close`
- `core:window:allow-start-dragging`

No extra plugins. Windows and Linux only.

### `/widget` resolution

**Vite / Tauri development**: `tauri.conf.json` `devUrl` is `http://localhost:1420`. `vite.config.js` pins port `1420` with `strictPort: true`. The widget window URL `/widget` loads `http://localhost:1420/widget`. Root `+layout.ts` already sets `ssr = false`. `/widget` is isolated.

**Production `adapter-static`**: existing `fallback: "index.html"` stays. Add `export const prerender = true` on `/widget` and `/widget-preview` so the build emits a real `widget.html` (SvelteKit `trailingSlash: 'never'` default) instead of relying only on SPA fallback. Widget `onMount` may call Tauri APIs; do **not** call Tauri inside `load` (prerender cannot use them). After `npm run build`, confirm `frontend/build/widget.html` exists. If a platform’s asset protocol only resolves the file with a `.html` suffix, set the configured window `url` to the emitted filename — still the same `/widget` route, not a second app.

**Preview**: `/widget-preview` is for `npm run dev` / `vite preview`. The Tauri widget window never loads it.

## Presentation model

Discriminated union on `kind` with **only** those four values. One active state. Optional `timeText?: string`. Callbacks live **on the variant that uses them** and are optional so missing handlers do not throw. Fixtures live under `fixtures/` and are imported by preview (and the production page’s default paused fixture). Reminder `label` is the accessible name; visual CSS may ellipsis.

Svelte 5 conventions already in the repo: PascalCase components, `$props()`, typed props objects. Widget-specific buttons are feature-local (`WidgetButton.svelte`).

## Testing decision

**Installed stack** (in `frontend/package.json`):

| Package | Why |
|---|---|
| `vitest@^5.0.0` | Supports Vite `^6.4 \|\| ^7 \|\| ^8`; matches lockfile Vite 8.2.2 |
| `jsdom` | Vitest DOM environment for component tests |
| `@testing-library/svelte@^5` | Svelte 5 `render` / semantic queries |
| `@testing-library/user-event@^14` | Keyboard operation |
| `@testing-library/jest-dom@^6` | DOM matchers |
| `axe-core@^4` | SC-008 automated accessibility checks |

`npm run test` runs `vitest run`. Vitest is configured in `vite.config.js` with `sveltekit()` + `svelteTesting()` from `@testing-library/svelte/vite`, `environment: 'jsdom'`. The setup file is `frontend/src/vitest-setup.ts` so jest-dom matcher types are inside the `svelte-check` program.

Automated gates: `npm run check`, `npm run test`, `npm run build`. Automated scope is T035–T038 and T043 in [tasks.md](./tasks.md). jsdom/axe do not prove real rendered color contrast. Manual scope — reminders-versus-reference comparison, live network inspection, and per-OS window checks — is [quickstart.md](./quickstart.md), with results in [checklists/visual-acceptance.md](./checklists/visual-acceptance.md). Manual results are not assumed to pass.

**Not used**: Playwright (not installed; not added). Storybook (forbidden).

## Design tokens & chrome

Two files split the styling concerns:

- `styles/widget-theme.css` — shared visual tokens only (size, border, radius, stroke, palette, font), scoped to `.companion-widget` and imported by the organism. Colors come from the reference: `#0E3052` / `#FAEFD5` / `#489D58` / `#2A705A` / `#626C69` / `#CEE4D1` / `#3A5364` / `#D5E2E9` / `#213D59`.
- `model/layout.ts` — typed per-state geometry (panel rect, character anchor, timer position, action metrics) emitted as CSS custom properties on the widget root. Coordinates never live in the theme. All states share the character anchor and top-left panel position, while panel dimensions and status overlays remain state-specific.

No glassmorphism, generic dashboard cards, or extra shadows. Do not paste SVG path `d` strings into CSS.

Custom SVG/CSS: orange alerts, pink alerts, bell, play, stop, Wi-Fi+`×`, window controls — authored as components, not extracted from the reference file. The title logo is the supplied `leaf-icon.png`, not custom SVG/CSS. Paused sleep marks come from the atlas frames, not a separate overlay component.

## Implementation order

1. Types + atlas constants + fixtures
2. Background scene + character clip
3. Atoms → molecules → `CompanionWidget`
4. Thin `/widget` and `/widget-preview` routes + prerender flags
5. Static Tauri window + capabilities + title-bar window APIs
6. Vitest stack and automated tests (`npm run check` / `npm run test` / `npm run build`)
7. Manual visual verification per `quickstart.md`, recording honest results and any unverified OS

## Complexity Tracking

None. No constitution violations.
