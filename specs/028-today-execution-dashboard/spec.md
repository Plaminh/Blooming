# Feature Specification: Refactor Today into an Execution-Only Dashboard

**Feature Branch**: `028-today-execution-dashboard`  
**Created**: 2026-09-26  
**Status**: Draft  
**Input**: User description: "Refactor Today into an execution-only dashboard. Today is responsible for viewing persisted Daily Plan, date navigation, selecting/inspecting tasks, viewing timeline blocks, starting Focus sessions, recording execution outcomes, marking tasks completed, requesting Quick Replan, and navigating to Mr. Bloom for plan changes. Today is NOT responsible for directly editing plan structure or metadata."

---

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Inspecting Daily Schedule & Task Details in Read-Only Mode (Priority: P1)

As a focused user viewing my day, I want to review my persisted schedule, navigate past and future dates, and select tasks to inspect their full details in a read-only sidebar without accidentally modifying plan metadata or bypassing the scheduling engine.

**Why this priority**: Today is the central execution cockpit of Blooming. Preventing accidental, unvalidated manual edits is fundamental to maintaining a realistic, conflict-free schedule validated by the deterministic scheduler.

**Independent Test**: Can be tested independently by loading an existing day plan with scheduled blocks, selecting different task cards, and verifying that the details pane renders accurate task information with zero editable fields, no "Edit Manually" toggle, and no direct delete controls.

**Acceptance Scenarios**:

1. **Given** a user navigates to `/today` for a date with a confirmed plan, **When** the page renders, **Then** the timeline displays scheduled task blocks, break intervals, the current-time indicator (for current day), and any carried-over tasks.
2. **Given** a user selects a scheduled task on the timeline, **When** the Right Rail (task details panel) opens, **Then** it displays title, description/notes, duration, time window, category, priority, status, carry-over indicator, and associated goal/milestone info (where available) as static, read-only text.
3. **Given** a user views the Right Rail, **When** inspecting available controls, **Then** there is no "Edit Manually" button, pencil icon, inline input, category dropdown, duration editor, or direct delete button.
4. **Given** a user views a date with no persisted plan, **When** the empty state is displayed, **Then** the user is presented with a clear prompt to plan the day with Mr. Bloom, without any inline task authoring form.
5. **Given** a user navigates across different dates using date navigation arrows or picker, **When** viewing a historical or future date, **Then** the corresponding persisted plan is loaded in read-only mode with the same execution-focused inspection capabilities.

---

### User Story 2 - Executing Tasks & Recording Outcomes from Today (Priority: P1)

As a user executing my scheduled work, I want to initiate focus sessions, record focus outcomes, and mark tasks complete directly from Today so that my progress and rewards are captured immediately without treating execution mutations as plan authoring.

**Why this priority**: Execution mutations (starting focus, recording outcomes, marking tasks complete) reflect real-world action and award in-game resources (Water, Leaves). They are distinct from structural plan re-authoring and must be frictionless within the dashboard.

**Independent Test**: Can be tested independently by selecting an upcoming task, launching a focus session, completing the session or directly checking "Mark Complete", and verifying that execution state changes, timestamps record, and rewards are granted without modifying the plan structure.

**Acceptance Scenarios**:

1. **Given** an upcoming task is selected in Today, **When** the user selects a focus preset (25/5, 50/10, or Custom) and clicks "START FOCUS", **Then** a focus session is initiated for that task, the task status transitions to active/in-progress, and the desktop widget synchronizes.
2. **Given** a task is in progress or selected in the Right Rail, **When** the user triggers "Mark Complete", **Then** the task and its corresponding timeline block transition to completed, completion timestamps are recorded, and Leaf rewards are credited to the user's ledger according to Blooming economy rules.
3. **Given** a focus session ends with an outcome of "DONE" or "FINISHED EARLY", **When** the outcome is recorded, **Then** Water rewards are credited, and the task status updates to completed.
4. **Given** a task is completed, **When** viewed on the timeline and Right Rail, **Then** its visual presentation reflects completed status and further focus initiation is disabled.

