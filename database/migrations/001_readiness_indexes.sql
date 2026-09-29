CREATE INDEX IF NOT EXISTS idx_focus_runs_user_status
    ON focus_runs (user_id, status);

CREATE INDEX IF NOT EXISTS idx_reminders_user_status_due
    ON reminders (user_id, status, due_at);
