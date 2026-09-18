"""Persist the widget rain animation preference.

Revision ID: b21e8a59c4d2
Revises: 6ebc3e7e2e0e
"""

from alembic import op

revision = "b21e8a59c4d2"
down_revision = "6ebc3e7e2e0e"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute(
        "ALTER TABLE user_settings ADD COLUMN IF NOT EXISTS "
        "weather_animation_enabled BOOLEAN NOT NULL DEFAULT TRUE"
    )


def downgrade() -> None:
    op.execute("ALTER TABLE user_settings DROP COLUMN IF EXISTS weather_animation_enabled")
