-- Table: daily_plans
CREATE TABLE daily_plans (
	id UUID DEFAULT gen_random_uuid() NOT NULL, 
	user_id UUID NOT NULL, 
	planning_session_id UUID, 
	plan_date DATE NOT NULL, 
	status VARCHAR(20) DEFAULT 'DRAFT' NOT NULL, 
	reality_check VARCHAR(20), 
	timezone_snapshot VARCHAR(64) NOT NULL, 
	confirmed_at TIMESTAMP WITH TIME ZONE, 
	completed_at TIMESTAMP WITH TIME ZONE, 
	created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	updated_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	PRIMARY KEY (id), 
	CONSTRAINT daily_plans_status_valid CHECK (status IN ('DRAFT', 'CONFIRMED', 'ACTIVE', 'COMPLETED', 'ARCHIVED')), 
	CONSTRAINT daily_plans_reality_check_valid CHECK (reality_check IS NULL OR reality_check IN ('COMFORTABLE', 'TIGHT', 'OVERLOADED')), 
	CONSTRAINT daily_plans_timezone_not_blank CHECK (BTRIM(timezone_snapshot) <> ''), 
	CONSTRAINT daily_plans_confirmation_valid CHECK (status = 'DRAFT' OR confirmed_at IS NOT NULL), 
	CONSTRAINT daily_plans_completion_valid CHECK ((status = 'COMPLETED' AND completed_at IS NOT NULL) OR (status <> 'COMPLETED')), 
	FOREIGN KEY(user_id) REFERENCES users (id) ON DELETE CASCADE, 
	FOREIGN KEY(planning_session_id) REFERENCES planning_sessions (id) ON DELETE SET NULL
);
CREATE UNIQUE INDEX daily_plans_one_active_per_local_date ON daily_plans (user_id, plan_date) WHERE status IN ('DRAFT', 'CONFIRMED', 'ACTIVE');
DROP TRIGGER IF EXISTS daily_plans_set_updated_at ON daily_plans;
CREATE TRIGGER daily_plans_set_updated_at
    BEFORE UPDATE ON daily_plans
    FOR EACH ROW EXECUTE FUNCTION set_row_updated_at();
