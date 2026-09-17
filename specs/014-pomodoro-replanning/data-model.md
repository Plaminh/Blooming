# Data Model: Pomodoro and Re-planning

## Entities

### `FocusRun` (Database Table: `focus_runs`)
Represents an individual Pomodoro session linked to a specific user and task.

**Fields**:
- `id`: UUID (Primary Key)
- `user_id`: UUID (Foreign Key to users)
- `task_id`: UUID (Foreign Key to tasks)
- `plan_block_id`: UUID (Foreign Key to plan_blocks)
- `status`: Enum String (`READY`, `FOCUSING`, `PAUSED`, `ENDED`)
- `outcome`: Enum String (`DONE`, `NEED_MORE_TIME`, `SKIP`, `FINISHED_EARLY`) - null until ended
- `planned_focus_seconds`: Integer
- `planned_break_seconds`: Integer
- `started_at`: DateTime (UTC)
- `expected_end_at`: DateTime (UTC)
- `paused_at`: DateTime (UTC)
- `total_paused_seconds`: Integer
- `ended_at`: DateTime (UTC)
- `actual_duration_seconds`: Integer
- `created_at`, `updated_at`: DateTime (UTC)

**Constraints**:
- A user can only have one active `FocusRun` where `status` is in `('READY', 'FOCUSING', 'PAUSED')`.
- `ended_at` must be >= `started_at`.
- `total_paused_seconds` must be >= 0.

### `FocusRunEvent` (Database Table: `focus_run_events`)
An append-only log of session lifecycle events, useful for auditing and analytics.

**Fields**:
- `id`: UUID (Primary Key)
- `focus_run_id`: UUID (Foreign Key to focus_runs)
- `event_type`: Enum String (`STARTED`, `PAUSED`, `RESUMED`, `ENDED`, `OUTCOME_RECORDED`)
- `occurred_at`: DateTime (UTC)
- `payload`: JSONB (Optional metadata, e.g., the specific outcome string)

### `Task` (Database Table: `tasks`)
The underlying actionable item. Focus sessions modify its status.

**Relevant Fields for Re-planning & Pomodoro**:
- `status`: Enum String (`DRAFT`, `PENDING`, `IN_PROGRESS`, `COMPLETED`, `SKIPPED`, `CANCELLED`)
- `scheduling_type`: Enum String (`FLEXIBLE`, `FIXED`)
- `estimated_duration_minutes`: Integer

### `PlanBlock` (Database Table: `plan_blocks`)
The scheduled blocks on the calendar.

**Relevant Fields for Re-planning**:
- `planned_start_at`: DateTime (UTC)
- `planned_end_at`: DateTime (UTC)
- `status`: Enum String (`PLANNED`, `ACTIVE`, `COMPLETED`, `SKIPPED`, `CANCELLED`)
- `block_type`: Enum String (`TASK`, `BREAK`, `FIXED_EVENT`)