---

### User Story 3 - Quick Replanning for Execution Shifts (Priority: P2)

As a user whose day has shifted due to an overrun, early finish, or brief interruption, I want to trigger a Quick Replan from Today so that the deterministic scheduler automatically rearranges my remaining work around the current time without altering task definitions or requiring chat intervention.

**Why this priority**: Days rarely go exactly as planned. When execution drifts, users need an instant, non-conversational schedule realignment that preserves existing task data and uses the deterministic scheduler.

**Independent Test**: Can be tested independently by taking a day with unfinished tasks where time has elapsed, clicking "Quick Replan", and verifying that remaining unfinished tasks are recomputed from the current time forward without changing task titles, durations, or constraints.

**Acceptance Scenarios**:

1. **Given** an active daily plan with unfinished tasks, **When** the user clicks "Quick Replan", **Then** the deterministic scheduler recalculates the start and end times for remaining uncompleted tasks based on current time and available schedule windows.
2. **Given** the scheduler reorders or pushes tasks during Quick Replan, **When** the new schedule is returned, **Then** the Today timeline updates immediately to reflect the revised blocks, and the revision history is preserved.
3. **Given** a task cannot fit into the remaining day during Quick Replan, **When** the replan completes, **Then** an informative banner informs the user which tasks could not fit and suggests adjusting availability or planning with Mr. Bloom.

---

### User Story 4 - Handing Off Structural Plan Modifications to Mr. Bloom (Priority: P1)

As a user who needs to add new tasks, remove work, modify task durations, alter time windows, or change constraints, I want a seamless transition from Today to Mr. Bloom with my plan context preserved so that all structural changes are validated by the deterministic scheduler before replacing my plan.

**Why this priority**: Structural changes (adding/removing tasks, modifying durations, editing priorities, altering time constraints) require re-evaluation against the user's total availability, dependencies, and scheduler invariants. Mr. Bloom owns plan authoring and draft refinement; Today must delegate this cleanly.

**Independent Test**: Can be tested independently by clicking "Adjust with Mr. Bloom" from Today (or from a selected task in Right Rail), verifying that Mr. Bloom opens with the active day and task context loaded into draft editing state, and verifying that the updated plan only replaces Today after explicit scheduler preview and save.

**Acceptance Scenarios**:

1. **Given** a user is viewing Today and needs to change plan structure, **When** clicking "Adjust with Mr. Bloom" (or from the Right Rail action), **Then** the user is navigated to Mr. Bloom with the current plan date and selected task context passed through.
2. **Given** Mr. Bloom receives the plan adjustment request, **When** the user requests modifications (e.g., "drop task B", "make task A 60 minutes instead of 30"), **Then** changes are applied to the working `TodayDraft`.
3. **Given** modifications have been applied to `TodayDraft`, **When** the user proceeds, **Then** any prior timeline preview is invalidated and a fresh timeline must be generated and validated by the deterministic scheduler.
4. **Given** a valid scheduler preview is generated in Mr. Bloom, **When** the user explicitly confirms "Save", **Then** the updated daily plan is persisted and navigating back to Today reflects the newly approved schedule.

---

### User Story 5 - Handling Task Skips Consistently (Priority: P2)

As a user choosing not to complete a scheduled task today, I want any skip action to integrate with the focus outcome and replanning flow rather than leaving a stale gap on the timeline.

**Why this priority**: Standalone "orphan" skips leave downstream timeline blocks misaligned with reality. Skips must cleanly transition task state and trigger deterministic rescheduling of subsequent work.

**Independent Test**: Can be tested by concluding a focus session with outcome "SKIP" (or choosing skip within the execution flow) and verifying that the remaining timeline automatically triggers a replan or prompts the user to realign remaining blocks.

