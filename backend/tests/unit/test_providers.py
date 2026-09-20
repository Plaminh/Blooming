import pytest
from app.ai.providers import CircuitBreaker

def test_circuit_breaker():
    cb = CircuitBreaker(failure_threshold=2, cooldown_seconds=0.1)
    
    assert cb.is_allowed() == True
    
    cb.record_failure()
    assert cb.is_allowed() == True
    
    cb.record_failure()
    assert cb.is_allowed() == False
    
    import time
    time.sleep(0.15)
    
    # Should be half-open now
    assert cb.is_allowed() == True
    
    # Successful request resets it
    cb.record_success()
    assert cb.is_allowed() == True
