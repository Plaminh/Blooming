# Implementation Plan: Authentication UI/UX

**Branch**: `N/A` | **Date**: 2026-09-13 | **Spec**: [specs/002-authentication-ui/spec.md](spec.md)

**Input**: Feature specification from `/specs/002-authentication-ui/spec.md`

**Note**: This template is filled in by the `/speckit-plan` command.

## Summary

This feature implements Blooming's desktop Authentication screen and integrates it as one hidden Tauri `main` window opened only by a genuine companion-widget double-click. Svelte 5 local state provides Login/Register UX and deterministic validation; CSS Grid/Flexbox provides a responsive 1440x900 baseline. A shared typed window service owns SSR-safe Tauri calls and in-flight deduplication. The source-only screenshot remains strictly excluded from runtime.

## Technical Context

**Language/Version**: TypeScript, Svelte 5, CSS

**Primary Dependencies**: SvelteKit, Vite

**Storage**: N/A (Presentation only)

**Testing**: Vitest, Testing Library, jsdom, axe-core

**Target Platform**: Desktop (Windows/Linux) via Tauri 2, plus browser-safe `/auth` preview

**Project Type**: Desktop app UI feature

**Performance Goals**: Instantaneous mode switching (< 100ms) without page reload.

**Constraints**: Maintainable layout primitives (CSS Grid/Flexbox). Baseline 1440x900 coordinate system. Use system fonts (no `next/font` or external libraries). No Tailwind or external UI kits.

**Scale/Scope**: 1 hidden main window, 1 preserved visible widget window, and 1 authentication screen with 2 local modes. Authentication remains backend-free.

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- [x] Does the plan align with the Spec-driven development workflow?
- [x] Does the plan preserve the approved Tauri 2/Rust, SvelteKit/TypeScript/Vite, FastAPI/Python/Pydantic, and PostgreSQL/SQLAlchemy boundaries?
- [x] Does deterministic application code remain authoritative while AI output and external input are validated at trust boundaries?
- [x] Are explicit contracts and type safety boundaries defined?
- [x] Is the proposed implementation the simplest that satisfies the spec?
- [x] Are testable behavior and quality gates defined?
- [x] Does the UX handle loading, partial, and failure states gracefully? (Validation states are handled).
- [x] Are resource efficiency and platform scope strictly followed? (Desktop only, UI only).
- [x] Are security and privacy principles respected? (No real API calls).

## Project Structure

### Documentation (this feature)

```text
specs/002-authentication-ui/
├── plan.md              # This file
├── research.md          # Phase 0 output
├── data-model.md        # Phase 1 output
├── quickstart.md        # Phase 1 output
└── tasks.md             # Phase 2 output (pending)
```

### Source Code (repository root)

```text
frontend/
├── src/
│   ├── lib/
│   │   └── features/
│   │       └── authentication/
│   │           ├── components/
│   │           │   ├── atoms/
│   │           │   │   ├── AuthenticationIcon.svelte
│   │           │   │   ├── PasswordVisibilityButton.svelte
│   │           │   │   ├── AuthenticationCheckbox.svelte
│   │           │   │   └── SegmentedTabButton.svelte
│   │           │   ├── molecules/
│   │           │   │   ├── AuthenticationField.svelte
│   │           │   │   ├── AuthenticationModeSelector.svelte
│   │           │   │   ├── PasswordField.svelte
│   │           │   │   └── ValidationMessage.svelte
│   │           │   └── organisms/
│   │           │       ├── LoginForm.svelte
│   │           │       ├── RegistrationForm.svelte
│   │           │       ├── AuthenticationPanel.svelte
│   │           │       └── AuthenticationView.svelte
│   │           ├── fixtures/
│   │           ├── model/
│   │           │   └── AuthState.svelte.ts
│   │           ├── styles/
│   │           │   └── theme.css
│   │           ├── types/
│   │           │   └── index.ts
│   │           ├── AuthenticationView.test.ts
│   │           └── index.ts
│   └── routes/
│       └── auth/
│           └── +page.svelte
└── static/
    └── assets/
        └── authentication/
            └── backgrounds/
                └── authentication-background.png
```

