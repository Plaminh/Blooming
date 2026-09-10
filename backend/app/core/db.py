"""Engine and session lifecycle live in ``app.db.session``.

This module is kept as the documented ``app/core`` entry point and re-exports
the async engine and session factory so existing imports keep working.
"""

from app.db.session import AsyncSessionLocal, engine

__all__ = ["AsyncSessionLocal", "engine"]
