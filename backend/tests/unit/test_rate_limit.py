import time
from uuid import uuid4

from app.core.rate_limit import SlidingWindowRateLimiter

def test_rate_limiter_allows_under_limit(monkeypatch):
    limiter = SlidingWindowRateLimiter(limit=2, window_seconds=60.0)
    user = str(uuid4())
    monkeypatch.setattr(time, "monotonic", lambda: 100.0)
    assert limiter.is_allowed(user) is True
    assert limiter.is_allowed(user) is True
    assert limiter.is_allowed(user) is False

def test_rate_limiter_expires_old_requests(monkeypatch):
    limiter = SlidingWindowRateLimiter(limit=1, window_seconds=60.0)
    user = str(uuid4())
    
    current_time = 100.0
    monkeypatch.setattr(time, "monotonic", lambda: current_time)
    assert limiter.is_allowed(user) is True
    assert limiter.is_allowed(user) is False
    
    current_time = 161.0
    assert limiter.is_allowed(user) is True

def test_rate_limiter_isolates_users(monkeypatch):
    limiter = SlidingWindowRateLimiter(limit=1, window_seconds=60.0)
    user1 = str(uuid4())
    user2 = str(uuid4())
    
    monkeypatch.setattr(time, "monotonic", lambda: 100.0)
    assert limiter.is_allowed(user1) is True
    assert limiter.is_allowed(user1) is False
    
    assert limiter.is_allowed(user2) is True
    assert limiter.is_allowed(user2) is False


def test_capacity_does_not_reset_existing_user_limits(monkeypatch):
    limiter = SlidingWindowRateLimiter(limit=1, window_seconds=60, max_users=1)
    monkeypatch.setattr(time, "monotonic", lambda: 100.0)
    assert limiter.is_allowed("first") is True
    assert limiter.is_allowed("second") is False
    assert limiter.is_allowed("first") is False
