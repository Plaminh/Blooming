# Feature Specification: Full-Stack Cleanup and Missing Integration Completion

**Feature Branch**: `[019-cleanup-integration]`

**Created**: 2026-09-17

**Status**: Corrective implementation; runtime validation pending

**Input**: User description: "Full-Stack Cleanup and Missing Integration Completion..."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Today Page Actions (Priority: P1)

As a user, I want the Edit and Replan actions on the Today page to perform real operations so that I can maintain an accurate schedule.

**Why this priority**: Core scheduling operations are broken or disconnected. Fixing these ensures the primary value proposition of the app works.

**Independent Test**: Can be fully tested by editing a scheduled block, confirming it updates in the backend and refreshes the UI without full reload. Clicking replan will preserve completed blocks, reschedule unfinished ones, and refresh the companion widget automatically.

**Acceptance Scenarios**:

1. **Given** I am on the Today page, **When** I edit a block's title or notes and save, **Then** the backend is updated, and the schedule refreshes.
2. **Given** I click "Replan", **When** the operation completes, **Then** completed blocks remain as they were, eligible unfinished work is rescheduled, and the UI immediately reflects the changes.
3. **Given** I change the schedule in the main window, **When** the operation finishes, **Then** the Tauri companion widget automatically updates its state via a Tauri cross-window event.

---

### User Story 2 - Accurate Garden State (Priority: P1)

As a user, I want my plant's actual species, growth stage, and vitality reflected in the widget and garden views rather than placeholder visuals.

**Why this priority**: The garden is a core reward mechanism. Hard-coded visuals break user trust and progression.

**Independent Test**: Can be fully tested by selecting different plants in the backend and verifying that both the garden view and the widget render the corresponding valid sprite frames.

**Acceptance Scenarios**:

1. **Given** my garden state has a specific plant and growth points, **When** I open the widget or garden view, **Then** the correct plant sprite frame is displayed, derived from central thresholds.
2. **Given** the backend garden data is unavailable, **When** I view the garden, **Then** the app falls back gracefully without overwriting my valid persisted state.

---

### User Story 3 - Milestone Reminders & Quiet Hours (Priority: P2)

As a user, I want my milestone reminders to trigger at the correct lead time and respect my configured quiet hours, so I am not disturbed at night but still get useful notice before deadlines.

**Why this priority**: Notifications that wake users at night or trigger at useless fixed times will cause users to uninstall the app.

**Independent Test**: Can be fully tested by setting milestone reminder lead time in settings, creating a milestone, and observing that the reminder's scheduled time reflects the correct offset, and is suppressed if it falls within quiet hours.

**Acceptance Scenarios**:

1. **Given** I set my milestone lead time to "1 day before", **When** I create a milestone due tomorrow at 5 PM, **Then** a reminder is scheduled for today at 5 PM.
2. **Given** my quiet hours are set to 22:00–07:00, **When** a reminder is scheduled for 23:00, **Then** the system suppresses delivery without permanently marking it completed or skipped.

---

### User Story 4 - Desktop Integrations (Priority: P2)

As a user, I want the app to start at login and optionally stay always-on-top, and I want to see a tray icon indicator when I have due reminders.

**Why this priority**: Native desktop features are essential for a companion app to feel integrated and unobtrusive.

**Independent Test**: Can be tested by toggling "Start at login", restarting the system or simulating login, and verifying the app autostarts correctly.

**Acceptance Scenarios**:

1. **Given** I enable "Start at login" in settings, **When** the Tauri permission is successfully granted, **Then** the setting is persisted and synchronized.
2. **Given** the app is running in the background with a due reminder, **When** I look at the system tray, **Then** the icon displays a red-dot variant.

### Edge Cases

