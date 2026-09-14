# Feature Specification: Goals Screen

**Feature Branch**: `[006-goals-screen]`

**Created**: 2026-09-14

**Status**: Draft

**Input**: User description: "Blooming Goals Screen — complete SpecKit prompts"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - View Goals Layout and Shared Shell (Priority: P1)

Users see the complete Goals screen layout anchored by the shared application shell (sidebar, title bar) and the three content columns (My Goals, Goal Details, Right Rail) scaled correctly at 1440 × 900.

**Why this priority**: Establishes the macro geometry, ensures shared components (app shell, sidebar, garden) render correctly, and validates that the correct SvelteKit route and window behavior work.

**Independent Test**: Can be fully tested by navigating to the Goals screen and observing the layout, shared title bar, sidebar states, and three columns.

**Acceptance Scenarios**:

1. **Given** the app is running and the viewport is ~1440 × 900, **When** the user navigates to the Goals route, **Then** the screen displays the full desktop application frame, turquoise title bar, and the left sidebar with the active Goals item.
2. **Given** the Goals screen is loaded, **When** the user observes the content area, **Then** there are exactly three content columns (My Goals, Goal Details, Right Rail) matching the reference proportions, with no accidental page scrolling or clipped panels.
3. **Given** the Goals screen is loaded, **When** the user observes the bottom right, **Then** the Your Garden panel is bottom-aligned with intentional whitespace above it, and displays "UNLOCKED PLANTS" "1 / 5".
4. **Given** the application is open, **When** the user clicks the Tauri window controls (minimize, maximize/restore, close) or drags the title bar, **Then** the window behaves correctly according to the shared shell logic.

---

### User Story 2 - View My Goals List (Priority: P2)

Users see a populated list of their goals with titles, descriptions, icons, and status indications, allowing them to browse their objectives.

**Why this priority**: Displays the core entity of the screen. Relies on the initial local view-model data provided.

**Independent Test**: Can be tested by verifying the My Goals list correctly renders the three required local fixtures.

**Acceptance Scenarios**:

1. **Given** the Goals screen is loaded, **When** the user views the "My Goals" panel, **Then** exactly three goals are listed ("Complete Blooming MVP", "Read 12 books", "Stay healthy") with their respective descriptions and icons.
2. **Given** the "My Goals" panel is visible, **When** a goal is selected, **Then** it is visually distinguished from the rest of the list according to the reference design.
3. **Given** the "My Goals" panel is visible, **When** the user views the action buttons, **Then** the primary action "CREATE GOAL WITH MR. BLOOM" is visible and correctly styled.

---

### User Story 3 - Select a Goal and View Details (Priority: P3)

When a user selects a goal from the list, the Goal Details, Roadmap, Next Milestone, and Overall Progress panels automatically synchronize to reflect the selected goal's data.

**Why this priority**: Connects the list selection to the detailed views and progress metrics, ensuring the UI state is properly synchronized.

**Independent Test**: Can be tested by clicking different goals in the My Goals list and observing the content of the other panels update to match the selection.

**Acceptance Scenarios**:

1. **Given** the user selects "Complete Blooming MVP" from the My Goals list, **When** the user views the Goal Details column, **Then** the summary shows the title, description, and Target date "Jun 30, 2024".
2. **Given** the goal "Complete Blooming MVP" is selected, **When** the user views the Roadmap, **Then** exactly four milestones are displayed with correct connector nodes, titles, descriptions, dates, and status badges ("Completed", "In progress", "Not started").
3. **Given** the goal "Complete Blooming MVP" is selected, **When** the user views the Right Rail, **Then** Next Milestone shows "Build planning core" and Overall Progress shows "2 / 4 milestones", "50%".
4. **Given** the goal "Complete Blooming MVP" is selected, **When** the user changes selection to another goal, **Then** the detail panels update to reflect the new selection (if data exists) or clear out appropriately.

---

### User Story 4 - Interact with Goal Actions (Priority: P4)

