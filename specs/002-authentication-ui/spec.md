# Feature Specification: Authentication UI/UX

**Feature Branch**: `N/A` (No branch created as per requirements)

**Created**: 2026-09-13

**Status**: Implemented; desktop manual acceptance pending

**Input**: User description: "Specify the UI and UX for Blooming’s desktop Authentication screen..."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Viewing and Using Default Login Mode (Priority: P1)

As an existing Blooming user, I want to see a clean login screen so that I can access my account.

**Why this priority**: Login is the default starting state and primary entry point for existing users, making it the highest priority.

**Independent Test**: Can be fully tested by launching the authentication screen, verifying the visual composition matches the 1440x900 baseline, and interacting with the email, password, and submit controls purely in local UI state.

**Acceptance Scenarios**:

1. **Given** the main application window has been opened from the companion widget, **When** `/auth` is rendered, **Then** the layout is a two-column split, with the illustration on the left and the login form on the right, and the active mode is Login.
2. **Given** the login form is active, **When** the user clicks the password visibility toggle, **Then** the password input switches between masked and visible text.
3. **Given** the login form is active, **When** the user types "you@example.com" and a password, **Then** the fields update locally without triggering a backend request.
4. **Given** the user is viewing the login screen, **When** they click the "Remember me" checkbox, **Then** it toggles the checked state visually.

---

### User Story 2 - Switching to and Using Register Mode (Priority: P2)

As a new user, I want to switch to a registration form so that I can create a new Blooming account.

**Why this priority**: Onboarding new users is essential, but secondary to the default login view.

**Independent Test**: Can be tested by clicking the mode switch links and verifying the UI updates to show the registration form fields without reloading the application.

**Acceptance Scenarios**:

1. **Given** the user is in Login mode, **When** they click the "REGISTER" tab or "Create an account" link, **Then** the UI transitions to Register mode, revealing the "Confirm password" field.
2. **Given** the user is in Register mode, **When** they click the "LOGIN" tab or "Login" link, **Then** the UI returns to Login mode.
3. **Given** the user switches between Login and Register modes, **When** they observe the transition, **Then** only one authentication surface is rendered at a time, and any previously entered values are preserved if reasonable.

---

### User Story 3 - Receiving Local Validation Feedback (Priority: P3)

As a user making mistakes on the form, I want to see immediate local validation errors so that I can correct them before submission.

**Why this priority**: Client-side validation improves user experience by catching basic errors early, but the core forms must exist first.

**Independent Test**: Can be tested by intentionally leaving fields blank, entering invalid emails, or mismatched passwords, and observing the presentation-only error states.

**Acceptance Scenarios**:

1. **Given** the login form is empty, **When** the user clicks "LOGIN", **Then** validation errors appear near the required fields and are announced accessibly.
2. **Given** the user types an invalid email format, **When** the field is validated, **Then** an error message indicating invalid email format appears.
3. **Given** the user is in Register mode, **When** they enter a password and a different confirm password, **Then** a "password does not match" error is displayed.
4. **Given** a field currently shows an error, **When** the user corrects the input, **Then** the corresponding error message is cleared.

---

### User Story 4 - Window Chrome and Layout Resizing (Priority: P4)

As a desktop user, I want a custom title bar and a responsive layout so that the app feels like a cohesive desktop experience.

**Why this priority**: Window chrome and responsive behavior are important for the desktop feel but are structural enhancements around the core forms.

**Independent Test**: Can be tested by resizing the browser preview and, in Tauri, interacting with the custom window controls (minimize, maximize/restore, close-to-hide, and drag).

**Acceptance Scenarios**:

1. **Given** the authentication screen is displayed, **When** the window is at the 1440x900 baseline, **Then** no scrollbars appear, and the left illustration is fully visible without distortion.
2. **Given** the authentication screen is displayed, **When** the user resizes the window narrower, **Then** the left illustration crops in a controlled manner, does not stretch, and the right form column remains fully accessible without overlapping.
3. **Given** the authentication screen is displayed in Tauri, **When** the user interacts with the custom title bar, **Then** dragging, minimize, maximize/restore, and close-to-hide affect the existing `main` window; in a browser preview the same actions safely no-op.

---

### User Story 5 - Opening the Main Window from the Widget (Priority: P1)

As a desktop user, I want the companion widget to remain available at startup and open Blooming only when I double-click its non-interactive surface.

**Independent Test**: Launch the Tauri app, verify only the widget is visible, single-click and double-click the widget surface, then repeat after hiding or minimizing `main`.

**Acceptance Scenarios**:

