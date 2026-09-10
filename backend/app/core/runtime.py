"""Event-loop compatibility for psycopg 3's async driver.

psycopg's async connections need ``loop.add_reader``/``add_writer``, which
Windows' default ``ProactorEventLoop`` does not implement. Both the ASGI server
and Alembic therefore have to run on a selector event loop.
"""

import asyncio
import sys


def selector_loop_factory() -> asyncio.AbstractEventLoop:
    """Create a psycopg-compatible event loop.

    Used as uvicorn's custom loop factory:
    ``uvicorn app.main:app --loop app.core.runtime:selector_loop_factory``
    """
    if sys.platform == "win32":
        return asyncio.SelectorEventLoop()
    return asyncio.new_event_loop()


def use_selector_event_loop_policy() -> None:
    """Apply a psycopg-compatible policy for scripts that create their own loop."""
    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
