-- Table: milestones
CREATE TABLE milestones (
	id UUID DEFAULT gen_random_uuid() NOT NULL, 
	goal_id UUID NOT NULL, 
	title VARCHAR(200) NOT NULL, 
	description TEXT, 
	expected_outcome TEXT, 
	due_at TIMESTAMP WITH TIME ZONE, 
	position INTEGER NOT NULL, 
	status VARCHAR(20) DEFAULT 'PENDING' NOT NULL, 
	completed_at TIMESTAMP WITH TIME ZONE, 
	created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	updated_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	PRIMARY KEY (id), 
	CONSTRAINT milestones_title_not_blank CHECK (BTRIM(title) <> ''), 
	CONSTRAINT milestones_position_valid CHECK (position >= 0), 
	CONSTRAINT milestones_status_valid CHECK (status IN ('PENDING', 'IN_PROGRESS', 'COMPLETED', 'SKIPPED', 'CANCELLED')), 
	CONSTRAINT milestones_completion_valid CHECK ((status = 'COMPLETED' AND completed_at IS NOT NULL) OR (status <> 'COMPLETED')), 
	CONSTRAINT milestones_goal_position_unique UNIQUE (goal_id, position), 
	FOREIGN KEY(goal_id) REFERENCES goals (id) ON DELETE CASCADE
);
CREATE INDEX milestones_goal_due_idx ON milestones (goal_id, due_at);
DROP TRIGGER IF EXISTS milestones_set_updated_at ON milestones;
CREATE TRIGGER milestones_set_updated_at
    BEFORE UPDATE ON milestones
    FOR EACH ROW EXECUTE FUNCTION set_row_updated_at();
