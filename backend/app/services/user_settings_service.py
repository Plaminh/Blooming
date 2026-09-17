from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from fastapi import HTTPException, status

from app.db.models.users import UserSettings
from app.schemas.user_settings import UserSettingsUpdate

async def get_user_settings(db: AsyncSession, user_id: str) -> UserSettings:
    result = await db.execute(select(UserSettings).where(UserSettings.user_id == user_id))
    settings = result.scalars().first()
    if not settings:
        raise HTTPException(status_code=404, detail="Settings not found")
    return settings

async def update_user_settings(db: AsyncSession, user_id: str, settings_in: UserSettingsUpdate) -> UserSettings:
    settings = await get_user_settings(db, user_id)
    
    update_data = settings_in.model_dump(exclude_unset=True)
    
    # Validation moved to Pydantic schemas
            
    for field, value in update_data.items():
        setattr(settings, field, value)
        
    if settings.quiet_hours_enabled:
        if settings.quiet_hours_start is None or settings.quiet_hours_end is None:
            raise HTTPException(status_code=422, detail="Both quiet_hours_start and quiet_hours_end must be provided when quiet_hours_enabled is true")
            
    if (settings.quiet_hours_start is None) != (settings.quiet_hours_end is None):
        raise HTTPException(status_code=422, detail="quiet_hours_start and quiet_hours_end must both be provided or both be omitted")
        
    db.add(settings)
    await db.commit()
    await db.refresh(settings)
    return settings
