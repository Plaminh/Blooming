# Research: Compact Desktop Companion Widget

All Technical Context unknowns are resolved. Decisions use repository evidence (lockfile, Tauri config, routes, inspected PNGs).

## Installed versions (do not treat caret ranges as resolved)

From `frontend/package.json`, `frontend/package-lock.json`, and `frontend/src-tauri/Cargo.lock`:

| Package | package.json | Lockfile / Cargo.lock |
|---|---|---|
| `svelte` | `^5.56.3` | **5.57.0** |
| `@sveltejs/kit` | `^2.65.1` | **2.70.3** |
| `@sveltejs/adapter-static` | `^3.0.10` | **3.0.10** |
| `@sveltejs/vite-plugin-svelte` | `^7.1.2` | **7.3.0** |
| `vite` | `^8.0.16` | **8.2.2** |
| `svelte-check` | `^4.6.0` | **4.7.6** |
| `typescript` | `~6.0.3` | **6.0.3** |
| `@tauri-apps/api` | `^2` | **2.11.1** |
| `@tauri-apps/cli` | `^2` | **2.11.4** |
| Tauri crate | `version = "2"` | **2.11.5** |
| `vitest` | `^5.0.0` | installed |
| `jsdom` | `^29.1.1` | installed |
| `@testing-library/svelte` | `^5.4.2` | installed |
| `@testing-library/user-event` | `^14.6.7` | installed |
| `@testing-library/jest-dom` | `^6.9.1` | installed |
| `axe-core` | `^4.13.0` | installed |

No extra Tauri plugins are registered. Playwright is not installed.

**Test tools**: `npm run check` (`svelte-kit sync && svelte-check`), `npm run test` (`vitest run`), `npm run build`.

**Routes**: `/widget` (production companion, prerendered, default paused fixture) and `/widget-preview` (dev fixture selector). Root `+layout.ts` sets `ssr = false`. There is no application-shell route group.

**Feature convention**: `src/lib/features/companion-widget/` with `components/atoms|molecules|organisms`, `fixtures/`, `types/`, `styles/`, and `model/`.

**SvelteKit adapter**: `@sveltejs/adapter-static` with `fallback: "index.html"`. `/widget` and `/widget-preview` set `prerender = true`.

**Tauri**: one static window, `label: "companion-widget"`, `url: "/widget"`, `680 × 289`, `decorations: false`, `transparent: false`. `devUrl` `http://localhost:1420`, `frontendDist` `../build`. Capabilities: `core:default` plus the four `core:window:*` permissions in `plan.md`, for `["companion-widget"]` only.

---

## Decision: Feature module `companion-widget`, not `src/lib/components/widget/`

- **Decision**: Implement `frontend/src/lib/features/companion-widget/` using atoms / molecules / organisms, plus `fixtures/`, `types/`, `styles/`, `model/`. Keep `/widget` and `/widget-preview`. Keep Tauri at `frontend/src-tauri/`.
- **Rationale**: Matches the feature-module layout and the required Atomic Design split. Widget chrome is pixel-specific and stays inside this feature.
- **Alternatives considered**: Nested `src/lib/components/widget/` (explicitly forbidden). Putting `src-tauri` under `src/` (incorrect).

## Decision: Runtime PNGs vs source-only reference

- **Decision**: Load only normalized/runtime files under `frontend/static/assets/widget/`. Treat `design-assets/widget/references/widget-reference.svg` and the irregular source artwork as source-only inputs: never requested by the app or edited in place.
- **Rationale**: Runtime roles and dimensions are listed in `design-assets/widget/README.md`; the source/runtime character-atlas distinction and mapping are authoritative in `plan.md` and `data-model.md`.
- **Alternatives considered**: Merge sky+bushes into one PNG (violates VR-008). Recreate Mr. Bloom in SVG (violates VR-009). Render the reference as the widget (violates VR-015). Trace its text paths into CSS (forbidden).

## Decision: normalized character atlas and compatible sequences

- **Decision**: Deterministically normalize each exact source row into four isolated runtime cells, then animate only the compatible per-state columns recorded in [data-model.md](./data-model.md).
- **Rationale**: The source's four horizontal sprites are irregularly positioned, can include detached marks, and overlap adjacent row boundaries. Dividing its full width into equal quarters or copying an entire raw row into every cell leaks foreign pixels. Normalization makes clipping reliable. Paused deliberately uses all four supplied sleeping frames with their baked effects; other states still exclude effects that contradict separate overlays.
- **Alternatives considered**: CSS-only scaling or overflow changes (cannot repair incorrect source boundaries). Using every column for states with contradictory overlays. A character component per state (unnecessary duplication).

## Decision: Shared scene box for mismatched backgrounds

- **Decision**: Composite both layers in a wrapper whose intrinsic size is the **sky**, with both images absolutely positioned bottom-left, the wrapper clipped, and the wrapper scaled as one unit. Do not size or `object-fit` the images independently. Implementation shape: [plan.md](./plan.md).
- **Rationale**: Bushes are 1px wider and 1px shorter, so independent `cover` scaling uses different aspect ratios (`1880/837` versus `1881/836`) and drifts. Bottom-left alignment keeps foliage planted; the extra bushes pixel is clipped on the right and the uncovered sky pixel sits at the top.
- **Alternatives considered**: Stretch bushes to the sky size (distorts pixels). Crop assets (forbidden). Ignore the 1px delta (fails SC-010). A `transparent: true` window to see the desktop through gaps (unnecessary; the sky is opaque).

