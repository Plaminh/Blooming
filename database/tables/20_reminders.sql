-- Table: reminders
CREATE TABLE reminders (
	id UUID DEFAULT gen_random_uuid() NOT NULL, 
	user_id UUID NOT NULL, 
	milestone_id UUID, 
	plan_block_id UUID, 
	reminder_type VARCHAR(30) NOT NULL, 
	message VARCHAR(300) NOT NULL, 
	due_at TIMESTAMP WITH TIME ZONE NOT NULL, 
	original_due_at TIMESTAMP WITH TIME ZONE NOT NULL, 
	status VARCHAR(20) DEFAULT 'SCHEDULED' NOT NULL, 
	viewed_at TIMESTAMP WITH TIME ZONE, 
	completed_at TIMESTAMP WITH TIME ZONE, 
	dismissed_at TIMESTAMP WITH TIME ZONE, 
	created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	updated_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	PRIMARY KEY (id), 
	CONSTRAINT reminders_type_valid CHECK (reminder_type IN ('PLAN_BLOCK_START', 'MILESTONE_DUE', 'CUSTOM')), 
	CONSTRAINT reminders_message_not_blank CHECK (BTRIM(message) <> ''), 
	CONSTRAINT reminders_status_valid CHECK (status IN ('SCHEDULED', 'DUE', 'COMPLETED', 'DISMISSED', 'CANCELLED')), 
	CONSTRAINT reminders_target_valid CHECK ((reminder_type = 'PLAN_BLOCK_START' AND plan_block_id IS NOT NULL AND milestone_id IS NULL) OR (reminder_type = 'MILESTONE_DUE' AND milestone_id IS NOT NULL AND plan_block_id IS NULL) OR (reminder_type = 'CUSTOM' AND milestone_id IS NULL AND plan_block_id IS NULL)), 
	CONSTRAINT reminders_completion_valid CHECK ((status = 'COMPLETED' AND completed_at IS NOT NULL) OR status <> 'COMPLETED'), 
	CONSTRAINT reminders_dismissal_valid CHECK ((status = 'DISMISSED' AND dismissed_at IS NOT NULL) OR status <> 'DISMISSED'), 
	FOREIGN KEY(user_id) REFERENCES users (id) ON DELETE CASCADE, 
	FOREIGN KEY(milestone_id) REFERENCES milestones (id) ON DELETE CASCADE, 
	FOREIGN KEY(plan_block_id) REFERENCES plan_blocks (id) ON DELETE CASCADE
);
CREATE INDEX reminders_plan_block_idx ON reminders (plan_block_id) WHERE plan_block_id IS NOT NULL;
CREATE INDEX reminders_user_unread_due_idx ON reminders (user_id, due_at) WHERE status = 'DUE' AND viewed_at IS NULL;
CREATE INDEX reminders_milestone_idx ON reminders (milestone_id) WHERE milestone_id IS NOT NULL;
CREATE INDEX reminders_user_sync_idx ON reminders (user_id, due_at) WHERE status IN ('SCHEDULED', 'DUE');
DROP TRIGGER IF EXISTS reminders_set_updated_at ON reminders;
CREATE TRIGGER reminders_set_updated_at
    BEFORE UPDATE ON reminders
    FOR EACH ROW EXECUTE FUNCTION set_row_updated_at();
