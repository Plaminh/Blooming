# Feature Specification: 013-manual-planning-today

**Feature Branch**: `[013-manual-planning-today]`

**Created**: 2026-09-16

**Status**: Demo Ready (MVP)

**Input**: User description: "/speckit-specify Create Specification **013 — Manual Planning and Today**..."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Create and Edit Manual Task Drafts (Priority: P1)

Users can manually create tasks with their scheduling constraints (duration, priority, fixed/flexible times) without relying on AI, enabling precise control over their work items.

**Why this priority**: Without tasks, there is nothing to schedule. This is the foundational input for the entire planning system.

**Independent Test**: Can be tested via API by submitting a task creation request and verifying it is persisted correctly in the database.

**Acceptance Scenarios**:
1. **Given** an empty state, **When** the user creates a task with title, estimated duration, and priority, **Then** the task is saved with 'DRAFT' status.
2. **Given** an existing task, **When** the user edits its duration or time window, **Then** the updates are saved correctly.
3. **Given** an existing task, **When** the user marks it as dependent on another task, **Then** the dependency is recorded and cyclical dependencies are rejected.

---

### User Story 2 - Generate Deterministic Timeline Draft (Priority: P1)

Users can request a timeline draft that deterministically schedules their active task drafts into available availability windows, respecting priorities, fixed times, and dependencies.

**Why this priority**: This replaces the AI scheduler with a reliable, predictable rule-based engine, which is the core goal of the feature.

**Independent Test**: Can be tested independently by calling the scheduling service with a set of tasks and availability windows, and verifying the exact generated `PlanBlock` timeline.

**Acceptance Scenarios**:
1. **Given** multiple flexible tasks with different priorities, **When** scheduling is requested, **Then** higher priority tasks are scheduled before lower priority ones.
2. **Given** a fixed task and a flexible task, **When** scheduling is requested, **Then** the fixed task is placed at its exact required time, and the flexible task is scheduled around it.
3. **Given** tasks that exceed the availability window, **When** scheduling is requested, **Then** the unscheduled tasks are identified as such, and the Reality Check returns 'OVERLOADED'.
4. **Given** a splittable task that spans across a scheduled break or fixed event, **When** scheduling is requested, **Then** the task is split into valid segments respecting the minimum split duration.

---

### User Story 3 - Save Timeline Draft as Daily Plan (Priority: P1)

Users can review a generated Timeline Draft and save it as their official Daily Plan, transitioning it from 'DRAFT' to 'CONFIRMED' or 'ACTIVE'.

**Why this priority**: Necessary to commit the draft into the system for actual tracking and execution.

**Independent Test**: Can be tested by invoking the save plan API with a valid draft and verifying the `DailyPlan` and `PlanBlock` statuses are updated.

**Acceptance Scenarios**:
1. **Given** a valid Timeline Draft with 'COMFORTABLE' reality check, **When** the user saves the plan, **Then** the `DailyPlan` status becomes 'CONFIRMED' (or 'ACTIVE') and the draft is persisted for Today.
2. **Given** an attempt to save a draft when a plan already exists for that date, **When** the save is requested, **Then** the API rejects the request or handles it safely to prevent duplicates.

---

### User Story 4 - Load Today Screen (Priority: P1)

Users can load the Today screen and see their saved Daily Plan and scheduled blocks in chronological order.

**Why this priority**: Users need to see their plan to execute their day.

**Independent Test**: Can be tested via `GET /today` endpoint verifying it returns the correct `DailyPlan` and ordered `PlanBlock`s for the authenticated user.

**Acceptance Scenarios**:
1. **Given** a saved Daily Plan for the current date, **When** `GET /today` is called, **Then** the API returns the ordered timeline blocks (tasks, breaks, fixed events) and reality check status.
2. **Given** no saved Daily Plan for the current date, **When** `GET /today` is called, **Then** the API returns a clear "no-plan" state without generating a new plan automatically.
3. **Given** another user's Daily Plan, **When** `GET /today` is called by the authenticated user, **Then** the API rejects access.

---

### User Story 5 - Edit Task and Update Status from Today (Priority: P2)

