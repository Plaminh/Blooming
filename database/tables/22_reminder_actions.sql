-- Table: reminder_actions
CREATE TABLE reminder_actions (
	id UUID DEFAULT gen_random_uuid() NOT NULL, 
	reminder_id UUID NOT NULL, 
	action_type VARCHAR(30) NOT NULL, 
	previous_due_at TIMESTAMP WITH TIME ZONE, 
	new_due_at TIMESTAMP WITH TIME ZONE, 
	payload JSONB, 
	created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	PRIMARY KEY (id), 
	CONSTRAINT reminder_actions_type_valid CHECK (action_type IN ('VIEWED', 'START_FOCUS', 'REMIND_LATER', 'OPEN_BLOOMING', 'CREATE_PLAN', 'MARK_COMPLETED', 'MOVE_MILESTONE', 'DISMISS', 'COMPLETE')), 
	CONSTRAINT reminder_actions_snooze_time_valid CHECK (action_type <> 'REMIND_LATER' OR (new_due_at IS NOT NULL AND previous_due_at IS NOT NULL AND new_due_at > previous_due_at)), 
	CONSTRAINT reminder_actions_payload_object CHECK (payload IS NULL OR jsonb_typeof(payload) = 'object'), 
	FOREIGN KEY(reminder_id) REFERENCES reminders (id) ON DELETE CASCADE
);
CREATE INDEX reminder_actions_reminder_recent_idx ON reminder_actions (reminder_id, created_at DESC);
