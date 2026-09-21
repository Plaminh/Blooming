-- Table: focus_run_events
CREATE TABLE focus_run_events (
	id UUID DEFAULT gen_random_uuid() NOT NULL, 
	focus_run_id UUID NOT NULL, 
	event_type VARCHAR(30) NOT NULL, 
	occurred_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	payload JSONB, 
	PRIMARY KEY (id), 
	CONSTRAINT focus_run_events_type_valid CHECK (event_type IN ('STARTED', 'PAUSED', 'RESUMED', 'ENDED', 'OUTCOME_RECORDED')), 
	CONSTRAINT focus_run_events_payload_object CHECK (payload IS NULL OR jsonb_typeof(payload) = 'object'), 
	FOREIGN KEY(focus_run_id) REFERENCES focus_runs (id) ON DELETE CASCADE
);
CREATE INDEX focus_run_events_run_chronological_idx ON focus_run_events (focus_run_id, occurred_at, id);
