"""Development ASGI launcher with a psycopg-compatible event loop."""

from __future__ import annotations

import os

import uvicorn

from app.core.runtime import selector_loop_factory


def main() -> None:
    uvicorn.run(
        "app.main:app",
        host=os.getenv("BLOOMING_BACKEND_HOST", "127.0.0.1"),
        port=int(os.getenv("BLOOMING_BACKEND_PORT", "8000")),
        reload=True,
        loop=selector_loop_factory,
    )


if __name__ == "__main__":
    main()
