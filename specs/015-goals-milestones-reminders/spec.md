# Feature Specification: goals-milestones-reminders

**Feature Branch**: `[015-goals-milestones-reminders]`

**Created**: 2026-09-17

**Status**: Draft

**Input**: User description: "Create feature 015-goals-milestones-reminders based on the requirements in 04-goals-reminders(1).md..."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Goal Management (Priority: P1)

As a user, I want to manage my existing goals so that I can refine and track my high-level objectives.
Goals and roadmap structure are created through Mr. Bloom. The Goals screen is used to view and manually edit existing Goal/Roadmap data.

**Why this priority**: Goals are the foundational entity for this feature, required before milestones and reminders can be meaningful.

**Independent Test**: Can be fully tested by editing an existing goal and verifying the data persists and displays correctly in the UI.

**Acceptance Scenarios**:

1. **Given** I have existing goals, **When** I edit a goal's details, **Then** the updated details are persisted and immediately reflect in the UI without a manual reload.

---

### User Story 2 - Milestone Management (Priority: P1)

As a user, I want to manage milestones within a goal so that I can track their status and target dates.
Goals and roadmap structure are created through Mr. Bloom. The Goals screen is used to view and manually edit existing Goal/Roadmap data.

**Why this priority**: Milestones make goals actionable and provide the context for reminder generation and tracking.

**Independent Test**: Can be fully tested by updating the status and target date of an existing milestone, and ensuring changes persist and the roadmap ordering remains stable.

**Acceptance Scenarios**:

1. **Given** an existing milestone, **When** I update its status and target date, **Then** the changes are persisted, displayed immediately, and the milestone ordering remains stable.

---

### User Story 3 - Due Reminders Loading (Priority: P2)

As a user, I want to see my due reminders so that I know what tasks need attention right now.

**Why this priority**: Once goals and milestones exist, the user needs to be prompted to take action when target dates approach.

**Independent Test**: Can be fully tested by verifying that `GET /reminders/due` returns only due reminders for the authenticated user, excluding completed, dismissed, cancelled, or postponed ones, and handling loading/error/empty states cleanly.

**Acceptance Scenarios**:

1. **Given** there are pending due reminders for my account, **When** I load the due reminders view, **Then** I see only my due reminders, and the UI displays them correctly.
2. **Given** there are no due reminders, **When** I load the view, **Then** the UI gracefully shows an empty state without breaking the screen.

---

### User Story 4 - Reminder Actions (Priority: P2)

As a user, I want to take action on my due reminders (create plan, mark completed, move milestone, or remind later) so that I can progress my goals or manage my schedule.

**Why this priority**: Loading reminders is only useful if the user can act on them.

**Independent Test**: Can be fully tested by performing each action on a due reminder and verifying the expected state change (e.g., milestone status updated, reminder postponed) and UI update.

**Acceptance Scenarios**:

1. **Given** a due reminder for a milestone, **When** I select "Mark completed", **Then** the reminder is completed, the associated milestone is updated consistently, and the reminder is removed from the due list.
2. **Given** a due reminder, **When** I select "Remind later" to a valid future time, **Then** the reminder is postponed and disappears from the current due list.
3. **Given** a due reminder for a milestone, **When** I select "Move milestone", **Then** I can change the milestone target date, and its reminder schedule updates accordingly.

### Edge Cases

- What happens when a user attempts to update a milestone belonging to a different goal? (Backend authorization must prevent this, returning a clear error).
- How does the system handle an action on a reminder that has already been completed in another session? (Must not apply the completion twice; backend should handle gracefully).
- What happens if the backend fails to load goals or reminders? (UI must display a clean error state without breaking the overall Goals/Roadmap screen).
- What happens when a goal with existing milestones and reminders is deleted? (Must safely handle dependent records according to existing deletion conventions).

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The system MUST load and display persisted goals in the existing Goals/Roadmap UI.
- **FR-002**: Goals and roadmap structure are created through Mr. Bloom. Users MUST be able to view and edit existing goals.
- **FR-003**: The UI MUST preserve its current design, reusing existing components, layouts, dialogs, form controls, stores, services, and types wherever possible.
- **FR-004**: Users MUST be able to view and edit existing milestones belonging to a specific goal.
- **FR-005**: The system MUST allow milestone status updates using predefined project statuses, and allow target-date updates.
- **FR-006**: The UI MUST immediately display milestone changes after a successful action without requiring a manual reload, maintaining stable ordering and roadmap presentation.
- **FR-007**: The backend MUST prevent a milestone from being modified through a different goal.
- **FR-008**: The system MUST implement and integrate `GET /reminders/due` to return only reminders currently due for the authenticated user, excluding completed, dismissed, cancelled, or postponed reminders.
- **FR-009**: The UI MUST display due reminders using the existing reminder UI (or smallest compatible addition), handling empty, loading, and error states cleanly.
- **FR-010**: Users MUST be able to perform "Create plan", "Mark completed", "Move milestone", and "Remind later" actions on due reminders.
- **FR-011**: The system MUST persist all data for goals, milestones, and reminders across application restarts using the real backend.
- **FR-012**: The backend MUST validate all required fields and date values, returning clear errors for invalid data, invalid transitions, and missing records.
- **FR-013**: The backend MUST enforce authorization so users cannot read or modify other users' data.
- **FR-014**: The backend MUST prevent duplicate plans or double completions from repeated reminder actions.
- **FR-015**: The system MUST safely handle dependent milestones and reminders when a goal is deleted, following existing project conventions.

### Key Entities *(include if feature involves data)*

- **Goal**: Represents a high-level objective. Has a title, description, and owns multiple milestones.
- **Milestone**: An actionable step within a goal. Has a title, status, and an optional target date. Must belong to exactly one Goal.
- **Reminder**: A notification entity generated for milestones or goals to prompt user action. Tracks due date, status (due, completed, postponed, dismissed), and relation to parent entities.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Users can complete the full demo flow (load goals, create goal and roadmap milestones via Mr. Bloom draft, edit existing milestone, load due reminder, perform reminder action) without any backend AI service or external API being required.
- **SC-002**: 100% of state-mutating actions (create, edit, delete, actions) immediately reflect in the local UI state without a full page reload.
- **SC-003**: `GET /reminders/due` returns only the correct user's due reminders and 0 records of completed/dismissed/postponed status.
- **SC-004**: Automated tests verify critical CRUD operations, user ownership boundaries, due-reminder filtering, and reminder-action flows.
- **SC-005**: All UI actions preserve the existing Goals/Roadmap visual appearance and do not negatively impact unrelated screens.

## Assumptions

- The project's existing deletion conventions dictate how dependent milestones/reminders are handled when a parent goal is deleted (e.g., cascade delete or soft delete).
- Existing backend authorization middleware is available and can be applied to the new/updated endpoints.
- The predefined statuses for milestones are already established in the database or domain models.
- "Create plan" from a reminder triggers an existing plan-creation flow initialized with the context.
