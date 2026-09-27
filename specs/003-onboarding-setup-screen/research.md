# Research

## Unknowns Resolved

### 1. Fonts and Theming
- **Decision**: Use the shared tokens in `frontend/src/lib/shared/styles/theme.css`. Headings use `--bloom-display-font` ("Cascadia Mono", "Lucida Console", Consolas, monospace). Body copy and inputs use `--bloom-body-font` (Inter, "Segoe UI", Arial, sans-serif). Colors and chrome use `--bloom-*` variables, not `--auth-*`.
- **Rationale**: Keeps the onboarding screen on the same desktop theme as the rest of the app and avoids a feature-local theme file.
- **Alternatives considered**: A feature-local `styles/theme.css` or reuse of `--auth-*` tokens from the authentication view.

### 2. Asset Identification
- **Decision**: The background image is `/assets/onboarding/onboarding-background.png`. The leaf icon is `/assets/icons/leaf-icon.png`. Title-bar and window-control styles come from the shared `theme.css`.
- **Rationale**: Reuses the provided onboarding background and existing standard assets.
- **Alternatives considered**: Attempting to slice the reference image, which is fragile and violates the reuse constraint.

### 3. Atomic Design Mapping
- **Decision**: Map the UI to the following structure within `src/lib/features/onboarding-setup`:
  - **Atoms**: `Input`, `Select`, `Checkbox`, `Button`
  - **Molecules**: `FormField`, `StepProgress`, `PresetSelector`, `QuoteCard`
  - **Organisms**: `DesktopTitleBar`, `OnboardingBrandPanel`, `OnboardingSetupForm`
  - **Page**: `components/pages/OnboardingSetupView.svelte`
- **Rationale**: Strictly adheres to the project's established Atomic Design structure per FR-010 while remaining isolated in its own feature module.
- **Alternatives considered**: Flattening the component tree, rejected due to FR-010.

### 4. Local State Management
- **Decision**: Use Svelte 5 runes (`$state`, `$derived`) inside a local model class (`OnboardingSetupState.svelte.ts`) instantiated by the page component and passed down as props. No backend calls are made. "BACK" and "FINISH" emit callbacks. Optional `windowService?: DesktopWindowService` is injected for title-bar window controls.
- **Rationale**: The spec requires keeping all state local and avoiding backend/API changes. Svelte 5 runes provide the cleanest reactive model. Injecting `windowService` keeps Tauri window APIs testable.
- **Alternatives considered**: Global Svelte stores, but they violate the requirement to keep state local to this screen.
