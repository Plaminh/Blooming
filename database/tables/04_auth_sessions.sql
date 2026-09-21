-- Table: auth_sessions
CREATE TABLE auth_sessions (
	id UUID DEFAULT gen_random_uuid() NOT NULL, 
	user_id UUID NOT NULL, 
	refresh_token_hash TEXT NOT NULL, 
	device_name VARCHAR(120), 
	platform VARCHAR(20), 
	expires_at TIMESTAMP WITH TIME ZONE NOT NULL, 
	last_used_at TIMESTAMP WITH TIME ZONE, 
	revoked_at TIMESTAMP WITH TIME ZONE, 
	created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	updated_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	PRIMARY KEY (id), 
	CONSTRAINT auth_sessions_refresh_token_hash_key UNIQUE (refresh_token_hash), 
	CONSTRAINT auth_sessions_platform_valid CHECK (platform IS NULL OR platform IN ('WINDOWS', 'LINUX', 'OTHER')), 
	CONSTRAINT auth_sessions_expiry_valid CHECK (expires_at > created_at), 
	CONSTRAINT auth_sessions_revocation_valid CHECK (revoked_at IS NULL OR revoked_at >= created_at), 
	FOREIGN KEY(user_id) REFERENCES users (id) ON DELETE CASCADE
);
CREATE INDEX auth_sessions_user_active_idx ON auth_sessions (user_id, expires_at) WHERE revoked_at IS NULL;
DROP TRIGGER IF EXISTS auth_sessions_set_updated_at ON auth_sessions;
CREATE TRIGGER auth_sessions_set_updated_at
    BEFORE UPDATE ON auth_sessions
    FOR EACH ROW EXECUTE FUNCTION set_row_updated_at();
