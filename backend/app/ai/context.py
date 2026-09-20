"""Trusted scheduling context built from authenticated settings."""

from dataclasses import dataclass, field
from datetime import datetime, time, timedelta
from uuid import UUID
from zoneinfo import ZoneInfo

from app.db.models.users import UserSettings
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession


@dataclass(frozen=True)
class ChatContext:
    db: AsyncSession
    user_id: UUID
    now: datetime
    timezone: ZoneInfo
    break_minutes: int
    default_windows: tuple[tuple[str, str], ...]
    default_date_offset: int
    calibration: dict[str, float] = field(default_factory=dict)


async def build_context(db: AsyncSession, user_id: UUID, now: datetime) -> ChatContext:
    from app.ai.calibration import calibration_multipliers

    settings = await db.scalar(
        select(UserSettings).where(UserSettings.user_id == user_id)
    )
    tz = ZoneInfo(settings.timezone if settings else "UTC")
    local = now.astimezone(tz)
    quiet_start = (
        settings.quiet_hours_start
        if settings and settings.quiet_hours_enabled
        else None
    )
    end = quiet_start or time(22, 0)
    rounded = local.replace(second=0, microsecond=0) + timedelta(
        minutes=(15 - local.minute % 15) % 15
    )
    start = max(rounded.time(), time(6, 0))
    tomorrow = datetime.combine(local.date(), end, tzinfo=tz) - rounded < timedelta(
        minutes=30
    )
    if tomorrow:
        start = time(8, 0)
    calibration = await calibration_multipliers(db, user_id)
    return ChatContext(
        db=db,
        user_id=user_id,
        now=local,
        timezone=tz,
        break_minutes=settings.default_break_minutes if settings else 5,
        default_windows=((start.strftime("%H:%M"), end.strftime("%H:%M")),),
        default_date_offset=1 if tomorrow else 0,
        calibration=calibration,
    )
