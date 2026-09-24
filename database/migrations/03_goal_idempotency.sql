-- Apply to existing Blooming databases. New installations receive the same
-- definition from database/tables/07_goals.sql.
ALTER TABLE goals ADD COLUMN IF NOT EXISTS source_idempotency_key VARCHAR(200);
CREATE UNIQUE INDEX IF NOT EXISTS goals_user_idempotency_idx
    ON goals (user_id, source_idempotency_key)
    WHERE source_idempotency_key IS NOT NULL;
