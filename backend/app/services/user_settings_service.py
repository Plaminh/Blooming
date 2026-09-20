from uuid import UUID

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.users import User, UserSettings
from app.schemas.user_settings import UserSettingsUpdate


async def get_user_settings(db: AsyncSession, user_id: UUID) -> UserSettings:
    result = await db.execute(
        select(UserSettings).where(UserSettings.user_id == user_id)
    )
    settings = result.scalars().first()
    if not settings:
        raise HTTPException(status_code=404, detail="Settings not found")
    return settings


async def update_user_settings(
    db: AsyncSession, user_id: UUID, settings_in: UserSettingsUpdate
) -> UserSettings:
    await db.execute(select(User.id).where(User.id == user_id).with_for_update())
    settings = await get_user_settings(db, user_id)

    update_data = settings_in.model_dump(exclude_unset=True)

    # Validation moved to Pydantic schemas

    for field, value in update_data.items():
        setattr(settings, field, value)

    if (settings.weather_lat is None) != (settings.weather_lon is None):
        raise HTTPException(
            status_code=422, detail="Both weather coordinates are required"
        )
    if (
        settings.weather_lat is not None
        and not (settings.weather_location_name or "").strip()
    ):
        raise HTTPException(status_code=422, detail="A selected place name is required")
    location_changed = bool(
        {"weather_enabled", "weather_lat", "weather_lon", "weather_location_name"}
        & update_data.keys()
    )
    if settings.weather_enabled and settings.weather_lat is None and location_changed:
        raise HTTPException(status_code=422, detail="Select a weather location first")

    if settings.quiet_hours_enabled and (
        settings.quiet_hours_start is None or settings.quiet_hours_end is None
    ):
        raise HTTPException(
            status_code=422,
            detail="Both quiet_hours_start and quiet_hours_end must be provided when quiet_hours_enabled is true",
        )

    if (settings.quiet_hours_start is None) != (settings.quiet_hours_end is None):
        raise HTTPException(
            status_code=422,
            detail="quiet_hours_start and quiet_hours_end must both be provided or both be omitted",
        )

    db.add(settings)
    await db.flush()
    if "milestone_reminder_lead_time_minutes" in update_data:
        from app.db.models.goals import Goal, Milestone
        from app.services.reminders_service import reminders_service

        milestones = (
            await db.scalars(
                select(Milestone).join(Goal).where(Goal.user_id == user_id)
            )
        ).all()
        for milestone in milestones:
            await reminders_service.sync_milestone_reminder(
                db,
                user_id,
                milestone.id,
                milestone.title,
                milestone.due_at,
                milestone.status,
            )
    await db.commit()
    await db.refresh(settings)
    return settings
