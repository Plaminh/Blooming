-- Table: ai_usage_log
CREATE TABLE ai_usage_log (
	id BIGSERIAL NOT NULL, 
	user_id UUID, 
	created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	purpose VARCHAR(20) NOT NULL, 
	provider VARCHAR(20) NOT NULL, 
	model VARCHAR(80) NOT NULL, 
	prompt_tokens INTEGER, 
	completion_tokens INTEGER, 
	latency_ms INTEGER, 
	outcome VARCHAR(20) NOT NULL, 
	PRIMARY KEY (id), 
	FOREIGN KEY(user_id) REFERENCES users (id) ON DELETE SET NULL
);
CREATE INDEX ai_usage_user_recent_idx ON ai_usage_log (user_id, created_at DESC);
CREATE INDEX ai_usage_recent_idx ON ai_usage_log (created_at DESC);
