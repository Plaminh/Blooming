"""Database infrastructure: declarative base, engine/session, and ORM models.

Importing this package registers every model on ``Base.metadata``, which is what
Alembic's ``env.py`` targets.
"""

from app.db import models as models
from app.db.base import Base

__all__ = ["Base", "models"]
