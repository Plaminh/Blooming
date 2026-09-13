# Implementation Tasks: Authentication UI/UX

**Feature Directory**: `specs/002-authentication-ui`

**Goal**: Implement the local, presentation-only desktop Authentication UI for Login and Register modes.

---

## Phase 1: Asset validation and feature setup

- [x] T001 [P] Verify `design-assets/app/references/authentication-login.png` exists and is preserved as a source-only reference (ensure it is never copied to `frontend/static`).
- [x] T002 [P] Verify `frontend/static/assets/authentication/backgrounds/authentication-background.png` exists (or create/place it) with 686x825 dimensions, preserving its RGBA transparency, aspect ratio, and crisp pixel rendering. Ensure no duplicate Mr. Bloom sprite is baked or layered over it.
- [x] T003 [P] Verify the existing leaf asset at `design-assets/widget/icons/leaf-icon.png` is available for reuse without duplication.
- [x] T004 Create base directory structure `frontend/src/lib/features/authentication/` with `components/atoms`, `components/molecules`, `components/organisms`, `fixtures`, `model`, `styles`, and `types`.

---

## Phase 2: Foundational presentation types, local state and validation helpers

- [x] T005 [P] Create `frontend/src/lib/features/authentication/types/index.ts` defining `AuthMode` and callback types.
- [x] T006 [P] Create `frontend/src/lib/features/authentication/model/validationHelpers.ts` with pure deterministic validation logic (required email, email format, required password, minimum 8 characters, confirmation required, password mismatch).
- [x] T007 Create `frontend/src/lib/features/authentication/model/AuthState.svelte.ts` to manage `mode`, field values, password visibility toggles, validation rules, and error states. Ensure it preserves values during mode switching and handles clear-on-correct.

---

## Phase 3: Shared authentication visual tokens and primitive components

- [x] T008 [P] Create `frontend/src/lib/features/authentication/styles/theme.css` with scoped CSS containing visual tokens (dark teal/navy outlines, warm cream surfaces, muted blue text, green primary actions) mapped to existing Blooming variables where appropriate.
- [x] T009 [P] Create semantic SVG functional icons in `frontend/src/lib/features/authentication/components/atoms/AuthenticationIcon.svelte` (email, lock, checkmark, minimize, maximize/restore, close).
- [x] T010 [P] Create `frontend/src/lib/features/authentication/components/atoms/PasswordVisibilityButton.svelte` implementing show/hide icons and toggle behavior.
- [x] T011 [P] Create `frontend/src/lib/features/authentication/components/atoms/AuthenticationCheckbox.svelte` for accessible checkbox keyboard behavior.
- [x] T012 [P] Create `frontend/src/lib/features/authentication/components/atoms/SegmentedTabButton.svelte` with correct segmented-selector semantics.
- [x] T013 Create visual title bar and semantic controls as `frontend/src/lib/features/authentication/components/molecules/AuthenticationTitleBar.svelte`, routed through the typed desktop-window service with browser-safe no-op behavior.

---

## Phase 4: Login UI user story

- [x] T014 [US1] Create `frontend/src/lib/features/authentication/components/organisms/LoginForm.svelte` with semantic `<form>`, labels, inputs, and primary `LOGIN` button.
- [x] T015 [US1] Integrate `AuthenticationField` (Email) with placeholder `you@example.com` and email icon.
- [x] T016 [US1] Integrate `PasswordField` with placeholder `Your password` and lock icon.
- [x] T017 [US1] Implement semantic form submission, invoking the optional `onSubmitLogin` callback only after valid local input.
- [x] T018 [US1] Add bottom prompt `Don't have an account?` and `Create an account` mode-switch control.

---

## Phase 5: Register UI user story

- [x] T019 [US2] Create `frontend/src/lib/features/authentication/components/organisms/RegistrationForm.svelte` with semantic `<form>`, active `REGISTER` tab, and primary `REGISTER` button.
- [x] T020 [US2] Integrate Email, Password, and Confirm Password fields. Ensure no fields for name, username, social login, subscription, or onboarding exist.
- [x] T021 [US2] Implement semantic form submission, invoking the optional `onSubmitRegister` callback only after valid local input.
- [x] T022 [US2] Add bottom prompt `Already have an account?` and `Login` mode-switch control.

---

## Phase 6: Local validation and correction UX

- [x] T023 [US3] Create `frontend/src/lib/features/authentication/components/molecules/ValidationMessage.svelte` for accessible error announcements (`aria-errormessage`).
- [x] T024 [US3] Wire up `LoginForm.svelte` to `AuthState` to conditionally display Email and Password local validation errors, associating them via `aria-invalid`.
- [x] T025 [US3] Wire up `RegistrationForm.svelte` to `AuthState` to display Email, Password, and Confirm Password validation errors (including password mismatch).
- [x] T026 [US3] After submission, revalidate affected fields on input, keep errors while invalid, revalidate confirmation from either password, and preserve entered values after failure.

---

## Phase 7: Password visibility and Remember-me interactions

- [x] T027 [US1] Integrate `AuthenticationCheckbox.svelte` into `LoginForm.svelte` as the "Remember me" toggle and wire to `AuthState`.
- [x] T028 [US1] Wire `PasswordVisibilityButton.svelte` to the Login password field to toggle masked/visible characters.
- [x] T029 [US2] Wire independent `PasswordVisibilityButton.svelte` instances to the Register password and confirm-password fields.

