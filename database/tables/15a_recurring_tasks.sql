-- Table: recurring_tasks
-- A repeating task template. Concrete daily tasks are created from it when a
-- day is planned; the template itself is never scheduled.
CREATE TABLE recurring_tasks (
	id UUID DEFAULT gen_random_uuid() NOT NULL, 
	user_id UUID NOT NULL, 
	title VARCHAR(200) NOT NULL, 
	estimated_duration_minutes INTEGER NOT NULL, 
	priority VARCHAR(20) DEFAULT 'MEDIUM' NOT NULL, 
	importance VARCHAR(20) DEFAULT 'CORE' NOT NULL, 
	category VARCHAR(50), 
	frequency VARCHAR(10) NOT NULL, 
	-- Bit i set = repeats on weekday i (0 = Monday ... 6 = Sunday). Ignored for DAILY.
	weekday_mask SMALLINT DEFAULT 0 NOT NULL, 
	fixed_start_time TIME WITHOUT TIME ZONE, 
	start_date DATE NOT NULL, 
	until_date DATE, 
	is_active BOOLEAN DEFAULT TRUE NOT NULL, 
	created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	updated_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	PRIMARY KEY (id), 
	CONSTRAINT recurring_tasks_title_not_blank CHECK (BTRIM(title) <> ''), 
	CONSTRAINT recurring_tasks_duration_valid CHECK (estimated_duration_minutes BETWEEN 5 AND 480), 
	CONSTRAINT recurring_tasks_priority_valid CHECK (priority IN ('LOW', 'MEDIUM', 'HIGH', 'URGENT')), 
	CONSTRAINT recurring_tasks_importance_valid CHECK (importance IN ('CORE', 'OPTIONAL')), 
	CONSTRAINT recurring_tasks_category_valid CHECK (category IS NULL OR category IN ('Learning', 'Work', 'Personal')), 
	CONSTRAINT recurring_tasks_frequency_valid CHECK (frequency IN ('DAILY', 'WEEKLY')), 
	CONSTRAINT recurring_tasks_weekday_mask_valid CHECK (weekday_mask BETWEEN 0 AND 127 AND (frequency = 'DAILY' OR weekday_mask > 0)), 
	CONSTRAINT recurring_tasks_until_valid CHECK (until_date IS NULL OR until_date >= start_date), 
	FOREIGN KEY(user_id) REFERENCES users (id) ON DELETE CASCADE
);
CREATE INDEX recurring_tasks_user_active_idx ON recurring_tasks (user_id) WHERE is_active;
DROP TRIGGER IF EXISTS recurring_tasks_set_updated_at ON recurring_tasks;
CREATE TRIGGER recurring_tasks_set_updated_at
    BEFORE UPDATE ON recurring_tasks
    FOR EACH ROW EXECUTE FUNCTION set_row_updated_at();