**Structure Decision**: A feature-scoped directory structure under `frontend/src/lib/features/authentication/`. Do not create an atom merely to wrap a single element without reusable behavior or styling. Avoid speculative abstractions and avoid creating a separate component for every decorative pixel.

## Architecture and Design Decisions

### Route Boundary
The primary preview route is `frontend/src/routes/auth/+page.svelte`.
- Render one Authentication view.
- Initialize local fixture/presentation data.
- Support switching between Login and Register.
- Remain completely backend-free.
- Avoid importing the source-only screenshot.
- Preserve `/widget` and `/widget-preview`; add only the double-click opener to the production widget surface and keep existing interactions intact.
- `+page.ts` should only be added if required by the existing SvelteKit static/prerender architecture. `/auth-preview` should not be added unless it provides a concrete testing benefit that `/auth` cannot.

### Source-Only Reference
The full Authentication Login screenshot is verified at `removed reference artwork`.
**Rules**:
- It must serve as source-only visual comparison material.
- Never imported by application source or copied into `frontend/static`.
- Never requested/served at runtime, nor used as a flattened screen background.
**Checks**: The plan requires automated source-reference exclusion checks and manual runtime network verification.

### Decorative Assets and Functional Icons
- **Decorative Leaf**: Reuse the existing `removed reference artwork` for title-bar branding and the decorative leaf above the heading. Do not create duplicate files.
- **Icons**: Plan small semantic SVG components inline (or as small reusable atoms) for: email, lock, show password, hide password, checkmark, minimize, maximize/restore, close. Do not use a generic icon library and do not crop icons from the screenshot.

### Layout Strategy
- **Baseline**: 1440x900 using CSS Grid or Flexbox. Avoid reproducing absolute coordinates literally.
- **Structure**: A custom title bar at the top, and a two-column split below (left illustration, right form area).
- **Form Area**: Warm cream CSS background. Centered in a constrained column of ~600px.
- **Responsiveness**:
  - Normal desktop: two-column layout.
  - Moderate resizing: preserve readable form width; allow controlled illustration cropping.
  - Narrow browser preview: the illustration may shrink, crop, stack, or become partially hidden, but the complete form must remain available.
  - Mobile application UX is out of scope.
  - Do not use whole-screen `transform: scale(...)`. The form must reflow naturally.
- **CSS Strategy**:
  - Distinguish between: stable shared visual tokens (colors, fonts), responsive structural layout (grid/flex), local component spacing (padding/margin), and decorative positioning (absolute).

### Typography and Styling
- **Fonts**: Use repository-compatible local/system fonts. Do not use `next/font` or runtime Google Font downloads.
- **Excluded styling**: No Tailwind, external UI kits, glassmorphism, unrelated gradients, generic dashboard styling, excessive shadows, or emojis.
- **Visual Language**: Enforce dark teal/navy outlines, teal title bar, warm cream surfaces, muted blue text, green primary actions, restrained radii, subtle borders, crisp pixel-art illustration, and calm desktop composition.
- **CSS Scoping**: Authentication-specific CSS tokens should live in a scoped feature stylesheet (`authentication/styles/theme.css`). They should relate to existing Blooming visual values via standard CSS variables but without coupling to widget-private CSS.

### Mode Switching & Behavior
- Switching modes must preserve entered values (e.g., email) if appropriate.
- Keyboard operation must be fully supported (tabs, fields, checkboxes, toggles, links, submit, window controls).
- Local validation must successfully pass before invoking any optional callback.
- No API requests will be made at any point.

### Login UX Specifics
The default Login mode must contain:
- Active `LOGIN` tab and inactive `REGISTER` tab.
- Email label, input, and icon with placeholder `you@example.com`.
- Password label, input, and lock icon with placeholder `Your password`.
- Show/hide password control.
- Remember-me checkbox.
- Primary `LOGIN` button.
- Bottom prompt: `Don't have an account?`
- Bottom mode-switch control: `Create an account`.
- Semantic form submission must be defined (using `<form>` and on:submit handlers) rather than standalone buttons outside a form context.

