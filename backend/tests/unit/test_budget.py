from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

import pytest

from app.ai.llm.budget import (
    BudgetMode,
    available_routes,
    get_budget_mode,
    record_usage,
)
from app.core.config import settings


def _db_with_usage(rows, user_calls=0):
    db = AsyncMock()
    db.add = MagicMock()
    result = MagicMock()
    result.all.return_value = rows
    db.execute.return_value = result
    db.scalar.return_value = user_calls
    return db


@pytest.mark.asyncio
async def test_budget_thresholds_are_evaluated_per_model():
    small = "openai/gpt-oss-20b"
    small_cap = settings.AI_TOKEN_BUDGET_24H[small]
    db = _db_with_usage([(small, small_cap * 0.72)])
    assert await get_budget_mode(db, uuid4(), "PLANNER") == BudgetMode.LEAN

    exhausted = [
        (model, capacity * 0.86)
        for model, capacity in settings.AI_TOKEN_BUDGET_24H.items()
    ]
    db = _db_with_usage(exhausted)
    # Gemini is an uncapped route in both planner tiers, so exhausting every
    # capped Groq model degrades to LEAN instead of disabling AI entirely.
    assert await get_budget_mode(db, uuid4(), "PLANNER") == BudgetMode.LEAN


@pytest.mark.asyncio
async def test_planner_lite_keeps_uncapped_fallback_when_groq_is_exhausted():
    small = "openai/gpt-oss-20b"
    db = _db_with_usage([(small, settings.AI_TOKEN_BUDGET_24H[small])])
    routes = await available_routes(db, settings.AI_ROUTE_PLANNER_LITE)
    assert routes == "gemini:gemini-3.5-flash-lite"
    assert await get_budget_mode(db, uuid4(), "PLANNER") == BudgetMode.LEAN


@pytest.mark.asyncio
async def test_exhausted_model_is_removed_without_blocking_other_models():
    exhausted = "llama-3.1-8b-instant"
    db = _db_with_usage([(exhausted, settings.AI_TOKEN_BUDGET_24H[exhausted] * 0.90)])
    routes = await available_routes(
        db,
        "groq:llama-3.1-8b-instant,groq:openai/gpt-oss-20b",
    )
    assert routes == "groq:openai/gpt-oss-20b"


@pytest.mark.asyncio
async def test_user_call_cap_is_isolated_from_other_users():
    capped_user = uuid4()
    other_user = uuid4()
    cap = settings.AI_USER_CALLS_PER_DAY["CHITCHAT"]
    capped_db = _db_with_usage([], user_calls=cap)
    other_db = _db_with_usage([], user_calls=0)
    assert (
        await get_budget_mode(capped_db, capped_user, "CHITCHAT")
        == BudgetMode.RULES_ONLY
    )
    assert await get_budget_mode(other_db, other_user, "CHITCHAT") == BudgetMode.NORMAL
    assert "ai_usage_log.user_id" in str(capped_db.scalar.call_args.args[0]).lower()


@pytest.mark.asyncio
async def test_planner_has_no_per_user_call_cap():
    db = _db_with_usage([], user_calls=1_000_000)
    assert "PLANNER" not in settings.AI_USER_CALLS_PER_DAY
    assert await get_budget_mode(db, uuid4(), "PLANNER") == BudgetMode.NORMAL


@pytest.mark.asyncio
async def test_usage_record_has_no_content_fields():
    db = AsyncMock()
    db.add = MagicMock()
    await record_usage(
        db,
        user_id=uuid4(),
        purpose="PLANNER",
        provider="groq",
        model="model",
        prompt_tokens=2,
    )
    value = db.add.call_args.args[0]
    assert not (
        {"prompt", "message", "reply", "content"} & set(value.__table__.columns.keys())
    )
    db.flush.assert_awaited_once()
