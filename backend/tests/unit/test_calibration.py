from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

import pytest
from app.ai.calibration import apply_multiplier, calibration_multipliers


@pytest.mark.asyncio
async def test_calibration_requires_five_distinct_tasks_and_uses_median():
    rows = [(uuid4(), "Work", 40, 3600) for _ in range(5)]
    result = MagicMock()
    result.all.return_value = rows
    db = AsyncMock()
    db.execute.return_value = result
    user_id = uuid4()
    values = await calibration_multipliers(db, user_id)
    assert values == {"Work": 1.36}
    assert apply_multiplier(40, "Work", values) == 55
    assert "tasks.source" in str(db.execute.call_args.args[0]).lower()
    query = str(db.execute.call_args.args[0]).lower()
    assert "tasks.status" in query
    assert "tasks.completed_at" in query
    assert await calibration_multipliers(db, user_id) == values
    db.execute.assert_awaited_once()


@pytest.mark.asyncio
async def test_calibration_ignores_small_samples():
    result = MagicMock()
    result.all.return_value = [(uuid4(), "Learning", 60, 5400) for _ in range(4)]
    db = AsyncMock()
    db.execute.return_value = result
    assert await calibration_multipliers(db, uuid4()) == {}