## Decision: One typed layout config per state

- **Decision**: Keep shared visual tokens in `styles/widget-theme.css` and put every state-specific coordinate in a typed `model/layout.ts` record, emitted as CSS custom properties on the widget root.
- **Rationale**: The four states have genuinely different compositions — a tall reminders panel, a wide replanning bubble, compact paused/offline bubbles with a dominant clock — so panel widths and heights must differ. All cream panels share a top-left origin `(x: 215, y: 60)` from `PANEL_POSITION`, and Mr. Bloom shares `(left: 70, bottom: 4)`. Centralizing the numbers keeps them reviewable and keeps components free of unexplained magic offsets. Runtime spritesheet normalization left-aligns each row to a shared slot, so the character anchor is shared. Status overlay coordinates remain state-specific.
- **Alternatives considered**: Duplicate coordinates in each component (drifts, unreviewable). Keep per-state values as CSS variables in the theme (mixes shared tokens with state geometry, and every state pays for the others' variables). A layout store or context (forbidden speculative abstraction).

## Decision: Static `companion-widget` window, opaque, `/widget`

- **Decision**: Declare only one window in `tauri.conf.json` with `label: "companion-widget"`, `url: "/widget"`, `width: 680`, `height: 289`, `decorations: false`, `transparent: false`. Startup creates only the companion widget. Never `new WebviewWindow`. Close uses `getCurrentWindow()` from `@tauri-apps/api/window`. Drag via `data-tauri-drag-region`. Capabilities cover that window plus the four `core:window:*` permissions listed in `plan.md`.
- **Rationale**: The spec needs a dedicated frameless widget sized to the VR-001 canvas so reference comparison is not distorted. Sky is opaque RGB, so transparency is not required. Static declaration is duplicate-safe without `allow-create-webview-window`.
- **Alternatives considered**: Runtime `WebviewWindow` (needs extra capability; easy to duplicate). `transparent: true` (old plan; no evidence). Hash URLs (`#/widget`) — fights SvelteKit routing. Loading `/widget-preview` in Tauri (would ship the fixture selector). Closing the widget with `hide()` (close control should close; next process start restores the static window).

## Decision: Prerender `/widget` and `/widget-preview`, keep SPA fallback

- **Decision**: Keep `adapter({ fallback: "index.html" })` and `ssr = false`. Add `prerender = true` on the two widget routes so production emits `widget.html` / `widget-preview.html`. Dev: `http://localhost:1420/widget`. Production: Tauri asset protocol + prerendered file, with SPA fallback as backup. Call Tauri window APIs only in `onMount`, never in `load`.
- **Rationale**: Tauri docs recommend adapter-static SPA mode because `load` cannot use Tauri during prerender. Custom-protocol history routes can 404 if no file exists; prerendering `/widget` makes a real file while the rest of the app can stay SPA. Port 1420 is already required by Vite+Tauri.
- **Alternatives considered**: Hash routing. A second Vite HTML entry. Prerendering the entire app . Relying only on fallback (works in some Tauri versions, not a deterministic Windows/Linux story).

## Decision: Vitest 5 + Testing Library + axe-core; not Playwright

- **Decision**: Use the installed `vitest@^5.0.0`, `jsdom`, `@testing-library/svelte@^5`, `@testing-library/user-event@^14`, `@testing-library/jest-dom@^6`, and `axe-core@^4` for atlas, layout-contract, copy/order, callbacks, optional props, automated a11y, and source-only-exclusion tests. Visual comparison, live network inspection, and native window checks stay manual. jsdom/axe do not prove real rendered color contrast. Do not add Playwright, Storybook, or a CSS/icon framework.
- **Rationale**: Constitution Principle 6 requires frontend state-transition tests. Vitest 5 lists `vite: ^6.4.0 \|\| ^7.0.0 \|\| ^8.0.0`, which matches lockfile Vite 8.2.2. Testing Library is the Svelte-documented component approach. axe-core covers automated SC-008 checks. Playwright would be a second runner and is not needed for DOM assertions.
- **Alternatives considered**: Playwright-only (weak for prop/callback unit tests, heavy). svelte-check only (cannot assert callbacks or atlas math). vitest Browser Mode + Playwright provider (extra packages, still Playwright).

## Decision: State-relevant optional callbacks on a `kind` union

- **Decision**: Model presentation as a discriminated union with `kind` and optional per-variant callbacks and optional `timeText`. Fixtures stay outside `CompanionWidget.svelte`.
- **Rationale**: The previous data model forced seven callbacks on every state and required `timeText` on paused/offline. That crashes easily when a handler is omitted and invents timers on behind-schedule.
- **Alternatives considered**: Parallel boolean flags (multiple states at once). A global store (forbidden). Required callbacks with no-op defaults inside the organism (hides fixture mistakes).

## Decision: No HTTP contracts; UI/window contract only

- **Decision**: Skip OpenAPI. Document the window label/URL and the presentation union in `contracts/ui-presentation.md`.
- **Rationale**: FR-007 forbids backend work. The user-facing contract is the widget window plus typed props.
- **Alternatives considered**: Inventing REST endpoints for reminders/offline (out of scope).
