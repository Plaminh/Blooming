from fastapi import HTTPException

from app.core.rate_limit import SlidingWindowLimiter


def test_sliding_window_blocks_then_recovers_with_retry_after():
    now = [100.0]
    limiter = SlidingWindowLimiter(2, 60, clock=lambda: now[0])
    limiter.record("account")
    limiter.record("account")

    try:
        limiter.enforce("account")
        raise AssertionError("expected the limiter to reject the third attempt")
    except HTTPException as exc:
        assert exc.status_code == 429
        assert exc.headers == {"Retry-After": "61"}

    now[0] = 161.0
    limiter.enforce("account")


def test_reset_clears_failures_for_a_successful_login():
    limiter = SlidingWindowLimiter(1, 60, clock=lambda: 100.0)
    limiter.record("account")
    limiter.reset("account")
    limiter.enforce("account")