**Acceptance Scenarios**:

1. **Given** a focus session is concluded with outcome "SKIP", **When** the outcome is recorded, **Then** the task is marked as skipped, zero Water rewards are granted for the skipped task, and the remaining schedule is evaluated for replanning.
2. **Given** a task is skipped outside an active focus session via an execution action, **When** processed, **Then** the system does not leave the future timeline in a stale state; it triggers a schedule recalculation or prompts for Quick Replan.

---

### Edge Cases

- **Task completed while offline / network drop**: Execution mutation (Mark Complete) displays a clear retry indicator if offline; user state is queued or warned without allowing the UI to enter an inconsistent edit state.
- **Zero tasks remaining after Quick Replan**: When all remaining tasks have already been completed or skipped, triggering Quick Replan gracefully confirms the schedule is complete rather than failing.
- **Overloaded day upon Replan**: If remaining tasks exceed the remaining hours of the day during Quick Replan, overflow tasks are marked unscheduled and surfaced in a notification banner with an invitation to adjust in Mr. Bloom.
- **Navigating to Mr. Bloom with unsaved execution state**: If an active focus session is running, attempting to navigate to Mr. Bloom warns the user that an active session is in progress.
- **Cross-window synchronization**: When a task is marked complete or a focus session starts in Today, a cross-window notification updates the Desktop Widget and tray status immediately.
- **Historical plans**: Viewing past dates displays the final historical execution state of tasks (completed, skipped, or uncompleted) with execution actions disabled for past days.

---

## Requirements *(mandatory)*

### Functional Requirements

#### Screen Responsibilities & Boundaries
- **FR-001**: The `/today` screen MUST serve strictly as an execution dashboard and schedule viewer.
- **FR-002**: The `/today` screen MUST NOT allow direct authoring, editing, or deletion of plan structure or task metadata.
- **FR-003**: The Today UI MUST remove the "Edit Manually" button, edit toggle, and any editable task form from the timeline and Right Rail.
- **FR-004**: The Today UI MUST remove direct task deletion controls (`Delete Task` / trash can icon) from the Today view.
- **FR-005**: All structural plan mutations (adding tasks, removing tasks, reordering tasks, changing durations, changing categories, editing notes/descriptions, changing priorities, changing time constraints/fixed times) MUST be authored exclusively through Mr. Bloom.

#### Read-Only Right Rail Inspection
- **FR-006**: Selecting a task or break block on the timeline MUST populate the Right Rail with the block's persisted details.
- **FR-007**: The Right Rail MUST render all supported task metadata in a non-editable, read-only presentation:
  - Task title
  - Description / notes
  - Category (badge)
  - Priority (where present)
  - Estimated duration and scheduled time window
  - Task status (upcoming, in-progress, completed, skipped)
  - Carry-over indicator (where applicable)
  - Linked goal or milestone information (where available)
- **FR-008**: The Right Rail MUST provide only the following user actions:
  - "START FOCUS" (with preset selector: 25/5, 50/10, Custom)
  - "MARK COMPLETE"
  - "ADJUST WITH MR. BLOOM" (navigating to Mr. Bloom with task and date context)

#### Execution Mutations vs. Plan Mutations
- **FR-009**: The system MUST distinguish between **Execution Mutations** (permitted on Today) and **Plan Mutations** (restricted to Mr. Bloom):
  - *Execution Mutations*: Starting a focus session, recording a focus outcome, marking a task complete, and triggering a deterministic Quick Replan.
  - *Plan Mutations*: Creating tasks, deleting tasks, editing task titles/durations/categories/notes/priorities, and changing availability windows.
- **FR-010**: Marking a task complete from Today MUST update task status to `COMPLETED`, record `completed_at`, and award Leaf rewards according to the Blooming resource ledger rules (1 Leaf per completed task, idempotent).
- **FR-011**: Starting a focus session from Today MUST record the active session run, transition the selected task to active/in-progress, and signal the desktop widget.
- **FR-012**: Completing a focus session MUST award Water resources (1 Water per valid focus, 0 for skip) and record session history.

