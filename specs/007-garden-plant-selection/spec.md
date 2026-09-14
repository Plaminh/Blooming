# Feature Specification: Garden Plant Selection

**Feature Branch**: `[007-garden-plant-selection]` (Branch creation managed manually by user)

**Created**: 2026-09-14

**Status**: Draft

**Input**: User description: "Create a new, independent specification for implementing the Blooming **Garden Plant Selection screen**, represented by the heading `CHOOSE YOUR PLANT`..."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Plant Selection and Carousel Navigation (Priority: P1)

As a user, I want to view my available plants in a carousel so that I can decide which one to select or unlock.

**Why this priority**: Core functionality needed to view the plants before unlocking or selecting them.

**Independent Test**: Can be tested by navigating left and right through the mocked plant inventory and verifying the displayed plant artwork, name, and description update correctly.

**Acceptance Scenarios**:

1. **Given** the Garden Plant Selection screen is open with Monstera selected, **When** I click the right arrow, **Then** the next plant in the collection is displayed with its correct artwork, name, description, and lock state.
2. **Given** I am at the first plant in the collection, **When** I click the left arrow, **Then** the carousel wraps to the last plant (or the left button is disabled, matching existing repository conventions).
3. **Given** the screen is loaded, **When** I view the top right, **Then** the leaf balance shows `124`.
4. **Given** the screen is loaded, **When** I view the center, **Then** Monstera artwork, title, and description "A bold and beautiful plant with iconic leaves. Brings a sense of calm and adventure to your space." are displayed.

---

### User Story 2 - Unlocking a Plant (Priority: P1)

As a user, I want to unlock a new plant using my collected leaves so that I can grow it in my garden.

**Why this priority**: Unlocking plants is the primary action and purpose of the progression system on this screen.

**Independent Test**: Can be tested by attempting to unlock a locked plant and observing the leaf balance decrease and the unlock status change.

**Acceptance Scenarios**:

1. **Given** I have a balance of `124` leaves and the Monstera plant costs `120` leaves and is locked, **When** I click the UNLOCK button, **Then** my balance decreases to `4` leaves, the plant becomes unlocked, and the unlock button changes to an appropriate selected/unlocked state.
2. **Given** I have a balance of `100` leaves and a plant costs `120` leaves, **When** I try to click UNLOCK, **Then** the action is prevented.
3. **Given** a plant is already unlocked, **When** I view it, **Then** the UNLOCK button is not shown or indicates it's unlocked, and I cannot be charged again.

---

### User Story 3 - Window and Keyboard Controls (Priority: P2)

As a user, I want to navigate the screen using my keyboard and use standard window controls so that the app is accessible and feels native.

**Why this priority**: Accessibility and native desktop feel are critical requirements for the application.

**Independent Test**: Can be tested by navigating the screen using the Tab key and interacting with window controls.

**Acceptance Scenarios**:

1. **Given** the screen is focused, **When** I press the Tab key, **Then** the previous, next, UNLOCK, and window controls show a visible focus state.
2. **Given** I am focused on the UNLOCK button, **When** I press Enter or Space, **Then** the unlock action is triggered.
3. **Given** the application is running in the desktop environment, **When** I click the close, minimize, or restore buttons on the title bar, **Then** the window behaves correctly.

### Edge Cases

- **Empty plant collection**: Show an empty state or fallback, though ideally there is at least one default plant.
- **Only one available plant**: The previous/next controls should be disabled or hidden.
- **Missing selected plant**: Fallback to a default plant or show an error state without crashing.
- **Insufficient leaf balance**: The UNLOCK button should be visually disabled or prevent the action and show a subtle indication.
- **Exact leaf balance equal to the unlock price**: The UNLOCK action should succeed, leaving the balance at 0.
- **Plant already unlocked**: Hide the UNLOCK button, prevent repeated charges, and show "Selected" or "Unlocked" state.
- **Repeated Unlock activation**: Rapid clicking should not deduct the cost multiple times (prevent double charging).
- **Rapid previous/next navigation**: The UI should update synchronously without race conditions in the local view-model.
- **Missing or invalid plant artwork**: Fallback to a placeholder safely without breaking the layout.
- **Keyboard-only navigation**: Ensure focus traps and order are logical.
- **Smaller supported desktop window sizes**: Graceful scaling without clipping the layout or introducing scrollbars if possible.
- **Running in a normal browser**: Tauri window APIs (minimize/close) should gracefully degrade or hide if unavailable.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST display the shared turquoise Blooming title bar with leaf logo, application name, and minimize/maximize/close controls.
- **FR-002**: System MUST display the user's current leaf balance in the top-right corner.
- **FR-003**: System MUST display the heading `CHOOSE YOUR PLANT` and subtitle `Pick a companion to grow with you.`.
- **FR-004**: System MUST render the central plant artwork with a shadow, preserving aspect ratio and crisp pixel art.
- **FR-005**: System MUST display the plant name and description.
- **FR-006**: System MUST provide previous and next plant controls for carousel navigation.
- **FR-007**: System MUST provide a large green UNLOCK button with a lock icon, unlock cost, and leaf icon for locked plants.
- **FR-008**: System MUST deduct the unlock cost exactly once from the local mock balance upon a successful unlock.
- **FR-009**: System MUST prevent unlocking if the leaf balance is insufficient.
- **FR-010**: System MUST enforce an asset inventory ensuring all visual elements map to real repository assets (e.g., using `/assets/...` or `$lib`) or correctly rendered sprite frames, without placeholders.
- **FR-011**: System MUST be built following Atomic Design principles, defining clear Atoms, Molecules, and Organisms.
- **FR-012**: System MUST scale gracefully at smaller supported desktop sizes without clipping or scrolling, keeping the entire frame visible.

### Out of Scope

- Implementing unrelated garden management, watering, growth simulation, or achievements.
- Implementing real inventory APIs, payment systems, or backend persistence.
- Adding the Today/Goals sidebar.
- Duplicating the shared application theme or title bar inside the Garden feature.
- Speculative backend contracts.
- Mobile redesign.

### Key Entities

- **Plant**: Contains id, name, description, artwork asset path/sprite data, unlock cost, and unlocked status.
- **UserSession**: Contains the current leaf balance.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Visual fidelity matches `design-assets/references/garden.png` at its native viewport (~1271 × 1062) accurately.
- **SC-002**: Screen initializes with Monstera selected, `124` balance, and `120` unlock cost.
- **SC-003**: Carousel navigation synchronizes the plant artwork, text, and unlock state without errors.
- **SC-004**: Local unlock behavior correctly deducts the cost exactly once and prevents double charging.
- **SC-005**: Zero broken or placeholder assets; all visuals are mapped to existing repository files.
- **SC-006**: All interactive controls are accessible and support keyboard navigation.
- **SC-007**: No regressions to the shared title bar, Today screen, Goals screen, or the existing Garden preview panel.

## Assumptions

- Target environment uses SvelteKit, TypeScript, and Tauri.
- The shared Svelte components, theme tokens, and pixel fonts exist in the repository and can be reused.
- Plant inventory and local leaf balance can be modeled via typed local fixture/view-model data.
- The application architecture supports route-specific sizing or scaling techniques for desktop window limits.
- Asset loading follows existing conventions (`/assets/` for static, `$lib` for source tree).