### Register UX Specifics
The Register mode must contain:
- Inactive `LOGIN` tab and active `REGISTER` tab.
- Email field.
- Password field.
- Confirm password field.
- Password visibility controls.
- Primary `REGISTER` button.
- Bottom prompt: `Already have an account?`
- Bottom mode-switch control: `Login`.
**Excluded Elements**: Do not add fields for name, username, social login, subscription plan, onboarding preferences, or terms/legal checkbox (unless the spec explicitly requires it).

### Validation Design
Validation is implemented as pure, deterministic functions (helpers) evaluating the following rules, which can later be replaced or aligned with backend rules:
- **Login**: Email required, valid email format. Password required, minimum 8 characters.
- **Register**: Email required, valid email format. Password required, minimum 8 characters. Confirmation required, must match password.
*(Note: The eight-character UI rule is a local presentation requirement and is not claimed to be a final security policy for the future backend.)*
**Validation Behavior**:
- Errors should first appear upon form submission, or optionally on blur for earlier feedback.
- Errors must clear immediately after the user corrects the input.
- Values must be strictly preserved after failed validation.
- Inputs must be associatively linked to error messages using `aria-invalid` and `aria-errormessage` (or `aria-describedby`) for accessible error announcement.

### Tauri Window Architecture and Chrome
Declare windows statically in `frontend/src-tauri/tauri.conf.json`; never construct `main` from the frontend.

- `companion-widget` stays visible with its existing `/widget` route and behavior.
- `main` uses label `main`, URL `/auth`, title `Blooming`, default 1440x900 size, 1000x700 minimum, centered/resizable/opaque/frameless configuration, and `visible: false` at startup.
- `frontend/src/lib/platform/desktopWindow.ts` is the only Tauri API boundary. It dynamically imports the window API only in Tauri, resolves the existing window by label, and safely no-ops in browser preview or SSR.
- A native `dblclick` listener on the non-interactive widget surface opens `main`; single clicks and interactive controls are excluded. One in-flight promise coalesces rapid repeated calls.
- Opening checks minimized/visible state, unminimizes or shows when required, then focuses the existing window.
- Main title-bar buttons minimize, toggle maximize/restore, and hide (not terminate). Its non-control region starts native dragging. The displayed maximize/restore state is queried through the adapter.
- The existing widget close operation remains close, so its previous behavior is preserved.
- Capabilities are restricted to retrieving, inspecting, showing, unminimizing, focusing, minimizing, maximizing/restoring, hiding/closing, and starting drag operations for the two configured labels.

### Accessibility Plan
Define implementation and automated test coverage (where possible) for:
- Semantic form, labels, inputs, and buttons.
- Input types (`type="email"` and appropriate password input types).
- Accessible names for password visibility toggles and window controls.
- Correct segmented-selector semantics (e.g., using proper ARIA roles for tabs).
- Keyboard switching between Login and Register.
- Logical focus order and visible focus states.
- Checkbox keyboard behavior.
- Associated error messages and error announcements.
- Decorative background exclusion from the accessibility tree.
- Sufficient contrast and no information conveyed through color alone.
- Reduced-motion behavior if transitions are used.

### Testing Plan
Use only the test tooling already present in the repository. Do not introduce new test tools (e.g., Playwright, Storybook, or a second test runner) unless a concrete missing capability is identified through repository evidence. Manual visual comparison remains appropriate for layout.
- **Test Stack**: Vitest (v5), `@testing-library/svelte` (v5), jsdom (v29), and axe-core (v4).
- **Automated Coverage**: The plan must include automated tests for:
  - Default Login rendering.
  - Login/Register mode switching.
  - Both bottom mode-switch controls.
  - Mode-specific fields (ensuring the correct fields appear/disappear).
  - Semantic labels.
  - Password visibility toggling.
  - Independently controlled password fields where applicable (e.g., standard password vs. confirm password).
  - Remember-me toggle.
  - Login validation and Register validation.
  - Password mismatch error handling.
  - Correction of invalid values (clearing errors upon valid input).
  - Callback invocation only after valid local input.
  - Missing callback safety (safely no-oping when omitted).
  - Keyboard operation across the entire view.
  - Accessible field-error relationships (`aria-invalid` and `aria-errormessage`).
  - axe-core violations for the main fixtures.
  - Ensuring only one Authentication view (Login or Register) is rendered at a time.
  - Runtime use of the clean authentication illustration (`authentication-background.png`).
  - Absence of source-only reference URLs in the runtime.
  - Complete absence of network/API invocations.
  - Main title-bar window-service calls and maximize/restore state.
  - Widget single-click and excluded-control behavior versus native double-click opening.
  - Hidden and minimized main-window paths, browser no-op behavior, and in-flight open coalescing with a mocked resolver/service.