#### Schedule Realignment & Replan
- **FR-013**: The Today screen MUST retain a "QUICK REPLAN" action that invokes the deterministic scheduler to rearrange remaining unfinished work from the current time forward without modifying task properties.
- **FR-014**: The Today screen MUST NOT support standalone task skipping that leaves downstream timeline blocks unadjusted. Any skip outcome MUST trigger or prompt a timeline recalculation.
- **FR-015**: When a user selects "ADJUST WITH MR. BLOOM", the application MUST transition to Mr. Bloom, load the active plan date and selected task into a draft editing session, require a deterministic scheduler preview before any save, and require an explicit Save before updating the persisted plan.

#### Backward Compatibility & Dependency Safety
- **FR-016**: Existing backend REST endpoints for task updating (`PATCH /today/tasks/{task_id}`) and task deletion (`DELETE /today/tasks/{task_id}`) MUST NOT be removed in this specification; their deprecation or retirement will be evaluated strictly following codebase dependency analysis during implementation.
- **FR-017**: The Goals feature, Garden feature, Desktop Widget internals, and core deterministic scheduler algorithm MUST NOT be modified as part of this feature.

---

### Key Entities

- **DailyPlan**: The authoritative, persisted daily plan entity representing a user's approved schedule for a given date. Contains ordered `PlanBlock` records.
- **PlanBlock**: A scheduled time block belonging to a `DailyPlan`, representing either a planned work task (linked to a `Task`) or a rest/break interval.
- **Task**: The persistent unit of work containing user intent, metadata (title, category, duration, priority, notes), and execution lifecycle status (`PENDING`, `IN_PROGRESS`, `COMPLETED`, `SKIPPED`).
- **Execution Mutation**: An in-flight update capturing real-world execution events (`start_focus`, `complete_task`, `record_outcome`) that modifies execution state and awards game resources (Water, Leaves) without rewriting plan definitions.
- **TodayDraft**: The mutable, intermediate plan representation used exclusively within Mr. Bloom during planning and adjustment, requiring validation by the deterministic scheduler and explicit user confirmation before replacing a `DailyPlan`.

---

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: 100% of task metadata fields displayed on the Today screen (title, description, category, duration, notes, times) are non-editable text inputs with zero inline editing capability.
- **SC-002**: 0 direct task creation, manual inline editing, or deletion actions exist within the Today interface (all structural changes navigate to Mr. Bloom).
- **SC-003**: 100% of structural plan changes initiated from Today pass through Mr. Bloom and receive deterministic scheduler validation before updating the persisted plan.
- **SC-004**: Users can complete execution actions (Start Focus, Mark Complete, Quick Replan) within 2 clicks from the Today dashboard.
- **SC-005**: 100% of task completions executed from Today correctly increment user Leaves and record completion timestamps without requiring conversational interaction.
- **SC-006**: Existing manual test suite case `TODAY-UI-03` is cleanly updated from "Edit Task Metadata Directly" to "Today Task Details Are Read-Only", and passes all verification steps.

---

## Assumptions

- The deterministic scheduler and Mr. Bloom draft editing capabilities (`TodayDraft`, preview tokens, deferred save) implemented in features 023-027 are fully functional and capable of receiving context from Today.
- Existing backend endpoints (`PATCH /today/tasks/{id}`) may remain functional on the server during the transition period to support any dependent sub-systems (e.g., legacy scripts or widget edge cases) until explicitly decommissioned.
- Users who need to make structural adjustments are willing to transition to Mr. Bloom's conversational or structured draft interface for scheduler-validated replanning.
- Game resource rewards are limited to Water (for focus completion) and Leaves (for task completion); no legacy points or coin concepts are used.
