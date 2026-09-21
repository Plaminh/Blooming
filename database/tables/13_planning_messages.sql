-- Table: planning_messages
CREATE TABLE planning_messages (
	id UUID DEFAULT gen_random_uuid() NOT NULL, 
	planning_session_id UUID NOT NULL, 
	role VARCHAR(20) NOT NULL, 
	content TEXT NOT NULL, 
	structured_payload JSONB, 
	created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	PRIMARY KEY (id), 
	CONSTRAINT planning_messages_role_valid CHECK (role IN ('USER', 'ASSISTANT', 'SYSTEM')), 
	CONSTRAINT planning_messages_content_not_blank CHECK (BTRIM(content) <> ''), 
	CONSTRAINT planning_messages_payload_object CHECK (structured_payload IS NULL OR jsonb_typeof(structured_payload) = 'object'), 
	FOREIGN KEY(planning_session_id) REFERENCES planning_sessions (id) ON DELETE CASCADE
);
CREATE INDEX planning_messages_session_chronological_idx ON planning_messages (planning_session_id, created_at, id);
