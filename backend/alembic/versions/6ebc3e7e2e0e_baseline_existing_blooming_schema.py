"""baseline existing blooming schema

Intentionally empty. The 19 Blooming tables, triggers, and indexes were already
installed from database/install.sql before Alembic was introduced, so this
revision only marks that state as the migration baseline. Databases at this
schema are stamped to this revision rather than upgraded into it.

The legacy `flyway_schema_history` table is out of scope and is excluded from
autogenerate comparison in alembic/env.py.

Revision ID: 6ebc3e7e2e0e
Revises:
Create Date: 2026-09-10 15:30:28.370890

"""
from typing import Sequence, Union



# revision identifiers, used by Alembic.
revision: str = '6ebc3e7e2e0e'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """No-op: the baseline schema already exists in PostgreSQL."""
    pass


def downgrade() -> None:
    """No-op: the baseline schema is owned by database/install.sql."""
    pass
