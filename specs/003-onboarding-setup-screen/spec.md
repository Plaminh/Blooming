# Feature Specification: onboarding-setup-screen

**Feature Branch**: `[003-onboarding-setup-screen]`

**Created**: 2026-09-13

**Status**: Draft

**Input**: User description: "Create a brand-new, standalone specification named `onboarding-setup-screen`..."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Configure User Profile (Priority: P1)

As a new user, I want to set up my name, timezone, and preferred focus session preset so that the application is customized to my needs and correctly schedules reminders.

**Why this priority**: Essential for the initial onboarding flow to allow users to personalize their experience before using the main application.

**Independent Test**: Can be tested independently by loading the onboarding setup screen, modifying all controls (name, timezone, presets, checkboxes), and verifying that local state updates correctly and that clicking Finish/Back triggers the correct events with the chosen data.

**Acceptance Scenarios**:

1. **Given** the onboarding setup screen is loaded, **When** the user edits the name input, **Then** the local state reflects the new name.
2. **Given** the onboarding setup screen is loaded, **When** the user selects a different focus session preset, **Then** the supporting description for that preset is displayed and exactly one preset is marked active.
3. **Given** the user has configured their preferences, **When** the user clicks "FINISH", **Then** the Finish callback is triggered with the current form state.

---

### User Story 2 - UI Layout & Asset Verification (Priority: P2)

As a user, I want to see a polished, pixel-art themed onboarding screen that perfectly matches the reference design.

**Why this priority**: The visual fidelity and atmosphere of the app are core to the product experience. It must match the design reference precisely.

**Independent Test**: Can be tested visually by running the app and comparing the window layout, colors, typography, spacing, and assets against the provided `design-assets/app/references/onboarding-setup.png`.

**Acceptance Scenarios**:

1. **Given** the app is launched at desktop size, **When** viewing the onboarding screen, **Then** the layout displays a two-column structure with the branding panel on the left and the setup form on the right separated by a thin teal divider.
2. **Given** the left branding panel, **When** it renders, **Then** it must include the specific pixel-art assets (sky, clouds, city, leaves, desk, signs, plant, Mr. Bloom) and the quote card at the bottom.
3. **Given** the setup screen is rendered, **When** examining the controls and typography, **Then** the exact wording, capitalization, and atomic components (Inputs, Selects, Checkboxes, Buttons) match the visual reference perfectly.

### Edge Cases

- What happens when a user clears the "Mr. Bloom's name" input entirely?
- How does the system handle extremely long names in the input?

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST display a compact teal desktop-style title bar containing a leaf icon, "BLOOMING" title, and window controls (minimize, maximize, close).
- **FR-002**: System MUST render a two-column layout with a left illustrated branding panel and a right setup form, divided by a thin teal vertical line.
- **FR-003**: System MUST display the specific branding panel containing the heading, tagline, pixel-art scene, and quote card with exact text from the design reference.
- **FR-004**: System MUST display a four-step progress indicator ("1 WELCOME", "2 TIME", "3 FOCUS", "4 WIDGET") with step 1 visually active in green.
- **FR-005**: System MUST provide an editable text input for "Mr. Bloom's name" with a default value of "Mr. Bloom" and supporting text.
- **FR-006**: System MUST provide a timezone selector with a default value of "Asia/Ho_Chi_Minh" and supporting text.
- **FR-007**: System MUST provide a focus session preset selector with options "25 / 5", "50 / 10", and "CUSTOM", updating the displayed description based on the selection.
- **FR-008**: System MUST provide "Additional options" checkboxes for "Start Blooming at login" and "Keep widget on top" with their respective supporting texts.
- **FR-009**: System MUST provide "BACK" and "FINISH" buttons that emit events/callbacks to the parent onboarding navigation.
- **FR-010**: System MUST build the UI using Atomic Design principles, composing specific Atoms, Molecules, Organisms, and Page level components.
- **FR-011**: System MUST use existing local assets for illustrations, icons, and fonts rather than substituting with CSS drawings or generic icons.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: 100% of visible copy matches the reference specification precisely.
- **SC-002**: Layout and visual composition pass a side-by-side screenshot comparison with the design reference at the intended desktop size.
- **SC-003**: All interactive controls (input, select, checkboxes, preset buttons) correctly update local component state.
- **SC-004**: Code passes strict TypeScript type checking, linting, and formatting rules without errors.
- **SC-005**: Implementation requires 0 new backend APIs or persistence integrations.

## Assumptions

- Surrounding onboarding navigation (parent component) will handle the actual routing or step progression when "BACK" or "FINISH" is clicked.
- `/onboarding-preview` is a development-only visual test route for this screen. It is not a production entry.
- Desktop window dimensions are defined by the Tauri shell configuration or global CSS; this screen adapts to or dictates a standard desktop aspect ratio as shown in the reference.
- Original illustration, character sprite, leaf icon, logo, background, and font assets are already present in the repository.
- Form validation (e.g., empty name) is handled gracefully by UI state, defaulting to reasonable bounds.