Users can initiate actions such as creating, editing, and refining goals using the provided buttons, utilizing existing flows or local UI fallback states.

**Why this priority**: Enables user interaction beyond passive viewing, utilizing either existing application flows or establishing functional fallback patterns.

**Independent Test**: Can be tested by clicking the action buttons and verifying focus states, keyboard navigation, and triggering of appropriate local flows or fallback behaviors.

**Acceptance Scenarios**:

1. **Given** the Goals screen is loaded, **When** the user clicks "CREATE GOAL WITH MR. BLOOM", **Then** the existing creation flow is triggered (or an accessible typed local UI action occurs if no flow exists).
2. **Given** a goal is selected, **When** the user clicks "EDIT MANUALLY" or "REFINE WITH MR. BLOOM", **Then** the appropriate existing dialogs/flows open (or an approved local UI behavior triggers).
3. **Given** the user navigates using the keyboard, **When** they Tab through the screen, **Then** focus states are visible and button semantics are correct for all actions.

### Clarifications

### Session 2026-09-14
- Q: What should the fallback UI behavior be for the Create, Edit, and Refine actions if their respective flows do not exist yet? → A: Open a simple accessible placeholder modal/dialog that says "Coming Soon" with a close button.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The screen MUST load at the existing Goals route and render the shared app title bar, sidebar, and three-column layout.
- **FR-002**: The screen MUST display the exact visual structure, colors, spacing, typography, and assets dictated by `design-assets/references/goal.png`.
- **FR-003**: The screen MUST populate the My Goals list using the required local typed fixture data.
- **FR-004**: The system MUST synchronize the Goal Details, Roadmap, Next Milestone, and Overall Progress panels when a goal is selected.
- **FR-005**: The Roadmap MUST correctly render milestone cards, vertical timeline connectors, numbered nodes, dates, and status badges.
- **FR-006**: The right rail MUST display Next Milestone details, Overall Progress explicitly calculating to the reference values (e.g., "2 / 4 milestones", "50%"), action buttons, and the bottom-aligned Your Garden panel.
- **FR-007**: The system MUST support accessible keyboard navigation, focus states, and button semantics for all interactive elements.
- **FR-008**: The screen MUST scale gracefully on smaller desktop sizes while remaining pixel-perfect at 1440 × 900.
- **FR-009**: The system MUST render assets (standalone and sprite sheets) correctly, preserving crisp pixel-art styling.

### Key Entities

- **Goal**: Represents an objective. Contains title, description, target date, assigned icon, and an array of milestones.
- **Milestone**: Represents a step in a goal's roadmap. Contains title, description, date, and status (`Completed`, `In progress`, `Not started`).
- **Progress**: Represents the completion state of a goal. Includes completed milestone count, total milestone count, and explicit completion percentage.
- **Garden State**: Represents the unlocked plants and watering state (e.g., "1 / 5").

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: The Goals screen layout exactly matches the visual composition of `design-assets/references/goal.png` at a 1440 × 900 viewport.
- **SC-002**: Selecting any goal from the list updates the detail panels without visual lag or broken states.
- **SC-003**: All visible decorative assets, icons, and sprites from the reference are rendered without using missing/broken placeholders or generic Unicode substitutes.
- **SC-004**: Implementation introduces zero regressions to the shared Today screen, app shell, or shared theme tokens.
- **SC-005**: All interactive elements (buttons, list items) can be navigated to and activated using only the keyboard.

## Assumptions

- No backend APIs or persistence mechanisms need to be developed; local typed fixture data is sufficient for the MVP.
- Real asset files (images, sprite sheets) are present in the repository; no assets need to be invented.
- The shared SvelteKit/Tauri frontend architecture is already configured with a working CSS/styling pipeline and font-loading strategy.
- Existing dialogs or flows for "Create", "Edit", and "Refine" may not exist yet, so functional typed local UI fallback actions are an acceptable implementation (specifically, a "Coming Soon" accessible placeholder modal).
