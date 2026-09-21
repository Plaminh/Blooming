"""Rolling per-model AI budgets and privacy-safe usage accounting."""

from datetime import datetime, timedelta, timezone
from enum import Enum
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.db.models.ai_usage import AiUsageLog


class BudgetMode(str, Enum):
    NORMAL = "NORMAL"
    LEAN = "LEAN"
    RULES_ONLY = "RULES_ONLY"


def _purpose_routes(purpose: str) -> str:
    if purpose == "EDITOR":
        return settings.AI_ROUTE_EDITOR
    if purpose == "PLANNER":
        return f"{settings.AI_ROUTE_PLANNER_LITE},{settings.AI_ROUTE_PLANNER}"
    if purpose == "CHITCHAT":
        return settings.AI_ROUTE_CHITCHAT
    return settings.AI_ROUTE_ROUTER


def _route_parts(route_spec: str) -> list[tuple[str, str]]:
    parts: list[tuple[str, str]] = []
    for raw in route_spec.split(","):
        provider, separator, model = raw.strip().partition(":")
        if separator and provider and model:
            parts.append((provider, model))
    return parts


async def model_budget_ratios(
    db: AsyncSession,
    route_spec: str,
    *,
    now: datetime | None = None,
) -> dict[str, float]:
    """Return rolling utilization for capped models referenced by a route."""
    now = now or datetime.now(timezone.utc)
    since = now - timedelta(hours=24)
    models = {
        model
        for provider, model in _route_parts(route_spec)
        if provider != "ollama" and model in settings.AI_TOKEN_BUDGET_24H
    }
    if not models:
        return {}
    rows = (
        await db.execute(
            select(
                AiUsageLog.model,
                func.coalesce(
                    func.sum(
                        func.coalesce(AiUsageLog.prompt_tokens, 0)
                        + func.coalesce(AiUsageLog.completion_tokens, 0)
                    ),
                    0,
                ),
            )
            .where(AiUsageLog.created_at >= since, AiUsageLog.model.in_(models))
            .group_by(AiUsageLog.model)
        )
    ).all()
    used_by_model = {model: int(used or 0) for model, used in rows}
    ratios = {}
    for model in models:
        capacity = settings.AI_TOKEN_BUDGET_24H[model]
        ratios[model] = (
            used_by_model.get(model, 0) / capacity if capacity > 0 else 1.0
        )
    return ratios


async def available_routes(
    db: AsyncSession,
    route_spec: str,
    *,
    now: datetime | None = None,
) -> str:
    """Remove only routes whose own rolling model quota is exhausted."""
    ratios = await model_budget_ratios(db, route_spec, now=now)
    allowed = [
        f"{provider}:{model}"
        for provider, model in _route_parts(route_spec)
        if provider == "ollama"
        or ratios.get(model, 0.0) < settings.AI_BUDGET_RULES_ONLY_THRESHOLD
    ]
    return ",".join(allowed)


async def get_budget_mode(
    db: AsyncSession,
    user_id: UUID,
    purpose: str,
    *,
    now: datetime | None = None,
) -> BudgetMode:
    now = now or datetime.now(timezone.utc)
    since = now - timedelta(hours=24)
    route_spec = _purpose_routes(purpose)
    ratios = await model_budget_ratios(db, route_spec, now=now)
    user_calls = await db.scalar(
        select(func.count(AiUsageLog.id)).where(
            AiUsageLog.user_id == user_id,
            AiUsageLog.purpose == purpose,
            AiUsageLog.created_at >= since,
        )
    )
    cap = settings.AI_USER_CALLS_PER_DAY.get(purpose)
    if cap is not None and int(user_calls or 0) >= cap:
        return BudgetMode.RULES_ONLY

    route_parts = _route_parts(route_spec)
    usable = [
        (provider, model)
        for provider, model in route_parts
        if provider == "ollama"
        or ratios.get(model, 0.0) < settings.AI_BUDGET_RULES_ONLY_THRESHOLD
    ]
    if route_parts and not usable:
        return BudgetMode.RULES_ONLY
    if len(usable) < len(route_parts) or any(
        ratio >= settings.AI_BUDGET_LEAN_THRESHOLD for ratio in ratios.values()
    ):
        return BudgetMode.LEAN
    return BudgetMode.NORMAL


async def record_usage(
    db: AsyncSession,
    *,
    user_id: UUID | None,
    purpose: str,
    provider: str,
    model: str,
    prompt_tokens: int = 0,
    completion_tokens: int = 0,
    latency_ms: int = 0,
    outcome: str = "OK",
) -> None:
    """Persist operational metadata only. This API accepts no message content."""
    db.add(
        AiUsageLog(
            user_id=user_id,
            purpose=purpose[:20],
            provider=provider[:20],
            model=model[:80],
            prompt_tokens=max(0, int(prompt_tokens or 0)),
            completion_tokens=max(0, int(completion_tokens or 0)),
            latency_ms=max(0, int(latency_ms or 0)),
            outcome=outcome[:20],
        )
    )
    await db.flush()
