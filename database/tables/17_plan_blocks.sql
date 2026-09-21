-- Table: plan_blocks
CREATE TABLE plan_blocks (
	id UUID DEFAULT gen_random_uuid() NOT NULL, 
	daily_plan_id UUID NOT NULL, 
	task_id UUID, 
	block_type VARCHAR(20) NOT NULL, 
	title VARCHAR(200), 
	planned_start_at TIMESTAMP WITH TIME ZONE NOT NULL, 
	planned_end_at TIMESTAMP WITH TIME ZONE NOT NULL, 
	position INTEGER NOT NULL, 
	status VARCHAR(20) DEFAULT 'PLANNED' NOT NULL, 
	is_locked BOOLEAN DEFAULT FALSE NOT NULL, 
	created_by VARCHAR(20) DEFAULT 'SCHEDULER' NOT NULL, 
	completed_at TIMESTAMP WITH TIME ZONE, 
	created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	updated_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	PRIMARY KEY (id), 
	CONSTRAINT plan_blocks_type_valid CHECK (block_type IN ('TASK', 'BREAK', 'BUFFER', 'FIXED_EVENT')), 
	CONSTRAINT plan_blocks_range_valid CHECK (planned_end_at > planned_start_at), 
	CONSTRAINT plan_blocks_position_valid CHECK (position >= 0), 
	CONSTRAINT plan_blocks_status_valid CHECK (status IN ('PLANNED', 'ACTIVE', 'COMPLETED', 'SKIPPED', 'CANCELLED')), 
	CONSTRAINT plan_blocks_creator_valid CHECK (created_by IN ('SCHEDULER', 'USER')), 
	CONSTRAINT plan_blocks_task_link_valid CHECK ((block_type = 'TASK' AND task_id IS NOT NULL) OR (block_type <> 'TASK' AND task_id IS NULL)), 
	CONSTRAINT plan_blocks_non_task_title CHECK (block_type = 'TASK' OR (title IS NOT NULL AND BTRIM(title) <> '')), 
	CONSTRAINT plan_blocks_completion_valid CHECK ((status = 'COMPLETED' AND completed_at IS NOT NULL) OR (status <> 'COMPLETED')), 
	CONSTRAINT plan_blocks_position_unique UNIQUE (daily_plan_id, position), 
	FOREIGN KEY(daily_plan_id) REFERENCES daily_plans (id) ON DELETE CASCADE, 
	FOREIGN KEY(task_id) REFERENCES tasks (id) ON DELETE CASCADE
);
CREATE INDEX plan_blocks_task_idx ON plan_blocks (task_id) WHERE task_id IS NOT NULL;
CREATE INDEX plan_blocks_plan_timeline_idx ON plan_blocks (daily_plan_id, planned_start_at, planned_end_at);
DROP TRIGGER IF EXISTS plan_blocks_set_updated_at ON plan_blocks;
CREATE TRIGGER plan_blocks_set_updated_at
    BEFORE UPDATE ON plan_blocks
    FOR EACH ROW EXECUTE FUNCTION set_row_updated_at();
