# Data Model: Authentication UI/UX

This feature is presentation-only and does not persist data to a database or interact with a backend service. The data model consists exclusively of local client-side state.

## Presentation State

### AuthenticationState

Manages the active mode, field values, and validation errors for the authentication view.

**Types**:
- `AuthMode = "login" | "register"`

**Fields**:
- `mode`: `AuthMode` (Active authentication mode)
- `email`: `string` (Current value of the email input)
- `password`: `string` (Current value of the password input)
- `confirmPassword`: `string` (Current value of the confirm password input, Register mode only)
- `rememberMe`: `boolean` (State of the "Remember me" checkbox, Login mode only)
- `passwordVisible`: `boolean` (Visibility state for the password field)
- `confirmPasswordVisible`: `boolean` (Visibility state for the confirm password field, stored independently)
- `errors`: `Partial<Record<'email' | 'password' | 'confirmPassword', string>>` (Active validation error messages keyed by field name)
- `hasAttemptedSubmit`: `boolean` (Enables continuous field revalidation only after the active form has first been submitted)

**Optional UI Callbacks**:
- `onSubmitLogin`: `(data: { email, password, rememberMe }) => void` (Safely does nothing when omitted)
- `onSubmitRegister`: `(data: { email, password }) => void` (Safely does nothing when omitted)
- `onModeChange`: `(mode: AuthMode) => void` (Safely does nothing when omitted)
- `onTitleBarAction`: `(action: 'minimize' | 'maximize' | 'close') => void` (Safely does nothing when omitted)

*(Note: No `console.log` defaults are used for these callbacks. They default to safe no-ops.)*

**Validation Rules (Presentation Only)**:
Validation must be implemented as pure, deterministic functions (no API requests).

*For Login*:
- Email: required, must match valid format.
- Password: required, minimum 8 characters.

*For Register*:
- Email: required, must match valid format.
- Password: required, minimum 8 characters.
- Confirm password: required, must match password.

**Validation UX Behavior**:
- Errors should first appear upon form submission, or optionally on blur for earlier feedback.
- After the first submit attempt, an affected field is revalidated on every input and its error clears only when its current value is valid.
- Confirmation is revalidated when either password value changes.
- Values must be preserved after failed validation.
- The UI must use `aria-invalid` to associate inputs with accessible error messages and ensure error announcement.
- Validation must successfully complete before any optional submission callback is invoked.

**Out of Scope Model Items**:
Do not model authenticated users, roles, permissions, tokens, server responses, refresh state, account persistence, or backend error codes.

## Desktop Window Boundary

### DesktopWindowService

Presentation components depend on this small service rather than Tauri classes:

- `openMainWindow()`: resolves the configured `main` handle, unminimizes it when needed, shows it when hidden, and focuses it. Concurrent calls reuse one in-flight promise.
- `minimizeCurrent()`: minimizes the current window.
- `toggleMaximizeCurrent()`: toggles and returns the current maximize state.
- `isCurrentMaximized()`: reads maximize state for the title-bar icon and accessible name.
- `hideCurrent()`: hides `main` so the widget can reopen it.
- `closeCurrent()`: preserves the companion widget's existing close behavior.
- `startDraggingCurrent()`: starts native dragging from a non-control title-bar region.

Every operation returns a resolved no-op when no Tauri runtime/window handle exists. The service never creates windows and contains no authentication or network state.
