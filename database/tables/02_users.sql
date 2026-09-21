-- Table: users
CREATE TABLE users (
	id UUID DEFAULT gen_random_uuid() NOT NULL, 
	email VARCHAR(320) NOT NULL, 
	password_hash TEXT NOT NULL, 
	display_name VARCHAR(100), 
	account_status VARCHAR(20) DEFAULT 'ACTIVE' NOT NULL, 
	email_verified_at TIMESTAMP WITH TIME ZONE, 
	last_login_at TIMESTAMP WITH TIME ZONE, 
	created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	updated_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	PRIMARY KEY (id), 
	CONSTRAINT users_email_not_blank CHECK (BTRIM(email) <> ''), 
	CONSTRAINT users_account_status_valid CHECK (account_status IN ('ACTIVE', 'DISABLED'))
);
CREATE UNIQUE INDEX users_email_lower_unique_idx ON users (LOWER(email));
DROP TRIGGER IF EXISTS users_set_updated_at ON users;
CREATE TRIGGER users_set_updated_at
    BEFORE UPDATE ON users
    FOR EACH ROW EXECUTE FUNCTION set_row_updated_at();
