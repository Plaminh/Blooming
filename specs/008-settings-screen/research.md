# Phase 0: Outline & Research

## Technical Context Clarifications

### Tauri Autostart Plugin
- **Decision**: Fallback to local typed UI state.
- **Rationale**: The `tauri-plugin-autostart` is not installed in `Cargo.toml`. The specification explicitly forbids adding new Tauri plugins without approval. We will store the toggle state locally and treat the platform integration as unfinished.
- **Alternatives considered**: None, as we are strictly prohibited from adding plugins.

### Widget Window Label
- **Decision**: The label is `"companion-widget"`.
- **Rationale**: Found in `tauri.conf.json` under `app.windows`. We will use `@tauri-apps/api/window` to interact with it for the "Keep widget on top" setting.
- **Alternatives considered**: N/A, we must use the configured label.

### Settings Store
- **Decision**: Create a local, strongly-typed settings store using Svelte 5 runes (`$state`).
- **Rationale**: The specification requires typed frontend settings without inventing a backend API. There is no existing global settings store. A local Svelte 5 store provides a reactive, single source of truth for the session.
- **Alternatives considered**: LocalStorage persistence. We can use LocalStorage, but since the spec emphasizes "without inventing a backend API", a simple local in-memory store initialized with defaults is the safest start.

### Form Controls
- **Decision**: Implement the form controls (toggle, input, select) within the Settings feature directory for now, unless they map perfectly to simple generalized atoms.
- **Rationale**: No existing shared form controls are found in `src/lib/shared/components/atoms` (only AppIcon, SpriteRenderer). To avoid polluting the shared space without a design system, we will create Settings-specific molecules/atoms and only promote them to shared if completely generalized.
- **Alternatives considered**: Creating them in `shared` directly.

### Visual Reference
- **Decision**: The native dimensions of `removed reference artwork` are exactly **1540x975**. We will use this viewport size for visual comparison.
- **Rationale**: Confirmed via PowerShell image inspection.
