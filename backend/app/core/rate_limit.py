"""Small in-process sliding-window limiter for unauthenticated endpoints.

The API currently runs as a single uvicorn worker. If it is scaled out, these
counters must move to a shared store so every worker observes the same limits.
"""

import time
from collections import deque
from collections.abc import Callable

from fastapi import HTTPException, status

_MAX_KEYS = 10_000


class SlidingWindowLimiter:
    def __init__(
        self,
        max_events: int,
        window_seconds: float,
        clock: Callable[[], float] = time.monotonic,
    ):
        self.max_events = max_events
        self.window_seconds = window_seconds
        self.clock = clock
        self._events: dict[str, deque[float]] = {}

    def _prune(self, key: str) -> deque[float]:
        events = self._events.setdefault(key, deque())
        cutoff = self.clock() - self.window_seconds
        while events and events[0] <= cutoff:
            events.popleft()
        if not events:
            self._events.pop(key, None)
        return events

    def retry_after(self, key: str) -> int:
        events = self._prune(key)
        if len(events) < self.max_events:
            return 0
        return max(1, int(events[0] + self.window_seconds - self.clock()) + 1)

    def record(self, key: str) -> None:
        if len(self._events) >= _MAX_KEYS:
            for stale in list(self._events)[: _MAX_KEYS // 10]:
                self._prune(stale)
            if len(self._events) >= _MAX_KEYS:
                self._events.pop(next(iter(self._events)))
        self._events.setdefault(key, deque()).append(self.clock())

    def reset(self, key: str) -> None:
        self._events.pop(key, None)

    def enforce(self, key: str) -> None:
        wait = self.retry_after(key)
        if wait:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Too many attempts. Please try again later.",
                headers={"Retry-After": str(wait)},
            )


# Bound bcrypt work regardless of whether credentials are right, wrong, or
# belong to an unverified user. This is deliberately keyed only by client IP.
login_requests = SlidingWindowLimiter(max_events=30, window_seconds=15 * 60)
# Failed credentials are narrower: one source attacking one account cannot
# lock that account for a legitimate user coming from another address.
login_failures = SlidingWindowLimiter(max_events=10, window_seconds=15 * 60)
registration_attempts = SlidingWindowLimiter(max_events=20, window_seconds=60 * 60)
resend_attempts = SlidingWindowLimiter(max_events=20, window_seconds=60 * 60)