Users can update the status of their tasks (e.g., from 'PLANNED' to 'IN_PROGRESS' or 'COMPLETED') directly from the Today view, and the changes are persisted.

**Why this priority**: Necessary for daily tracking and interaction.

**Independent Test**: Can be tested by calling the status update API for a specific task and verifying the state change.

**Acceptance Scenarios**:
1. **Given** a task block in 'PLANNED' state, **When** the user marks it 'COMPLETED', **Then** the task and block statuses are updated, and the `completed_at` timestamp is recorded.
2. **Given** an invalid status transition (e.g., 'COMPLETED' to 'DRAFT'), **When** the user requests the transition, **Then** the API rejects the update.

## Edge Cases

- What happens when a user creates a dependency cycle between tasks? (The API must reject it during task creation/update).
- How does the system handle tasks larger than the remaining available window? (The scheduler must attempt to split if allowed; if not, leave unscheduled and mark schedule as OVERLOADED).
- How does the system handle overlapping fixed tasks? (The scheduler leaves them overlapping but flags them as a conflict).
- What happens if the timezone changes between creating a draft and saving the plan? (The timezone snapshot at draft creation is preserved).

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001 (Task Drafts)**: The system MUST provide APIs to create, read, update, and delete manual tasks. Tasks MUST support title, estimated duration, priority, scheduling type (FLEXIBLE/FIXED), dependencies, and splittability options.
- **FR-002 (Deterministic Scheduler)**: The system MUST provide a deterministic scheduling service that accepts task drafts and availability windows and returns an ordered timeline of `PlanBlock`s. It MUST NOT use AI services.
- **FR-003 (Scheduling Rules)**: The scheduler MUST prioritize tasks by priority, respect fixed time constraints, insert breaks, respect dependencies, and split tasks only when permitted by the minimum split duration.
- **FR-004 (Reality Check)**: The scheduling service MUST evaluate the generated timeline and return a Reality Check enum ('COMFORTABLE', 'TIGHT', 'OVERLOADED') along with structured reasons (e.g., unscheduled tasks, fixed-task conflicts).
- **FR-005 (Plan Persistence)**: The system MUST provide an API to confirm a Timeline Draft, saving it as a `DailyPlan` and its `PlanBlock`s. It MUST prevent duplicate active plans for the same date.
- **FR-006 (Today API)**: The system MUST provide a `GET /today` API that returns the authenticated user's saved Daily Plan and ordered timeline blocks for the requested or current local date.
- **FR-007 (Status Updates)**: The system MUST provide an API to update task and block statuses, validating transitions and recording timestamps (e.g., `completed_at`).
- **FR-008 (User Isolation)**: All APIs MUST strictly enforce user ownership, never exposing or modifying another user's data.

### Key Entities

- **Task**: The core work item, including duration, priority, constraints, and whether it can be split.
- **TaskDependency**: Defines prerequisite relationships between tasks.
- **DailyPlan**: The container for a user's plan for a specific date, tracking the overall status and Reality Check.
- **AvailabilityWindow**: Defines the time bounds within which the scheduler can place tasks.
- **PlanBlock**: An individual scheduled segment (Task, Break, Fixed Event) on the timeline.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001 (Determinism)**: Identical valid task inputs and availability windows consistently produce the exact same scheduled timeline and Reality Check result, verified via automated testing.
- **SC-002 (Performance)**: The deterministic scheduling algorithm completes in under 500ms for a set of 50 tasks.
- **SC-003 (Independence)**: The entire planning and Today workflow functions correctly with all AI services disabled or unreachable.
- **SC-004 (Reliability)**: 100% of cyclic dependencies and invalid fixed-task overlaps are caught and rejected or flagged by the API and scheduler.

## Assumptions

- We are extending the existing database schema (`Task`, `DailyPlan`, `PlanBlock`, `AvailabilityWindow`). Fields for splittability (e.g., `is_splittable`, `min_split_duration_minutes`) and break preferences will be added to the `Task` or user preferences schema.
- The user's timezone is provided in the API requests or retrieved from user settings to determine local date boundaries.
- Authentication is handled by the existing backend infrastructure.
- The Today UI will adapt to consume the structured Reality Check reasons alongside the enum.
