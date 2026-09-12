# Quickstart: Companion Widget Validation

This guide is the runnable check for the plan. Launch behavior matches `plan.md`: **`npm run tauri dev` from `frontend/` starts only the companion widget window that loads `/widget`.** Do not expect a runtime “open widget” button.

Visual and cross-platform checks are **not** already passed.

## Prerequisites

- Node.js capable of the current Vite 8 / SvelteKit 2 toolchain
- Rust toolchain for Tauri 2 (`frontend/src-tauri`)
- Working directory: `frontend/` unless noted
- Runtime PNGs present:
  - `static/assets/widget/backgrounds/default-sky.png`
  - `static/assets/widget/backgrounds/background-bushes.png`
  - `static/assets/widget/characters/mr-bloom-spritesheet.png`
  - `static/assets/widget/icons/leaf-icon.png`
  - `static/assets/widget/plants/*-spritesheet.png`
- Source-only art under `../design-assets/` is never copied or served (spec VR-015)

## 1. Types and unit/component tests

The Vitest stack from `plan.md` is already installed (`vitest@^5`, `jsdom`, `@testing-library/svelte@^5`, `@testing-library/user-event@^14`, `@testing-library/jest-dom@^6`, `axe-core@^4`):

```bash
npm run check
npm run test
```

Both commands must be clean. The suite covers the atlas mapping and clipping, per-state layout config, fixture copy and button order, callbacks and omitted callbacks, omitted `timeText`, keyboard activation, accessible reminder labels, axe-core on all four fixtures, and source-only asset exclusion across the frontend source tree. jsdom and axe-core do not prove real rendered color contrast.

## 2. Browser preview (fixtures)

```bash
npm run dev
```

Vite is pinned to **port 1420** (`vite.config.js`, Tauri `devUrl`). Open:

- Production-shaped widget: `http://127.0.0.1:1420/widget`
  Renders `CompanionWidget` with the default **paused** fixture. No fixture selector.
- Development preview: `http://127.0.0.1:1420/widget-preview`
  Fixture selector **outside** the `680 × 289` widget. Cycle `paused`, `behindSchedule`, `offline`, `reminders`.

Manual checks (record results in [checklists/visual-acceptance.md](./checklists/visual-acceptance.md)):

- One state visible at a time
- Layered sky + bushes aligned; no seam or drift
- Supplied leaf PNG in the title bar; no leaf-balance pill
- One normalized character cell and one selected plant; no neighboring sprite fragments throughout each configured sequence
- Paused cycles its four cleanly cropped sleeping frames, including the cyan sleep effects baked into those frames; other states retain their orange, pink, and offline semantic overlays
- Plant at the far-left edge behind Mr. Bloom, never between the content panel and buttons
- Capture four screenshots at the spec canvas, preserving its aspect ratio. Keep captures outside the repository, and point any capture tool's browser profile at an OS temporary directory.
- Compare the **reminders** capture side by side with the reference SVG in an external viewer
- Resize 90–110%: no scrollbars, clipping, or overlap
- DevTools network: no request for any `design-assets/` path

## 3. Production static files

```bash
npm run build
```

Confirm `build/widget.html` (and `build/widget-preview.html`) exist because those routes set `prerender = true`, while `adapter-static` still has `fallback: "index.html"` for the SPA shell.

Optional:

```bash
npm run preview
```

Open `/widget` and `/widget-preview` on the preview port and repeat the fixture checks.

## 4. Tauri windows (deterministic launch)

From `frontend/`:

```bash
npm run tauri dev
```

**Expected startup (same as the plan):**

1. Window `companion-widget` — frameless, opaque, **680×289**, URL `/widget` (`http://localhost:1420/widget` in dev).

There is no second spawn path. Closing and relaunching `tauri dev` is how the widget returns after it is closed.

Native checks:

- Drag the dark teal title bar (not the control buttons)
- Minimize, maximize/restore, close via the custom controls (`getCurrentWindow()`)
- Close widget → the process exits (this is the only window)
- Windows: perform here. Linux: perform on a Linux host, or record **unverified** — do not claim it passed

## 5. Out of scope (do not validate as this feature)

Real timers, focus persistence, AI replan, reminder scheduling, connectivity probes, backend APIs, Storybook, and rendering the reference SVG as the widget.
