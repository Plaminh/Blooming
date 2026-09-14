# Feature Specification: Settings Screen

**Feature Branch**: `[008-settings-screen]`

**Created**: 2026-09-14

**Status**: Draft

**Input**: User description: "Create a new, independent specification for implementing the Blooming Settings screen."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Settings Visual Representation & Navigation (Priority: P1)

Users need to view their settings screen with exact visual fidelity to the provided reference and be able to navigate to it via the sidebar.

**Why this priority**: The core requirement is visual fidelity and placement within the shared app shell. Without a faithful recreation of the UI, no functional settings updates can be performed confidently.

**Independent Test**: Can be fully tested by navigating to the Settings route and verifying the layout matches `design-assets/app/references/settings.png` without needing any backend connectivity.

**Acceptance Scenarios**:

1. **Given** the user is authenticated, **When** they click "Settings" in the shared sidebar, **Then** the Settings route becomes active and the Settings navigation item is visually highlighted.
2. **Given** the user is on the Settings screen, **When** the page renders, **Then** the page layout exactly matches `design-assets/app/references/settings.png` at its native dimensions, including the shared title bar, shared sidebar, and correct proportions of the Account, General, Focus Timer, and Notifications panels.
3. **Given** the user views the Settings screen, **When** inspecting the controls, **Then** they display the exact initial values from the reference: "Mr. Bloom", "Asia/Ho_Chi_Minh", "25 minutes", "5 minutes", "20:00", with "Start Blooming at login", "Keep widget on top", and "Email reminders" toggled on.
4. **Given** the user is on the Settings screen, **When** they inspect the assets, **Then** all icons (Blooming logo, gear, plant, counters, user, clock, bell) render using verified real repository assets without utilizing the reference screenshot at runtime.

---

### User Story 2 - Draft Editing and Validation (Priority: P2)

Users need to edit their preferences in the settings form and receive immediate validation feedback before saving.

**Why this priority**: Users must be able to change settings and see valid vs. invalid states before finalizing them.

**Independent Test**: Can be fully tested by interacting with the inputs, toggles, and dropdowns, observing state updates, and triggering validation errors.

**Acceptance Scenarios**:

1. **Given** the user is editing the Settings form, **When** they modify "Mr. Bloom's name" or toggle a preference, **Then** the draft state is updated and the form is marked as dirty.
2. **Given** the user is modifying "Mr. Bloom's name", **When** they clear the field, **Then** a validation error is displayed indicating the name cannot be empty.
3. **Given** the user modifies multiple fields, **When** they edit one field, **Then** other previously modified unsaved fields retain their draft values.

---

### User Story 3 - Save Changes and Cancel (Priority: P3)

Users need to be able to save their draft changes to persist them, or cancel to revert to the last saved state.

**Why this priority**: State persistence and cancellation complete the primary loop of a settings screen.

**Independent Test**: Can be fully tested by editing fields, clicking Save/Cancel, and observing the state revert or persist in local memory/shared store.

**Acceptance Scenarios**:

1. **Given** the user has unsaved draft changes, **When** they click "CANCEL", **Then** all unsaved changes are discarded, and the form reverts to the last successfully saved values.
2. **Given** the form is valid and dirty, **When** the user clicks "SAVE CHANGES", **Then** the settings are saved (to the existing shared store or local typed state), the dirty state is cleared, and accessible success feedback is shown.
3. **Given** a save is already in progress, **When** the user attempts to save again, **Then** the save action is prevented to avoid duplicates.
4. **Given** the user toggles "Start Blooming at login", **When** Tauri APIs are unavailable, **Then** local UI state updates gracefully and treats platform integration as unfinished.

---

### User Story 4 - Logout (Priority: P4)

Users need a clear way to end their session directly from the Settings screen.

**Why this priority**: Important account action that must trigger the existing application logout flow.

**Independent Test**: Can be tested by clicking Logout and verifying the session is cleared without needing the settings form to be fully implemented.

**Acceptance Scenarios**:

1. **Given** the user clicks "LOGOUT", **When** the existing authentication flow is available, **Then** the session state is cleared and the user is navigated according to the auth route behavior.
2. **Given** the user clicks "LOGOUT", **When** the authentication flow is absent, **Then** an approved local fallback behavior runs.

---

### Edge Cases

- Settings load with no existing saved data (should fall back to defaults matching reference).
- Local settings are partially missing or contain invalid persisted values.
- Rapid toggle changes by the user.
- Multiple fields changed before saving.
- Cancel activated after several edits.
- Repeated Save activation while pending.
- Save fails after platform settings (like Tauri autostart) partially succeed.
- Browser preview where Tauri APIs (autostart, always-on-top) are unavailable.
- Autostart permission or plugin is unavailable.
- Widget window is not currently open when toggling "Keep widget on top".
- User is not authenticated.
- Very long email address or long timezone value causing potential layout overflow.
- Application opened in a smaller supported desktop window.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST render the Settings route with layout, styling, and proportions matching `design-assets/app/references/settings.png`.
- **FR-002**: System MUST integrate the existing shared application shell (sidebar, title bar, pixel font, theme tokens, sprite renderers) without duplication.
- **FR-003**: System MUST implement Settings using Atomic Design component responsibility (Atoms, Molecules, Organisms).
- **FR-004**: System MUST NOT use runtime images, backgrounds, or crops of the reference screenshot. All visual components must use verified repository assets (`/assets/...` or `$lib/...`).
- **FR-005**: System MUST maintain distinct form states: initial, draft, saved, dirty, validation, saving, save-success, and save-error.
- **FR-006**: System MUST allow editing of typed draft state independent of the saved state until submission.
- **FR-007**: System MUST discard draft changes and revert to the saved state when Cancel is activated.
- **FR-008**: System MUST perform full form validation upon Save Changes.
- **FR-009**: System MUST NOT persist data or clear dirty state if validation or the save action fails.
- **FR-010**: System MUST NOT allow a duplicate save operation while a save is pending.
- **FR-011**: System MUST integrate with existing Tauri autostart and window behavior for platform settings, or gracefully fall back in browser previews.
- **FR-012**: System MUST clear session state and route appropriately upon Logout using the existing authentication architecture.
- **FR-013**: System MUST provide keyboard accessibility, visible focus indicators, semantic HTML, and correct label associations for all form controls.
- **FR-014**: System MUST NOT regress visually or functionally on existing screens (Today, Goals, Garden, Onboarding, Widget).