---

## Phase 8: `/auth` route integration

- [x] T030 Create `frontend/src/lib/features/authentication/components/organisms/AuthenticationPanel.svelte` to conditionally render `LoginForm` or `RegistrationForm` based on `AuthState` mode, without duplication.
- [x] T031 Create `frontend/src/lib/features/authentication/AuthenticationView.svelte` combining `AuthenticationTitleBar`, the left illustration (with HTML marketing copy), and the right `AuthenticationPanel`.
- [x] T032 Create `frontend/src/routes/auth/+page.svelte` to render `<AuthenticationView>` without real authentication or API connections.

---

## Phase 9: Accessibility and automated tests

- [x] T033 [P] [US1] Write automated test in `frontend/src/lib/features/authentication/AuthenticationView.test.ts` for default Login rendering, mode-specific fields, and exactly one Authentication surface.
- [x] T034 [P] [US1] Write automated tests for Remember-me toggling, semantic labels, missing callback safety, and keyboard behavior.
- [x] T035 [P] [US2] Write automated tests for mode switching, Register fields, and callback invocation (only after valid local input).
- [x] T036 [P] [US3] Write automated tests for Login/Register validation rules, password mismatch, error correction, accessible error relationships (`aria-invalid`), and independent password visibility toggling.
- [x] T037 [P] Run `axe-core` programmatic checks on representative fixtures for accessibility violations.
- [x] T038 [P] Assert absence of source-only reference URL and API/network requests in test fixtures. Assert presence of correct clean background asset without duplicate Mr. Bloom.

---

## Phase 10: Responsive styling and manual visual acceptance

- [x] T039 [US4] Implement Grid/Flexbox layout in `AuthenticationView.svelte` at 1440x900 baseline, ensuring form width is ~600px and two-column alignment is clean without absolute coords.
- [x] T040 [US4] Implement `object-fit: cover` controlled cropping for the background illustration and prevent any whole-screen `transform: scale()`.
- [ ] T041 [US4] [MANUAL] Verify baseline 1440x900 composition, title-bar, leaf, brand, controls, and HTML marketing copy placement.
- [ ] T042 [US4] [MANUAL] Verify comparison with source-only reference, heading/subtitle positioning, segmented control, label/input/toggle/submit alignment, and real-browser contrast.
- [ ] T043 [US4] [MANUAL] Verify usable moderate resizing, no clipping or unexpected scrollbars, and sharp illustration pixel rendering.
- [ ] T044 [US4] [MANUAL] Inspect browser network tab to ensure forbidden source-only reference image is not loaded at runtime.

---

## Phase 11: Final quality gates and documentation synchronization

- [x] T045 Run `npm run check` in `frontend/` and fix any TypeScript or Svelte errors.
- [x] T046 Run `npm run test` in `frontend/` and ensure all feature tests pass.
- [x] T047 Run `npm run build` in `frontend/` and fix any build failures.

---

## Phase 12: Desktop window integration

- [x] T048 Add one static hidden `main` window at `/auth` (1440x900, 1000x700 minimum, centered, resizable, opaque, frameless) while preserving the visible `companion-widget` window.
- [x] T049 Add a typed SSR/browser-safe desktop-window service that retrieves existing handles, shows/unminimizes/focuses `main`, controls the current window, and coalesces in-flight open requests.
- [x] T050 Add native `dblclick` opening to the non-interactive widget surface; exclude single clicks and interactive controls without changing existing widget actions.
- [x] T051 Wire the Authentication title bar to native drag, minimize, maximize/restore state, and close-to-hide behavior; keep widget close behavior unchanged.
- [x] T052 Grant only the required window inspection/control capabilities to `companion-widget` and `main`.

---

## Phase 13: Desktop integration tests and acceptance

- [x] T053 Test widget single click, genuine double click, and excluded interactive controls with a mocked window service.
- [x] T054 Test hidden/minimized main paths, focus, rapid in-flight coalescing, and browser-safe no-op behavior with a mocked resolver.
- [x] T055 Test Authentication title-bar service calls and retained optional callbacks.
- [x] T056 Run `cargo check` for the Tauri configuration and Rust application.
- [ ] T057 [MANUAL] Launch Tauri and verify widget-only startup, single/double-click behavior, same-window reuse, minimized/hidden reopening, `/auth`, and all main title-bar controls on Windows.
- [ ] T058 [MANUAL] Verify equivalent runtime behavior on Linux; leave open when no Linux environment is available.

---

## Dependencies & Execution Order

- **Phase 1** must be verified before proceeding to ensure assets are correct.
- **Phase 2 & 3** build the foundational types, state logic, and visual tokens required by the forms.
- **Phase 4 & 5** (Login/Register Forms) can be worked on sequentially or in parallel by different developers once atoms/state exist.
- **Phase 6 & 7** refine the forms with complex validation and interaction behavior.
- **Phase 8** integrates everything into the routable view.
- **Phase 9** (Automated Tests) verifies behavior.
- **Phase 10** finalizes CSS responsive layout and manual visual checks.
- **Phase 11** enforces CI/CD readiness.

## Implementation Strategy
- **MVP Boundary**: Completing Phase 4 and integrating it into Phase 8 delivers a functioning local Login preview. Register mode (Phase 5) is the subsequent increment.
