-- Table: plan_revisions
CREATE TABLE plan_revisions (
	id UUID DEFAULT gen_random_uuid() NOT NULL, 
	daily_plan_id UUID NOT NULL, 
	revision_number INTEGER NOT NULL, 
	reason TEXT NOT NULL, 
	trigger_type VARCHAR(30) NOT NULL, 
	generated_by VARCHAR(20) NOT NULL, 
	before_snapshot JSONB NOT NULL, 
	after_snapshot JSONB NOT NULL, 
	created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	PRIMARY KEY (id), 
	CONSTRAINT plan_revisions_number_valid CHECK (revision_number >= 1), 
	CONSTRAINT plan_revisions_reason_not_blank CHECK (BTRIM(reason) <> ''), 
	CONSTRAINT plan_revisions_trigger_valid CHECK (trigger_type IN ('MANUAL_EDIT', 'DELAY', 'NEED_MORE_TIME', 'SKIP', 'CONFLICT', 'RECOVERY')), 
	CONSTRAINT plan_revisions_generated_by_valid CHECK (generated_by IN ('USER', 'SYSTEM', 'AI')), 
	CONSTRAINT plan_revisions_before_object CHECK (jsonb_typeof(before_snapshot) = 'object'), 
	CONSTRAINT plan_revisions_after_object CHECK (jsonb_typeof(after_snapshot) = 'object'), 
	CONSTRAINT plan_revisions_number_unique UNIQUE (daily_plan_id, revision_number), 
	FOREIGN KEY(daily_plan_id) REFERENCES daily_plans (id) ON DELETE CASCADE
);
CREATE INDEX plan_revisions_plan_recent_idx ON plan_revisions (daily_plan_id, revision_number DESC);