- What happens if the widget countdown reaches zero exactly at the same time a manual completion is triggered? (Must prevent repeated completion side effects, ensuring only one state transition occurs).
- What happens if quiet hours are set across a timezone boundary or daylight saving transition? (Must interpret the range using the configured IANA timezone, ensuring accurate boundaries).
- What happens if starting a focus session fails on the backend? (Must display a user-visible error and recover the UI state, rather than silently failing).

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The system MUST persist and invoke real backend operations for Today page Edit and Replan actions, refreshing the Today schedule and syncing the Tauri companion widget using Tauri cross-window events (not browser `CustomEvent`).
- **FR-002**: The system MUST render the actual selected plant species and derived growth stage in the widget and garden views, removing hard-coded `monstera` and frame `0` values.
- **FR-003**: The backend MUST persist non-negative cumulative growth points in the `garden_states` table through direct edits to authoritative SQL CREATE TABLE files, with no new feature Alembic migration, deriving the growth stage from centralized thresholds instead of persisting a duplicated enum.
- **FR-004**: The system MUST respect configured quiet hours (including overnight ranges) in the user's IANA timezone, suppressing due reminder delivery during these hours without marking them skipped/completed.
- **FR-005**: The system MUST store milestone reminder lead time as a validated number of minutes in `UserSettings` and sync milestone reminders to trigger at the deadline minus the lead time.
- **FR-006**: The system MUST integrate the Tauri v2 autostart plugin and Always-on-top permission, ensuring settings state matches the native runtime state.
- **FR-007**: The system MUST provide a system tray icon that toggles to a red-dot variant when actionable reminders are due, returning to normal when none are due.
- **FR-008**: The system MUST map the `description` field from the backend task model to the "Notes" field in the Today UI.
- **FR-009**: The system MUST add `category` as a validated string field to the backend `Task` model, updating the corresponding schemas and authoritative SQL definitions, and map it correctly to the Today UI.
- **FR-010**: The backend MUST use timezone-aware UTC timestamps for garden unlock idempotency logic.
- **FR-011**: The system MUST show a user-visible error when a focus session fails to start, and ensure the widget countdown transition at zero seconds completes exactly once.
- **FR-012**: The backend MUST suppress output of sensitive email reset tokens/links in production environments.

### Key Entities

- **GardenState**: Add cumulative `growth_points` and expose derived `growth_stage`; preserve legacy persisted `stage`, visual counts and unrelated currency columns.
- **UserSettings**: Updated to include `milestone_reminder_lead_time_minutes` (persisted integer).
- **Task**: The `description` field maps to "Notes" in the UI.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Today UI Replanning successfully completes in under 2 seconds, preserving finished tasks and refreshing both the main window and companion widget.
- **SC-002**: 100% of hard-coded plant states (monstera, frame 0) are removed from the production codebase and replaced with derived logic based on the user's persisted garden state.
- **SC-003**: Reminder delivery logic suppresses 100% of notifications during the exact bounds of a user's configured quiet hours in their local timezone.
- **SC-004**: Static checks, builds, unaffected historical tests and recorded manual exercises validate quiet-hour boundaries, timezone conversions, native settings failures and countdown transitions. No new feature-specific test files or replacement coverage are introduced. Native checks must be performed in a real Tauri runtime before claiming completion.
- **SC-005**: All production logs are verified to contain 0 instances of sensitive email links or user secrets.

## Assumptions

- The existing polling architecture for reminder evaluation is maintained, as replacing it with a local Tauri scheduler is a large architectural change not strictly required for MVP unless explicitly approved.
- The system tray icon is considered part of the MVP and implemented since no explicit specification defers it.
- Milestone reminder lead time defaults to a safe value (e.g., 24 hours / 1440 minutes) for existing users.
- The `description` field is fully sufficient for task notes.

## Corrective scope decisions

- Direct SQL sources: database/migrations/01_users_and_auth.sql, 04_tasks_and_dependencies.sql, 08_heart_and_garden.sql. No new Alembic feature migration or baseline edits. No automatic database volume changes. Existing databases require manual updates or recreation.
- Category: Learning, Work, Personal or NULL. Uncategorized is UI text only. Title, duration, category and notes edits preserve drafts and report errors accessibly; category/description accept explicit null.
- Actual endpoints: PATCH /api/v1/today/tasks/{task_id}, POST /api/v1/today/replan (no request body).
- growth_stage: SPROUTING 0-99, GROWING 100-299, BLOOMING 300-699, FLOURISHING 700+. Growth is atomic with eligible Leaves awards using existing completion keys, no separate currency event, no helper commits.
- Lead time: integer 0-43200 inclusive, default 1440. original_due_at retains the deadline, due_at is deadline minus lead time. Synchronize milestone creation, deadline/title/status edits and settings changes without duplicate active reminders.
- Quiet hours apply only when enabled, using UserSettings timezone, inclusive start/exclusive end (equal endpoints empty), with safe UTC fallback for invalid zones. Suppression preserves reminder status.
- Preserve historical tests and unrelated user changes. Remove feature-specific test files and test-only additions. The user's corrective validation decision overrides new-test requirements for this feature. Actual validation evidence and pending desktop checks are in quickstart.md.
