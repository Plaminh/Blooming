-- Extensions and common functions
CREATE EXTENSION IF NOT EXISTS pgcrypto;

-- Scope: keep mutable rows' updated_at values correct inside PostgreSQL.
CREATE OR REPLACE FUNCTION set_row_updated_at()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$;
