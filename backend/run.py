import sys
import asyncio

from app.core.runtime import use_selector_event_loop_policy
use_selector_event_loop_policy()

import uvicorn

if __name__ == "__main__":
    uvicorn.run("app.main:app", port=8000, log_level="info", loop="none")
