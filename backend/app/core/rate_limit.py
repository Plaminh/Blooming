import time
from collections import deque
from threading import Lock

class SlidingWindowRateLimiter:
    def __init__(self, limit: int, window_seconds: float = 60.0, max_users: int = 10000):
        self.limit = limit
        self.window_seconds = window_seconds
        self.max_users = max_users
        self.store: dict[str, deque[float]] = {}
        self.lock = Lock()

    def is_allowed(self, user_id: str) -> bool:
        now = time.monotonic()
        with self.lock:
            if len(self.store) >= self.max_users and user_id not in self.store:
                self._evict_stale(now)
                if len(self.store) >= self.max_users:
                    return False

            if user_id not in self.store:
                self.store[user_id] = deque()
            
            history = self.store[user_id]
            while history and history[0] <= now - self.window_seconds:
                history.popleft()
            
            if len(history) >= self.limit:
                return False
            
            history.append(now)
            return True

    def _evict_stale(self, now: float):
        stale_users = []
        for uid, history in self.store.items():
            while history and history[0] <= now - self.window_seconds:
                history.popleft()
            if not history:
                stale_users.append(uid)
        for uid in stale_users:
            del self.store[uid]
