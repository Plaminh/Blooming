# Feature Specification: Today Screen

**Feature Branch**: `[User managed]`

**Created**: 2026-09-14

**Status**: Implemented

**Input**: User description: "Create a fresh, independent specification for implementing the Blooming **Today screen**."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - View Today's Schedule (Priority: P1)

Users open the app to see their schedule for the current day displayed as a timeline, so they can understand what they need to do and when.

**Why this priority**: The timeline view is the core value proposition of the Today screen, establishing the main layout and geometry.

**Independent Test**: Can be fully tested by launching the app, verifying the Today sidebar item is active, and confirming the 4 required tasks render at the correct coordinates with their respective states.

**Acceptance Scenarios**:

1. **Given** the user navigates to the Today screen, **When** the screen loads, **Then** the timeline displays the exact four tasks: "Study databases", "Break", "Finish proposal", and "Go for a walk".
2. **Given** the Today screen is visible, **When** checking the sidebar, **Then** "Today" is highlighted as the active destination, and a large plant with leaf/water counters is visible at the bottom.
3. **Given** the Today screen is loaded, **When** the user accesses it via keyboard, **Then** all interactive controls (tasks, sidebar, buttons) must be reachable via `Tab` and actionable with `Enter` or `Space` natively.

---

### User Story 2 - Navigate Dates (Priority: P2)

Users want to view schedules for past and future days, as well as quickly jump back to the current day.

**Why this priority**: Navigating time is a fundamental feature of a calendar/planner.

**Independent Test**: Can be tested by clicking the date navigation controls and verifying the date text updates appropriately.

**Acceptance Scenarios**:

1. **Given** the user is on the Today screen, **When** they click the "Next" button, **Then** the displayed date increments by one day and tasks update or clear.
2. **Given** the user clicks the "Previous" button, **Then** the displayed date decrements by one day.
3. **Given** the user has navigated away from the current date, **When** they click "Today", **Then** the screen resets to the application's reference local "today" value (Apr 23, 2024 for demo purposes).
4. **Given** the user navigates to a day with no scheduled tasks, **When** the timeline loads, **Then** an explicit empty state message is shown without layout errors.

---

### User Story 3 - View Task Details and Next Session (Priority: P1)

Users want to select a specific task on the timeline to see its full details and their next upcoming session in the right rail.

**Why this priority**: The synchronized state between the timeline and the right rail is a critical interaction pattern.

**Independent Test**: Can be tested by clicking different tasks in the timeline and verifying the "Task Details" panel updates to match.

**Acceptance Scenarios**:

1. **Given** the Today screen is loaded, **When** the user selects "Study databases", **Then** the "Task Details" panel derives its category, notes, time, and title from the active task state.
2. **Given** the right rail is visible, **When** viewing the "Next Session" panel, **Then** it accurately reflects the next session's static fallback or derived state.

---

### User Story 4 - Setup Focus Session (Priority: P2)

Users need to prepare for a task by selecting a focus preset and starting a focus session.

**Why this priority**: This connects the schedule to the actual productivity tools (timers).

**Independent Test**: Can be tested by interacting with the Focus Setup panel and verifying exclusive selection of presets.

**Acceptance Scenarios**:

1. **Given** the Focus Setup panel is visible, **When** the user clicks "25/5", "50/10", or "Custom", **Then** exactly one preset becomes visually selected at a time.
2. **Given** a preset and a task are selected, **When** the user clicks "Start Focus", **Then** the frontend dispatches a typed local UI action/state indicating focus has started.
3. **Given** no task is selected, **When** viewing the Start Focus button, **Then** it is disabled or visually indicates it requires a task selection.

---

### User Story 5 - Replan and Edit Actions (Priority: P3)

Users may need to adjust their schedule either manually or with AI assistance (Mr. Bloom).

**Why this priority**: Important for flexibility, but secondary to viewing and starting work.

**Independent Test**: Can be tested by verifying the bottom action buttons trigger existing flows or fire local UI events.

**Acceptance Scenarios**:

1. **Given** the user clicks "Edit Manually", **Then** the app executes a typed local state mutation or placeholder action without calling a non-existent backend endpoint.
2. **Given** the user clicks "Replan with Mr. Bloom", **Then** the app executes a typed placeholder action or local state mutation.

---

### User Story 6 - Tauri Desktop Controls (Priority: P2)

Users expect standard OS window lifecycle actions to function.

**Acceptance Scenarios**:
1. **Given** the shared Tauri title bar is rendered, **When** clicking minimize, maximize, or close, **Then** the appropriate native Tauri window function fires.
2. **Given** the shared title bar, **When** dragging on its empty space, **Then** the window moves without triggering underlying buttons.

### Edge Cases

- App window resizing smaller than 1440x900 triggers horizontal and vertical overflow scrolling rather than strictly clipping required UI.
- Keyboard navigation provides native focus rings on elements instead of inventing custom non-standard focus states.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST match the visual composition, proportions, typography, and assets of `removed reference artwork` at exactly a 1440x900 desktop viewport.
- **FR-002**: System MUST render exactly four schedule cards for the reference date. (No "Lunch" card, no standalone Mr. Bloom message panel).
- **FR-003**: System MUST provide interactive date navigation driving derived local state.
- **FR-004**: System MUST allow selecting a timeline task via mouse or keyboard to synchronize its information into the Task Details panel.
- **FR-005**: System MUST execute a "Start Focus" typed local action when clicked, assuming a task is selected.
- **FR-006**: System MUST reuse the existing `DesktopTitleBar.svelte` to preserve Tauri desktop-shell behavior natively.
- **FR-007**: System MUST use typed local fixture/view-model data.
- **FR-008**: System MUST follow Atomic Design principles for components, properly extracting Date Navigation, Status Badges, and Presets.

### Key Entities

- **Task**: Represents an entry on the timeline. Contains properties for title, time range, status, icon, category, and notes.
- **Focus Preset**: Represents a timer configuration (e.g., 25/5).
- **Date State**: Represents the currently viewed day on the timeline.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Visual comparison of the implemented Today screen at 1440x900 against the provided screenshot shows strict alignment of layout, padding, colors, fonts, and assets.
- **SC-002**: Interactive states (task selection, date navigation, focus preset selection, local feature actions) function natively with keyboard and mouse without throwing console errors.
- **SC-003**: Real sprite rendering (monstera, mr. bloom if used) respects actual sheet frames via the `PlantSprite.svelte` conventions.
- **SC-004**: The feature is strictly frontend-only, introducing zero React/JSX and zero speculative API requests.

## Assumptions

- No new backend APIs are expected; missing data is mocked with typed local variables/view-models.
- 1440x900 is the primary comparison viewport. Smaller screens will use basic scroll bars instead of elaborate responsive grid rearrangements.
- Any Svelte routing navigation in the sidebar will only attempt to navigate to routes that already exist.
