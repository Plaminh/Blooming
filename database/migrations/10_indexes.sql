-- Scope: uniqueness and indexes for Blooming's expected access patterns.

-- Account lookup is case-insensitive without requiring the citext extension.
CREATE UNIQUE INDEX IF NOT EXISTS users_email_lower_unique_idx
    ON users (LOWER(email));

CREATE INDEX IF NOT EXISTS auth_sessions_user_active_idx
    ON auth_sessions (user_id, expires_at)
    WHERE revoked_at IS NULL;

CREATE INDEX IF NOT EXISTS goals_user_status_idx
    ON goals (user_id, status, target_date);

CREATE INDEX IF NOT EXISTS milestones_goal_due_idx
    ON milestones (goal_id, due_at);

CREATE INDEX IF NOT EXISTS planning_sessions_user_recent_idx
    ON planning_sessions (user_id, created_at DESC);

CREATE INDEX IF NOT EXISTS planning_messages_session_chronological_idx
    ON planning_messages (planning_session_id, created_at, id);

CREATE INDEX IF NOT EXISTS tasks_user_status_deadline_idx
    ON tasks (user_id, status, deadline_at);

CREATE INDEX IF NOT EXISTS tasks_milestone_idx
    ON tasks (milestone_id)
    WHERE milestone_id IS NOT NULL;

CREATE INDEX IF NOT EXISTS task_dependencies_prerequisite_idx
    ON task_dependencies (depends_on_task_id);

CREATE INDEX IF NOT EXISTS availability_windows_plan_start_idx
    ON availability_windows (daily_plan_id, available_start_at);

CREATE INDEX IF NOT EXISTS plan_blocks_plan_timeline_idx
    ON plan_blocks (daily_plan_id, planned_start_at, planned_end_at);

CREATE INDEX IF NOT EXISTS plan_blocks_task_idx
    ON plan_blocks (task_id)
    WHERE task_id IS NOT NULL;

CREATE INDEX IF NOT EXISTS plan_revisions_plan_recent_idx
    ON plan_revisions (daily_plan_id, revision_number DESC);

CREATE INDEX IF NOT EXISTS focus_runs_user_recent_idx
    ON focus_runs (user_id, created_at DESC);

CREATE INDEX IF NOT EXISTS focus_runs_user_active_idx
    ON focus_runs (user_id, status)
    WHERE status IN ('READY', 'FOCUSING', 'PAUSED');

CREATE INDEX IF NOT EXISTS focus_runs_task_idx
    ON focus_runs (task_id)
    WHERE task_id IS NOT NULL;

CREATE INDEX IF NOT EXISTS focus_runs_plan_block_idx
    ON focus_runs (plan_block_id)
    WHERE plan_block_id IS NOT NULL;

CREATE INDEX IF NOT EXISTS focus_run_events_run_chronological_idx
    ON focus_run_events (focus_run_id, occurred_at, id);

CREATE INDEX IF NOT EXISTS reminders_user_sync_idx
    ON reminders (user_id, due_at)
    WHERE status IN ('SCHEDULED', 'DUE');

CREATE INDEX IF NOT EXISTS reminders_user_unread_due_idx
    ON reminders (user_id, due_at)
    WHERE status = 'DUE' AND viewed_at IS NULL;

CREATE INDEX IF NOT EXISTS reminders_milestone_idx
    ON reminders (milestone_id)
    WHERE milestone_id IS NOT NULL;

CREATE INDEX IF NOT EXISTS reminders_plan_block_idx
    ON reminders (plan_block_id)
    WHERE plan_block_id IS NOT NULL;

CREATE INDEX IF NOT EXISTS reminder_actions_reminder_recent_idx
    ON reminder_actions (reminder_id, created_at DESC);

CREATE INDEX IF NOT EXISTS reward_events_user_chronological_idx
    ON reward_events (user_id, created_at, id);

CREATE INDEX IF NOT EXISTS reward_events_focus_run_idx
    ON reward_events (source_focus_run_id)
    WHERE source_focus_run_id IS NOT NULL;

CREATE INDEX IF NOT EXISTS reward_events_task_idx
    ON reward_events (source_task_id)
    WHERE source_task_id IS NOT NULL;

CREATE INDEX IF NOT EXISTS reward_events_milestone_idx
    ON reward_events (source_milestone_id)
    WHERE source_milestone_id IS NOT NULL;

CREATE INDEX IF NOT EXISTS reward_events_plan_revision_idx
    ON reward_events (source_plan_revision_id)
    WHERE source_plan_revision_id IS NOT NULL;

