-- Table: availability_windows
CREATE TABLE availability_windows (
	id UUID DEFAULT gen_random_uuid() NOT NULL, 
	daily_plan_id UUID NOT NULL, 
	available_start_at TIMESTAMP WITH TIME ZONE NOT NULL, 
	available_end_at TIMESTAMP WITH TIME ZONE NOT NULL, 
	created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	updated_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	PRIMARY KEY (id), 
	CONSTRAINT availability_windows_range_valid CHECK (available_end_at > available_start_at), 
	CONSTRAINT availability_windows_unique UNIQUE (daily_plan_id, available_start_at, available_end_at), 
	FOREIGN KEY(daily_plan_id) REFERENCES daily_plans (id) ON DELETE CASCADE
);
CREATE INDEX availability_windows_plan_start_idx ON availability_windows (daily_plan_id, available_start_at);
DROP TRIGGER IF EXISTS availability_windows_set_updated_at ON availability_windows;
CREATE TRIGGER availability_windows_set_updated_at
    BEFORE UPDATE ON availability_windows
    FOR EACH ROW EXECUTE FUNCTION set_row_updated_at();
