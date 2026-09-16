# Feature Specification: Frontend Architecture Cleanup and UI Consistency

**Feature Branch**: `011-frontend-architecture-cleanup`

**Created**: 2026-09-16

**Status**: Draft

**Input**: User description: "Create a new feature specification named **Frontend Architecture Cleanup and UI Consistency**."

## User Scenarios & Testing

### User Story 1 - App Navigation and Shell Persistence (Priority: P1)

As a user, I can navigate between main application pages (Today, Goals, Mr. Bloom, Statistics, Settings) without the sidebar or overall application shell remounting or flashing.

**Why this priority**: Core architectural cleanup requirement that impacts performance and visual stability.

**Independent Test**: Can be tested by navigating across all main app routes to verify the DesktopAppShell and AppSidebar stay mounted.

**Acceptance Scenarios**:

1. **Given** I am on the Today page, **When** I click the Goals page in the sidebar, **Then** the page transitions without destroying and recreating the sidebar.
2. **Given** I navigate between main app pages, **Then** the URL updates and navigation history is preserved correctly.
3. **Given** I open a standalone route like Authentication or Onboarding, **Then** the main app shell is not rendered.

---

### User Story 2 - Garden Panel Stability (Priority: P1)

As a user, I see the Garden panel on both Today and Goals screens, and it persists seamlessly between them without visual glitches.

**Why this priority**: Visual defect with bright strips/stretching ruins the UI; unnecessary remounts hurt performance.

**Independent Test**: Can be tested by navigating between Today and Goals and checking the Garden panel visually.

**Acceptance Scenarios**:

1. **Given** I navigate from Today to Goals, **When** the page transitions, **Then** the shared Garden panel is not unnecessarily remounted or reset.
2. **Given** I view the Garden panel, **Then** there is no visible bright strip, incorrect exposure, distorted image, or invalid crop.
3. **Given** I am on a route that should not display the Garden panel, **Then** the Garden panel is not forced onto the screen.

---

### User Story 3 - Visual and Thematic Consistency (Priority: P2)

As a user, I see consistent colors and accurate icons throughout the application, identical to the approved design.

**Why this priority**: Standardizing the atomic design implementation and removing duplicate code makes the app maintainable.

**Independent Test**: Can be tested by verifying no empty rounded squares exist, and all colors match the approved theme exactly.

**Acceptance Scenarios**:

1. **Given** an icon like category or check_circle is rendered, **Then** the correct SVG glyph appears with proper styling.
2. **Given** I view the UI components (TextInput, StatusBadge, buttons), **Then** they use the standardized shared atomic components rather than local duplicated ones.
3. **Given** I view feature screens, **Then** all colors use semantic `var(--bloom-*)` tokens and no hardcoded values exist.

---

### User Story 4 - Chat Message Legibility (Priority: P3)

As a user, I can read Mr. Bloom chat messages without excessive blank space.

**Why this priority**: Fixes a layout bug in the chat UI.

**Independent Test**: Can be tested by sending short and long messages to Mr. Bloom.

**Acceptance Scenarios**:

1. **Given** a message is displayed in Mr. Bloom chat, **Then** the chat bubble uses content-driven height with properly aligned timestamps.

### Edge Cases

- What happens when standalone previews or companion widgets are loaded directly via URL? (They must remain isolated from the app shell).
- What happens when a user views a screen with a fallback icon? (Fallback icons should no longer appear, except perhaps intentionally as an error state, though ideally unknown names cause build or test failures).
- What happens on resizing the window? (The Garden panel background and chat bubbles must continue to crop and reflow correctly).

## Requirements

### Functional Requirements

- **FR-001**: System MUST consolidate duplicate implementations of text input and status badge components and update consumers.
- **FR-002**: System MUST replace hardcoded palette colors with semantic design tokens from the theme in feature-level components.
- **FR-003**: System MUST provide proper vector geometry for all missing application icon values (category, notes, replan, edit, drag-indicator, rocket, local_cafe, directions_walk, check_circle, check, bug).
- **FR-004**: System MUST remove the rounded empty-square fallback from the application icon component and add a regression test for icon rendering.
- **FR-005**: System MUST implement a routing layout strategy to ensure the desktop application shell and sidebar remain mounted during navigation between primary app pages.
- **FR-006**: System MUST ensure standalone routes (Authentication, Onboarding, Companion Widget) do not accidentally receive the main application shell.
- **FR-007**: System MUST lift the shared Garden panel state to a persistent layout level valid for Today and Goals routes, avoiding unnecessary remounts.
- **FR-008**: System MUST fix the chat message component to remove excessive blank space and use content-driven height.
- **FR-009**: System MUST NOT modify backend code, APIs, database models, or migrations.
- **FR-010**: System MUST preserve existing routes, interactions, content, assets, responsive behavior, and desktop application support.
- **FR-011**: System MUST remove confirmed unused components and stale exports.
- **FR-012**: System MUST reduce draft preview duplication without collapsing distinct views into an unreadable conditional component.
- **FR-013**: System MUST ensure large affected components have clearer responsibility boundaries without needless fragmentation.
- **FR-014**: System MUST prefer behavior-focused tests over implementation-detail assertions and provide a clearly documented manual verification procedure if remount persistence cannot be reliably covered by the current test stack.

## Success Criteria

### Measurable Outcomes

- **SC-001**: 100% of declared application icon names render intentional vector glyphs, and the empty-square fallback never appears.
- **SC-002**: Main application routes successfully share one persistent layout instance without side-effects or remounts.
- **SC-003**: Duplicate text input and status badge implementations are successfully removed and replaced by shared primitives.
- **SC-004**: Feature-level hardcoded colors are 100% removed or explicitly justified in comments.
- **SC-005**: All existing codebase checks, unit/component tests, and production build checks pass.
- **SC-006**: Visual regressions do not exist when compared against approved reference images for affected routes (Today, Goals, Mr. Bloom chat, Settings, Statistics, Garden selection, Authentication, Onboarding, Companion widget).
- **SC-007**: Manual route verification passes for all required desktop/web preview flows without errors or UI glitches (Today → Goals → Today; Today → Mr. Bloom → Settings → Statistics; direct app route loading; isolated standalone routes; message length variations).

## Deliverables

Produce:

1. A route-membership table showing which routes use the persistent app layout and which remain standalone.
2. A theme-token migration strategy.
3. A component consolidation map showing old components and their replacements.
4. A test and visual-regression plan.
5. A clear list of files expected to be added, moved, updated, or deleted.

## Assumptions

- Target environments (Tauri 2, Desktop, Web) remain the same.
- Shared components will be integrated under `src/lib/shared/components/`.
- No visual redesign is desired, only refactoring to match the existing appearance using a cleaner architecture.
