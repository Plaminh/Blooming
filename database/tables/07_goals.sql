-- Table: goals
CREATE TABLE goals (
	id UUID DEFAULT gen_random_uuid() NOT NULL, 
	user_id UUID NOT NULL, 
	title VARCHAR(200) NOT NULL, 
	description TEXT, 
	roadmap_summary TEXT, 
	target_date DATE, 
	source_idempotency_key VARCHAR(200),
	status VARCHAR(20) DEFAULT 'DRAFT' NOT NULL, 
	completed_at TIMESTAMP WITH TIME ZONE, 
	created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	updated_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	PRIMARY KEY (id), 
	CONSTRAINT goals_title_not_blank CHECK (BTRIM(title) <> ''), 
	CONSTRAINT goals_status_valid CHECK (status IN ('DRAFT', 'ACTIVE', 'ON_HOLD', 'COMPLETED', 'CANCELLED')), 
	CONSTRAINT goals_completion_valid CHECK ((status = 'COMPLETED' AND completed_at IS NOT NULL) OR (status <> 'COMPLETED')), 
	FOREIGN KEY(user_id) REFERENCES users (id) ON DELETE CASCADE
);
CREATE INDEX goals_user_status_idx ON goals (user_id, status, target_date);
CREATE UNIQUE INDEX goals_user_idempotency_idx ON goals (user_id, source_idempotency_key)
    WHERE source_idempotency_key IS NOT NULL;
DROP TRIGGER IF EXISTS goals_set_updated_at ON goals;
CREATE TRIGGER goals_set_updated_at
    BEFORE UPDATE ON goals
    FOR EACH ROW EXECUTE FUNCTION set_row_updated_at();
