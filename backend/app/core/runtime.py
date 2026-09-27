"""Event-loop compatibility for psycopg 3's async driver.

psycopg's async connections need ``loop.add_reader``/``add_writer``, which
Windows' default ``ProactorEventLoop`` does not implement. The ASGI server
therefore has to run on a selector event loop.
"""

import asyncio
import sys


def selector_loop_factory() -> asyncio.AbstractEventLoop:
    """Create a psycopg-compatible event loop.

    Passed programmatically by ``dev_server.py`` because Uvicorn's CLI only
    accepts its built-in loop names.
    """
    if sys.platform == "win32":
        return asyncio.SelectorEventLoop()
    return asyncio.new_event_loop()


