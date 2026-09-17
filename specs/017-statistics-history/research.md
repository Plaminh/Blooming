# Phase 0: Outline & Research

## Decision 1: Aggregation Strategy for Plan History Tasks
**Decision**: Use an aggregate scalar subquery or grouping to compute total tasks and completed tasks for the Plan History to avoid N+1 queries.
**Rationale**: Paginating `DailyPlan` and joining `PlanBlock` (where `block_type = 'TASK'`) via GROUP BY or scalar subqueries keeps it in a single SQL operation, keeping pagination bounded and fast.
**Alternatives considered**: Loading all plans and their blocks into Python memory, which degrades performance as history grows.

## Decision 2: Timezone Handling for Daily Stats
**Decision**: Pass the user's local timezone (e.g., from `UserSettings` or frontend `Intl.DateTimeFormat().resolvedOptions().timeZone`) and use PostgreSQL's `AT TIME ZONE` to group timestamps by local date.
**Rationale**: Focus runs are stored in UTC (`DateTime(timezone=True)`). Using `AT TIME ZONE :tz` ensures day boundaries are accurate to the user's specified reporting period.
**Alternatives considered**: Doing grouping in Python, which complicates matching continuous day ranges with zeros.

## Decision 3: Plan Status Classification
**Decision**: `COMPLETED` plans are "Completed". `CONFIRMED` and `ACTIVE` plans are "Unfinished". `DRAFT` and `ARCHIVED` plans are excluded from completion statistics.
**Rationale**: Follows existing domain rules for active/completed plans.

## Decision 4: Focus Time Calculation
**Decision**: Focus time is the sum of `actual_duration_seconds` for `FocusRun` where `status = 'ENDED'`.
**Rationale**: The spec requires excluding paused/abandoned runs and paused time. The `actual_duration_seconds` accurately reflects the final tracked focus.