### Key Entities

- **Settings Profile**: The core data entity containing typed user preferences.
  - Email (string, via auth state or local fixture)
  - Mr. Bloom's display name (string)
  - Timezone identifier (string, e.g. IANA timezone `Asia/Ho_Chi_Minh`)
  - Focus duration (number, e.g. `25` minutes)
  - Break duration (number, e.g. `5` minutes)
  - Start at login preference (boolean)
  - Keep widget on top preference (boolean)
  - Milestone reminder time (validated time representation, e.g. "20:00")
  - Email reminders preference (boolean)
- **Form State Model**:
  - `draftSettings`: Currently edited values
  - `savedSettings`: Last successfully persisted values
  - `isDirty`: Derived boolean if draft differs from saved
  - `isSaving`: Boolean indicating an ongoing save request
  - `validationErrors`: Key-value record of current field errors

### State Transitions

- **Initial Load**: Fetch/initialize `savedSettings`. Set `draftSettings` = `savedSettings`.
- **Edit Field**: Update `draftSettings[field]`. Set `isDirty` based on comparison with `savedSettings`.
- **Cancel**: Set `draftSettings` = `savedSettings`. Clear `validationErrors`.
- **Save Changes**: Validate `draftSettings`. Set `isSaving` = true. On success, `savedSettings` = `draftSettings`, `isDirty` = false. On error, set error state. Clear `isSaving`.

### Validation Rules

- **Mr. Bloom's Name**: MUST NOT be empty. MUST NOT be whitespace only. MUST NOT exceed the approved maximum length.
- **Timezone**: MUST be a valid supported timezone identifier.
- **Focus / Break Duration**: MUST be numbers greater than zero. MUST NOT be empty or invalid.
- **Reminder Time**: MUST be a valid time representation.
- **Platform Integrations**: MUST explicitly report failures rather than silently swallowing Tauri API errors.

### Visual Verification Requirements

The implemented feature must be verifiable by:
1. Opening the actual Settings route.
2. Rendering it at the reference image's verified native dimensions.
3. Comparing it against `design-assets/app/references/settings.png`.
4. Correcting macro geometry first, then panel/control dimensions, typography/assets, and finally colors/borders/shadows/spacing.
5. Repeating comparison until defined tolerance is satisfied.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Settings screen layout and styling visually matches `design-assets/app/references/settings.png` to the naked eye at native dimensions.
- **SC-002**: Initial state precisely mirrors the values in the visual reference.
- **SC-003**: Draft edits can be canceled and successfully reverted to the saved state 100% of the time.
- **SC-004**: Form submission correctly validates all fields, rejecting empty names and invalid durations.
- **SC-005**: 100% of form controls are fully operable via keyboard navigation.
- **SC-006**: Existing screens (Today, Goals, Garden, etc.) exhibit zero regressions after Settings implementation.
- **SC-007**: No duplicate shared shell components (sidebar, title bar) are created in the codebase for this screen.
- **SC-008**: All used visual assets map to actual files in the repository; zero runtime image imports of the reference screenshot exist in the build.
- **SC-009**: The UI safely falls back in a standard web browser where Tauri APIs are absent, preventing runtime crashes.

## Assumptions

- Users have basic familiarity with form interactions.
- The repository already contains the required design assets (icons, sprite sheets, font files) at `/assets/...` or `$lib/...`.
- The project already has accessible select/dropdown controls or native equivalents that can be styled to match the reference.
- A timezone dataset is available (via browser `Intl` API or shared source) and does not require building a full custom timezone database.
- A navigation-back convention or standard cancel behavior can fall back to resetting local state if no history exists.

## Dependencies

- Existing shared Svelte components for the application shell (sidebar, title bar).
- Pre-existing verified styling system (theme tokens, pixel fonts, colors).
- Existing asset-loading conventions for sprites and icons.
- Current Tauri bindings and window management APIs.
- Existing authentication architecture (if available) for the logout flow and email display.

## Out of Scope

- Implementing new backend authentication APIs or settings persistence endpoints.
- Email delivery systems.
- Notification scheduling backend logic.
- New Tauri plugins (e.g. installing a new autostart plugin if not approved).
- Account deletion, password changes, or expanded profile editing.
- Settings sections not visible in the reference.
- Any general application redesign outside of this specific screen.
- Mobile layout redesign.
- Modifying behavior of Today, Goals, Garden, or Widget screens.
