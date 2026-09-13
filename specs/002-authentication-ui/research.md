# Research: Authentication UI/UX

## Controlled Cropping for Illustration

**Decision**: Use `object-fit: cover` on an `<img>` element to achieve controlled cropping for the left illustration asset (`authentication-background.png`) without stretching.

**Rationale**: The specification requires that the illustration crops in a controlled manner when space decreases, without distorting or stretching. `object-fit: cover` allows the image to scale proportionally to fill its container and crops any excess, preserving the pixel-art aspect ratio natively.

**Alternatives considered**: 
- `object-fit: contain` or `background-size: contain`: Rejected because it would introduce empty space (letterboxing) rather than cropping.
- Manual `@media` queries with different image crops: Rejected as too complex and difficult to maintain compared to native CSS image fitting properties.

## Form Layout primitives

**Decision**: Use CSS Flexbox and Grid for the right-hand column. A constrained maximum width (e.g., `max-width: 600px`) and `margin: 0 auto` will center the form area within the right column.

**Rationale**: The baseline is 1440x900, but it must be responsive. Flexbox and Grid provide predictable responsive behaviors without manual positioning, preventing unintended scrollbars or overlap.

**Alternatives considered**:
- Absolute positioning: Explicitly banned by the specification (except for decorative/chrome details).

## Tauri Window Integration

**Decision**: Declare both windows statically in `src-tauri/tauri.conf.json`. Keep `companion-widget` visible and configure one `main` window at `/auth` with `visible: false`. Resolve `main` by label through a typed service, then conditionally unminimize/show and focus it.

**Rationale**: Static configuration guarantees one authoritative instance and avoids duplicate-window races. A shared in-flight promise coalesces rapid open requests. Dynamic import of `@tauri-apps/api/window` occurs only after detecting the Tauri runtime, so browser preview and SSR paths do not execute host APIs.

**Alternatives considered**:
- Constructing `new WebviewWindow('main')` on every widget interaction: rejected because it introduces duplicate/error races and grants unnecessary create-window capability.
- Importing Tauri directly in each Svelte component: rejected because it spreads host concerns across presentation code and weakens browser-preview safety.
- A custom click timer: rejected because the native `dblclick` event expresses the required gesture without delaying existing single-click behavior.

## Local Typography

**Decision**: Use the repository-established system monospace stack (`Cascadia Mono`, `Lucida Console`, `Consolas`, monospace) for pixel-style display text and system sans-serif for smaller form copy.

**Rationale**: No font files are committed to the repository, and downloading runtime fonts or assets is prohibited. This is the closest local/system-only approximation; exact reference glyph shapes remain a documented visual limitation.
