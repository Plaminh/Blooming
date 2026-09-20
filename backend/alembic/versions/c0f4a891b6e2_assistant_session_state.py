"""Repair AI usage user IDs on already upgraded databases and track pending intent.

Revision ID: c0f4a891b6e2
Revises: 8e47a157a9b0
"""

from alembic import op
import sqlalchemy as sa

revision = "c0f4a891b6e2"
down_revision = "8e47a157a9b0"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("""
    DO $$ BEGIN
      IF EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_name = 'ai_usage_log' AND column_name = 'user_id'
          AND data_type <> 'uuid'
      ) THEN
        ALTER TABLE ai_usage_log DROP CONSTRAINT IF EXISTS ai_usage_log_user_id_fkey;
        ALTER TABLE ai_usage_log ALTER COLUMN user_id TYPE uuid USING user_id::uuid;
      END IF;
    END $$;
    """)
    op.execute("""
    DO $$ BEGIN
      IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'ai_usage_log_user_id_fkey') THEN
        ALTER TABLE ai_usage_log ADD CONSTRAINT ai_usage_log_user_id_fkey
          FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE SET NULL;
      END IF;
    END $$;
    """)
    op.add_column("planning_sessions", sa.Column("pending_intent", sa.String(30), nullable=True))


def downgrade() -> None:
    op.drop_column("planning_sessions", "pending_intent")