1. **Given** the desktop process starts, **When** no widget open gesture has occurred, **Then** `companion-widget` is visible and the single configured `main` window is hidden.
2. **Given** `main` is hidden, **When** the user genuinely double-clicks the non-interactive widget surface, **Then** `main` is shown and focused at `/auth`.
3. **Given** `main` is minimized, **When** the user double-clicks the widget surface, **Then** the same window is unminimized and focused.
4. **Given** the user single-clicks the widget or double-clicks an interactive widget control, **Then** the main window is not opened.
5. **Given** the first open request is still running, **When** more double-clicks arrive, **Then** they share the in-flight request and do not create or duplicate a window.

### Edge Cases

- What happens when the user resizes the window to extremely narrow widths (mobile size)? (The feature may stack or hide part of the illustration, provided the form remains accessible).
- How does the system handle rapid toggling between Login and Register modes? (Local state should immediately reflect the active mode without rendering duplicates).
- What happens when the user enters an extremely long email address or password? (The input fields should handle overflow gracefully without breaking the layout).

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST render a two-column desktop authentication layout with a custom title bar, left illustration, and right form area.
- **FR-002**: System MUST support a `login` mode and a `register` mode, controlled by local component state, displaying exactly one mode at a time.
- **FR-003**: System MUST display an email input, password input, password visibility toggle, "Remember me" checkbox, and a primary submit button in Login mode.
- **FR-004**: System MUST display an email input, password input, confirm password input, password visibility controls, and a primary submit button in Register mode.
- **FR-005**: System MUST allow users to switch between modes using a segmented selector or bottom links without triggering a page reload.
- **FR-006**: System MUST perform local, presentation-only validation for required fields, email format, minimum password length, and password matching (in Register mode).
- **FR-007**: System MUST associate validation error messages with their corresponding inputs for accessibility and visual proximity.
- **FR-008**: System MUST use `frontend/static/assets/auth/authentication-background.png` for the left illustration, preserving its aspect ratio and pixel-art sharpness.
- **FR-009**: System MUST NOT make real backend requests, access databases, or implement actual authentication logic (JWT, sessions, etc.).
- **FR-010**: System MUST render semantic HTML forms and inputs, ensuring keyboard operability and logical focus order.
- **FR-011**: System MUST NOT use the complete-screen reference image (`removed reference artwork`) at runtime.
- **FR-012**: System MUST implement a `/auth` SvelteKit route for local UI preview and testing.
- **FR-013**: Tauri MUST statically configure exactly one hidden, centered, frameless, opaque, resizable `main` window at `/auth` with a 1440x900 default and approximately 1000x700 minimum.
- **FR-014**: The existing `companion-widget` window MUST remain visible and retain its current interactions while opening or focusing `main` only from a native double-click on its non-interactive surface.
- **FR-015**: A shared typed desktop-window service MUST retrieve existing windows and coalesce concurrent opens; it MUST never construct a duplicate `main` window.
- **FR-016**: The main custom title bar MUST minimize, toggle maximize/restore, hide instead of terminate, and start window dragging through the service; all service operations MUST safely no-op outside Tauri and during SSR.
- **FR-017**: Tauri capabilities MUST be limited to the window inspection and operations required by the widget opener and both custom title bars, for Windows and Linux desktop targets.

### Key Entities

- **Authentication State**: A local, presentation-only state object managing the active mode (`login` or `register`), field values, visibility toggles, and active validation errors.
- **Desktop Window Service**: A typed boundary that resolves the configured current or `main` Tauri window and performs safe window operations without exposing Tauri imports to presentation components.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: All required form fields, buttons, and toggles for both Login and Register modes are fully interactive using only the keyboard.
- **SC-002**: Local validation correctly catches and displays errors for empty fields, invalid emails, and mismatched passwords in 100% of tested scenarios without backend calls.
- **SC-003**: The UI layout matches the 1440x900 baseline design composition, verified by manual visual inspection against the reference image, with no unintended gaps, overlaps, or scrollbars.
- **SC-004**: Switching between Login and Register modes occurs instantaneously (< 100ms) without page reloads or rendering duplicated form elements.
- **SC-005**: The left illustration asset (`authentication-background.png`) remains undistorted during window resizing, utilizing CSS properties to crop rather than stretch.
- **SC-006**: Automated integration tests prove a single click and excluded-control double-click do not open `main`, while one surface double-click requests one open and rapid repeated opens share one in-flight operation.
- **SC-007**: Tauri starts with only the widget visible and can repeatedly hide, reopen, unminimize, and focus the same `main` window, verified manually on the available desktop environment.

## Assumptions

- The target platform is strictly desktop environments; mobile-specific interactions or layouts are out of scope.
- The minimum password length for local validation is assumed to be 8 characters, based on common industry standards, since it wasn't strictly defined.
- Existing shared visual tokens (colors, fonts) established in the Blooming repository will be reused.
- The feature remains frontend-only for authentication: it has no backend authentication or API integration. Tauri window lifecycle integration is in scope.
- Windows and Linux are the supported desktop targets; browser `/auth` remains a safe preview surface.
