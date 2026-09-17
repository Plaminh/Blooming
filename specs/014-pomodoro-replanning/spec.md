# Feature Specification: Pomodoro and Re-planning

**Feature Branch**: `014-pomodoro-replanning`

**Created**: 2026-09-17

**Status**: Draft

**Input**: User description: Pomodoro and Re-planning

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Start and Manage a Focus Session (Priority: P1)

Users need to be able to start a focus session directly from a Today task and pause/resume it during their focus time. The frontend manages the live timer display without flooding the backend with per-second updates.

**Why this priority**: Without the ability to start, pause, and resume a session, the Pomodoro feature fundamentally does not exist.

**Independent Test**: Can be fully tested by selecting a task, clicking start, pausing the timer, resuming it, and observing the timer counts accurately without backend sync issues.

**Acceptance Scenarios**:

1. **Given** an eligible Today task is selected, **When** the user starts a focus session, **Then** a new active session begins and the live countdown is displayed.
2. **Given** a session is actively running, **When** the user pauses the session, **Then** the timer pauses and the backend records the pause event.
3. **Given** a session is paused, **When** the user resumes the session, **Then** the timer continues and the backend records the resumption event.
4. **Given** an active or paused session is in progress, **When** the user refreshes or reopens the desktop application, **Then** the session state and timer are accurately restored.

---

### User Story 2 - Finish a Session and Complete Task (DONE & FINISHED EARLY) (Priority: P1)

Users must be able to end a focus session successfully when they finish their work, either right on time or early.

**Why this priority**: Reaping the rewards of a focus session by marking tasks complete is the core value proposition of a Pomodoro timer.

**Independent Test**: Can be fully tested by finishing an active session with DONE or FINISHED_EARLY and verifying the task status and recorded session durations.

**Acceptance Scenarios**:

1. **Given** an active or paused session, **When** the user finishes the session with `DONE`, **Then** the session ends and the linked task is marked completed.
2. **Given** an active or paused session, **When** the user finishes the session with `FINISHED_EARLY`, **Then** the session ends, the linked task is marked completed, and the recorded session duration reflects the shorter actual time spent.

---

### User Story 3 - Finish a Session without Completion (NEED MORE TIME & SKIP) (Priority: P2)

Users must be able to gracefully end a focus session if they run out of time without finishing the task, or if they decide to skip it entirely.

**Why this priority**: Handling incomplete states is essential for realistic daily planning, but secondary to the happy path.

**Independent Test**: Can be tested by finishing a session with NEED_MORE_TIME or SKIP and ensuring the task is appropriately left pending or skipped.

**Acceptance Scenarios**:

1. **Given** an active or paused session, **When** the user finishes the session with `NEED_MORE_TIME`, **Then** the session ends, but the linked task remains incomplete and available for future scheduling.
2. **Given** an active or paused session, **When** the user finishes the session with `SKIP`, **Then** the session ends, and the linked task is left incomplete or marked skipped (based on existing product terminology).

---

### User Story 4 - Trigger Re-planning (Priority: P2)

After finishing a focus session, users need their remaining day to automatically adjust and re-plan around the newly recorded session and its outcome.

**Why this priority**: Re-planning dynamically adapts the schedule to the user's actual pace, fulfilling the app's promise of an intelligent calendar, but requires session finishing to be implemented first.

**Independent Test**: Can be tested by finishing a session and verifying that only future flexible tasks shift their scheduled times, while completed and fixed tasks stay put.

**Acceptance Scenarios**:

1. **Given** a session just finished, **When** the system triggers a re-plan, **Then** only incomplete, flexible, future tasks are rescheduled starting from the current effective time or next valid free slot.
2. **Given** a schedule containing completed, fixed-time, locked, and past entries, **When** a re-plan occurs, **Then** these entries and all historical sessions remain completely unchanged.
3. **Given** a schedule where the remaining flexible tasks cannot fit into the available time, **When** a re-plan occurs, **Then** the tasks that cannot fit are reported as unscheduled/overflow tasks and do not disappear silently.

---

### User Story 5 - Lifecycle and State Integrity Validation (Priority: P3)

The system must protect the state from invalid interactions, such as creating simultaneous sessions or finishing an already-finished session.

**Why this priority**: Ensures data consistency and robust edge-case handling.

**Independent Test**: Can be tested by attempting conflicting actions (e.g., rapid clicks, API calls) and verifying the state remains uncorrupted.

**Acceptance Scenarios**:

1. **Given** an active session exists, **When** the user attempts to start another session, **Then** the action is rejected and the original session remains unaffected.
2. **Given** a session is already finished, **When** a finish action is repeated, **Then** the action is rejected, preventing duplicate history or double-completion effects.

---

### Edge Cases

- What happens when a user attempts to pause an already paused session? (The action is rejected/ignored).
- What happens when the user's computer goes to sleep during an active session? (The frontend recalculates the elapsed time upon waking using the persisted timestamps).
- How does the system handle a schedule where all remaining tasks cannot fit? (They are flagged as overflow/unscheduled tasks instead of disappearing).

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The system MUST allow users to start, pause, resume, and finish a focus session from a Today task.
- **FR-002**: The backend MUST persist the start, pause, resume, and finish timestamps of the session.
- **FR-003**: The frontend MUST independently manage the live countdown without sending continuous updates to the backend.
- **FR-004**: The system MUST enforce that a user can only have one active focus session at a time.
- **FR-005**: The system MUST support exactly four finish outcomes: `DONE`, `FINISHED_EARLY`, `NEED_MORE_TIME`, and `SKIP`.
- **FR-006**: The system MUST update the linked task's status to completed when the session outcome is `DONE` or `FINISHED_EARLY`.
- **FR-007**: The system MUST keep the linked task incomplete when the session outcome is `NEED_MORE_TIME` or `SKIP`.
- **FR-008**: The system MUST support a deterministic, rule-based re-planning action after a session finishes.
- **FR-009**: The re-planning engine MUST ONLY modify incomplete, flexible, future tasks.
- **FR-010**: The re-planning engine MUST NOT alter completed tasks, past schedule entries, fixed/locked tasks, or historical sessions.
- **FR-011**: The re-planning engine MUST respect existing durations, deadlines, dependencies, priorities, availability, and ordering constraints where applicable.
- **FR-012**: The system MUST safely handle overflow tasks that cannot fit in the remaining schedule without deleting them.

### Key Entities *(include if feature involves data)*

- **Focus Session**: Represents a period of time the user committed to a task. Tracks start time, accumulated pause time, expected duration, actual duration, outcome, and status (active, paused, finished).
- **Task / Schedule Entry**: The actionable item linked to a focus session. Has properties denoting whether it is flexible or fixed, completed or incomplete.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Users can successfully navigate the start-to-finish flow of a Pomodoro session without state corruption across app reloads.
- **SC-002**: The backend database records zero per-second countdown sync events during an active session.
- **SC-003**: Following a session finish, re-planning executes predictably, leaving 100% of past, completed, and fixed schedule entries unchanged.
- **SC-004**: Users are visually notified of any tasks that are pushed into an "overflow" state during a re-plan.

## Assumptions

- Desktop app environment provides standard local storage or persistence mechanisms to recover state if the user navigates away.
- Actual focus duration excludes paused time.
- "Skipped" tasks are treated according to existing product terminology (i.e. marked as skipped, or simply left incomplete and un-scheduled for the rest of the day).
- Re-planning uses deterministic rules and does not require AI-generated scheduling.
- The Pomodoro interface exists and does not require a UI redesign, only wiring to these behaviors.
