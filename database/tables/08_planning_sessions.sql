-- Table: planning_sessions
CREATE TABLE planning_sessions (
	id UUID DEFAULT gen_random_uuid() NOT NULL, 
	user_id UUID NOT NULL, 
	session_type VARCHAR(20) NOT NULL, 
	status VARCHAR(30) DEFAULT 'OPEN' NOT NULL, 
	context_date DATE, 
	pending_intent VARCHAR(30), 
	closed_at TIMESTAMP WITH TIME ZONE, 
	created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	updated_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	PRIMARY KEY (id), 
	CONSTRAINT planning_sessions_type_valid CHECK (session_type IN ('DAILY_PLAN', 'PLAN_EDIT', 'REPLAN', 'ROADMAP')), 
	CONSTRAINT planning_sessions_status_valid CHECK (status IN ('OPEN', 'AWAITING_CLARIFICATION', 'COMPLETED', 'CANCELLED')), 
	CONSTRAINT planning_sessions_closed_at_valid CHECK (closed_at IS NULL OR closed_at >= created_at), 
	FOREIGN KEY(user_id) REFERENCES users (id) ON DELETE CASCADE
);
CREATE INDEX planning_sessions_user_recent_idx ON planning_sessions (user_id, created_at DESC);
DROP TRIGGER IF EXISTS planning_sessions_set_updated_at ON planning_sessions;
CREATE TRIGGER planning_sessions_set_updated_at
    BEFORE UPDATE ON planning_sessions
    FOR EACH ROW EXECUTE FUNCTION set_row_updated_at();
