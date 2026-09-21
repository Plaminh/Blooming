-- Table: tasks
CREATE TABLE tasks (
	id UUID DEFAULT gen_random_uuid() NOT NULL, 
	user_id UUID NOT NULL, 
	milestone_id UUID, 
	title VARCHAR(200) NOT NULL, 
	description TEXT, 
	category VARCHAR(50), 
	estimated_duration_minutes INTEGER NOT NULL, 
	priority VARCHAR(20) DEFAULT 'MEDIUM' NOT NULL, 
	importance VARCHAR(20) DEFAULT 'CORE' NOT NULL, 
	scheduling_type VARCHAR(20) DEFAULT 'FLEXIBLE' NOT NULL, 
	source VARCHAR(20) DEFAULT 'MANUAL' NOT NULL, 
	status VARCHAR(20) DEFAULT 'DRAFT' NOT NULL, 
	deadline_at TIMESTAMP WITH TIME ZONE, 
	is_splittable BOOLEAN DEFAULT FALSE NOT NULL, 
	min_split_duration_minutes INTEGER, 
	preferred_break_duration_minutes INTEGER, 
	fixed_start_at TIMESTAMP WITH TIME ZONE, 
	fixed_end_at TIMESTAMP WITH TIME ZONE, 
	completed_at TIMESTAMP WITH TIME ZONE, 
	created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	updated_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	PRIMARY KEY (id), 
	CONSTRAINT tasks_title_not_blank CHECK (BTRIM(title) <> ''), 
	CONSTRAINT tasks_duration_valid CHECK (estimated_duration_minutes BETWEEN 1 AND 10080), 
	CONSTRAINT tasks_priority_valid CHECK (priority IN ('LOW', 'MEDIUM', 'HIGH', 'URGENT')), 
	CONSTRAINT tasks_importance_valid CHECK (importance IN ('CORE', 'OPTIONAL')), 
	CONSTRAINT tasks_scheduling_type_valid CHECK (scheduling_type IN ('FLEXIBLE', 'FIXED')), 
	CONSTRAINT tasks_source_valid CHECK (source IN ('MANUAL', 'AI', 'MILESTONE', 'QUICK')), 
	CONSTRAINT tasks_status_valid CHECK (status IN ('DRAFT', 'PENDING', 'IN_PROGRESS', 'COMPLETED', 'SKIPPED', 'CANCELLED')), 
	CONSTRAINT tasks_category_valid CHECK (category IS NULL OR category IN ('Learning', 'Work', 'Personal')), 
	CONSTRAINT tasks_scheduling_window_valid CHECK ((scheduling_type = 'FIXED' AND fixed_start_at IS NOT NULL AND fixed_end_at IS NOT NULL AND fixed_end_at > fixed_start_at) OR (scheduling_type = 'FLEXIBLE' AND fixed_start_at IS NULL AND fixed_end_at IS NULL)), 
	CONSTRAINT tasks_completion_valid CHECK ((status = 'COMPLETED' AND completed_at IS NOT NULL) OR (status <> 'COMPLETED')), 
	CONSTRAINT tasks_min_split_duration_valid CHECK (min_split_duration_minutes IS NULL OR min_split_duration_minutes > 0), 
	CONSTRAINT tasks_preferred_break_duration_valid CHECK (preferred_break_duration_minutes IS NULL OR preferred_break_duration_minutes > 0), 
	CONSTRAINT tasks_min_split_duration_limit CHECK (min_split_duration_minutes IS NULL OR min_split_duration_minutes <= estimated_duration_minutes), 
	FOREIGN KEY(user_id) REFERENCES users (id) ON DELETE CASCADE, 
	FOREIGN KEY(milestone_id) REFERENCES milestones (id) ON DELETE SET NULL
);
CREATE INDEX tasks_milestone_idx ON tasks (milestone_id) WHERE milestone_id IS NOT NULL;
CREATE INDEX tasks_user_status_deadline_idx ON tasks (user_id, status, deadline_at);
DROP TRIGGER IF EXISTS tasks_set_updated_at ON tasks;
CREATE TRIGGER tasks_set_updated_at
    BEFORE UPDATE ON tasks
    FOR EACH ROW EXECUTE FUNCTION set_row_updated_at();