### Required Fixtures or Preview Scenarios
Plan deterministic fixtures or controlled scenarios for:
1. Default Login
2. Login with password visible
3. Login validation errors
4. Login with Remember me selected
5. Default Register
6. Register with password visible
7. Register validation errors
8. Register password mismatch
*(Note: Do not build eight duplicated Authentication components. Use one shared view driven by local state, props, or fixture initialization.)*

### Manual Visual Acceptance Plan
Create a repeatable browser-preview procedure at the baseline design size (1440x900) to verify:
- Overall 1440 × 900 composition.
- Title-bar height and alignment.
- Title-bar leaf, brand, and controls.
- Two-column split.
- Correct authentication background asset usage.
- Sharp pixel rendering.
- No duplicated Mr. Bloom in the illustration.
- Real HTML marketing copy overlaying the left illustration.
- Right-panel form width (constrained to ~600px).
- Heading and subtitle positioning.
- Segmented Login/Register control appearance.
- Label and input alignment.
- Password toggle alignment.
- Remember-me checkbox alignment.
- Submit-button dimensions and color.
- Lower separator, prompt, and mode-switch link appearance.
- No clipping, overlap, distortion, or unexpected scrolling.
- Usable moderate resizing.
- No runtime request for the source-only reference image.
- **Manual Acceptance**: Do not claim that jsdom or axe-core proves real-browser color contrast or pixel-perfect layout. Visual alignment (1440x900 baseline, no scrollbars, cleanly cropped illustrations) and true color contrast checks must be performed via manual visual acceptance in a real browser environment.
*(Note: Screenshots created for manual comparison should remain outside the repository unless the specification explicitly defines a source-only QA evidence policy.)*

For desktop acceptance, launch the normal Tauri development command and verify widget-only startup; single versus double click; same-window focus; hidden/minimized reopening; title-bar drag/minimize/maximize/restore/hide; and `/auth` routing. Record Windows results honestly and leave Linux unverified when the current environment cannot exercise it.

### Documentation Consistency
The plan and related artifacts must consistently state and adhere to the following constraints:
- Frontend authentication UI/UX plus Tauri window integration
- `/auth` browser preview
- No real authentication
- No API interactions
- No global store
- One statically configured hidden `main` window; no runtime window construction
- Companion widget preserved except for its non-interactive-surface double-click opener and shared window-service adoption
- Clean illustration (`authentication-background.png`) is the sole runtime asset
- Complete screenshot is source-only
- Register uses only email, password, and confirm password
- Password minimum is a provisional local validation rule
- Optional callbacks safely no-op without console logging

*(Note: Do not leave contradictions between `plan.md`, `research.md`, `data-model.md`, `quickstart.md`, and the UI contract.)*

## Planning Quality Gates
Before finishing:
1. Confirm the plan complies with the project constitution.
2. Confirm all technical unknowns are resolved from the repository or explicitly documented.
3. Confirm no backend scope or runtime window construction was introduced.
4. Confirm asset paths and roles are unambiguous.
5. Confirm the proposed component structure is proportional to the feature.
6. Confirm tests map directly to specification acceptance criteria.
7. Confirm manual checks are not falsely marked completed.
8. Confirm desktop and browser-safe window behavior is represented consistently across all feature artifacts.
9. Confirm automated and manual verification results are not conflated.
10. Confirm no branch, commit, or push operation occurred.

## Complexity Tracking

*No violations.*
