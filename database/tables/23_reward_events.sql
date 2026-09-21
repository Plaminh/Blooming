-- Table: reward_events
CREATE TABLE reward_events (
	id UUID DEFAULT gen_random_uuid() NOT NULL, 
	user_id UUID NOT NULL, 
	event_type VARCHAR(40) NOT NULL, 
	resource_type VARCHAR(20) NOT NULL, 
	amount INTEGER NOT NULL, 
	idempotency_key TEXT NOT NULL, 
	source_focus_run_id UUID, 
	source_task_id UUID, 
	source_milestone_id UUID, 
	source_plan_revision_id UUID, 
	metadata JSONB, 
	created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	PRIMARY KEY (id), 
	CONSTRAINT reward_events_idempotency_key_key UNIQUE (idempotency_key), 
	CONSTRAINT reward_events_type_valid CHECK (event_type IN ('FOCUS_COMPLETED', 'TASK_COMPLETED', 'CORE_OBJECTIVE_COMPLETED', 'MILESTONE_COMPLETED', 'RECOVERY_PLAN_COMPLETED', 'PLANT_UNLOCK', 'WATER_PLANT')), 
	CONSTRAINT reward_events_resource_type_valid CHECK (resource_type IN ('WATER', 'LEAVES')), 
	CONSTRAINT reward_events_idempotency_key_not_blank CHECK (BTRIM(idempotency_key) <> ''), 
	CONSTRAINT reward_events_max_one_source CHECK (num_nonnulls(source_focus_run_id, source_task_id, source_milestone_id, source_plan_revision_id) <= 1), 
	CONSTRAINT reward_events_metadata_object CHECK (metadata IS NULL OR jsonb_typeof(metadata) = 'object'), 
	FOREIGN KEY(user_id) REFERENCES users (id) ON DELETE CASCADE, 
	FOREIGN KEY(source_focus_run_id) REFERENCES focus_runs (id) ON DELETE CASCADE, 
	FOREIGN KEY(source_task_id) REFERENCES tasks (id) ON DELETE CASCADE, 
	FOREIGN KEY(source_milestone_id) REFERENCES milestones (id) ON DELETE CASCADE, 
	FOREIGN KEY(source_plan_revision_id) REFERENCES plan_revisions (id) ON DELETE CASCADE
);
CREATE INDEX reward_events_milestone_idx ON reward_events (source_milestone_id) WHERE source_milestone_id IS NOT NULL;
CREATE INDEX reward_events_task_idx ON reward_events (source_task_id) WHERE source_task_id IS NOT NULL;
CREATE INDEX reward_events_user_chronological_idx ON reward_events (user_id, created_at, id);
CREATE INDEX reward_events_plan_revision_idx ON reward_events (source_plan_revision_id) WHERE source_plan_revision_id IS NOT NULL;
CREATE INDEX reward_events_focus_run_idx ON reward_events (source_focus_run_id) WHERE source_focus_run_id IS NOT NULL;
