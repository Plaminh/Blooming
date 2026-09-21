-- Table: email_verification_tokens
CREATE TABLE email_verification_tokens (
	id UUID DEFAULT gen_random_uuid() NOT NULL, 
	user_id UUID NOT NULL, 
	token_hash VARCHAR(64) NOT NULL, 
	expires_at TIMESTAMP WITH TIME ZONE NOT NULL, 
	used_at TIMESTAMP WITH TIME ZONE, 
	created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	PRIMARY KEY (id), 
	CONSTRAINT email_verification_tokens_token_hash_key UNIQUE (token_hash), 
	CONSTRAINT email_verification_tokens_expiry_valid CHECK (expires_at > created_at), 
	FOREIGN KEY(user_id) REFERENCES users (id) ON DELETE CASCADE
);
CREATE INDEX email_verification_tokens_user_active_idx ON email_verification_tokens (user_id, expires_at) WHERE used_at IS NULL;
