# Research Notes: Widget Environment Rendering

## Background
The user requested the restructuring of static image assets (`daytime`, `season`, `weather`) from the repository root into `frontend/static/assets/widget/environment/`, and the actual implementation of the widget's environment layers utilizing them.

## Clarifications Resolved
- **Runtime vs Design Assets**: All images in the specified directories were validated as runtime assets meant for composing the Svelte widget scene.
- **Dynamic rain vs spritesheets**: The user clarified that rain animation must be handled entirely via frontend code. We implemented a container-query based CSS procedural rain rather than utilizing canvas, WebGL, or `requestAnimationFrame`.
- **Weather State**: The authenticated weather route uses the saved location, geocodes it with Open-Meteo, caches the normalized current condition, and falls back to `CLEAR` on provider errors.
- **Timezone Context**: The clock supplies the current instant; the scene formats that instant with the timezone saved during onboarding or in Settings.

## Tech Decisions
- **Implementation Strategy**: Standard file moving (`git mv` / PowerShell Move-Item) directly to target directories, followed by a global `grep` verify.
- **Naming Standardization**: `thunder-storm.png` was renamed to `storm-overlay.png` to align with lowercase kebab-case standards and project examples.
- **Clock store**: A central `clockStore.ts` using `readable()` with proper SSR guards was chosen over scattering `setInterval` within components.
