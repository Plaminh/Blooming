-- Table: focus_runs
CREATE TABLE focus_runs (
	id UUID DEFAULT gen_random_uuid() NOT NULL, 
	user_id UUID NOT NULL, 
	task_id UUID, 
	plan_block_id UUID, 
	quick_task_title VARCHAR(200), 
	status VARCHAR(20) DEFAULT 'READY' NOT NULL, 
	outcome VARCHAR(30), 
	planned_focus_seconds INTEGER NOT NULL, 
	planned_break_seconds INTEGER DEFAULT 0 NOT NULL, 
	started_at TIMESTAMP WITH TIME ZONE, 
	expected_end_at TIMESTAMP WITH TIME ZONE, 
	paused_at TIMESTAMP WITH TIME ZONE, 
	total_paused_seconds INTEGER DEFAULT 0 NOT NULL, 
	ended_at TIMESTAMP WITH TIME ZONE, 
	actual_duration_seconds INTEGER, 
	created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	updated_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	PRIMARY KEY (id), 
	CONSTRAINT focus_runs_subject_valid CHECK (task_id IS NOT NULL OR (quick_task_title IS NOT NULL AND BTRIM(quick_task_title) <> '')), 
	CONSTRAINT focus_runs_status_valid CHECK (status IN ('READY', 'FOCUSING', 'PAUSED', 'ENDED')), 
	CONSTRAINT focus_runs_outcome_valid CHECK (outcome IS NULL OR outcome IN ('DONE', 'NEED_MORE_TIME', 'SKIP', 'FINISHED_EARLY')), 
	CONSTRAINT focus_runs_focus_duration_valid CHECK (planned_focus_seconds BETWEEN 1 AND 86400), 
	CONSTRAINT focus_runs_break_duration_valid CHECK (planned_break_seconds BETWEEN 0 AND 21600), 
	CONSTRAINT focus_runs_pause_duration_valid CHECK (total_paused_seconds >= 0), 
	CONSTRAINT focus_runs_actual_duration_valid CHECK (actual_duration_seconds IS NULL OR actual_duration_seconds >= 0), 
	CONSTRAINT focus_runs_expected_end_valid CHECK (started_at IS NULL OR expected_end_at IS NULL OR expected_end_at >= started_at), 
	CONSTRAINT focus_runs_end_valid CHECK (ended_at IS NULL OR (started_at IS NOT NULL AND ended_at >= started_at)), 
	CONSTRAINT focus_runs_ended_state_valid CHECK (status <> 'ENDED' OR (ended_at IS NOT NULL AND actual_duration_seconds IS NOT NULL)), 
	FOREIGN KEY(user_id) REFERENCES users (id) ON DELETE CASCADE, 
	FOREIGN KEY(task_id) REFERENCES tasks (id) ON DELETE CASCADE, 
	FOREIGN KEY(plan_block_id) REFERENCES plan_blocks (id) ON DELETE SET NULL
);
CREATE INDEX focus_runs_plan_block_idx ON focus_runs (plan_block_id) WHERE plan_block_id IS NOT NULL;
CREATE INDEX focus_runs_task_idx ON focus_runs (task_id) WHERE task_id IS NOT NULL;
CREATE INDEX focus_runs_user_recent_idx ON focus_runs (user_id, created_at DESC);
CREATE INDEX focus_runs_user_active_idx ON focus_runs (user_id, status) WHERE status IN ('READY', 'FOCUSING', 'PAUSED');
CREATE INDEX idx_focus_runs_user_status ON focus_runs (user_id, status);
DROP TRIGGER IF EXISTS focus_runs_set_updated_at ON focus_runs;
CREATE TRIGGER focus_runs_set_updated_at
    BEFORE UPDATE ON focus_runs
    FOR EACH ROW EXECUTE FUNCTION set_row_updated_at();
