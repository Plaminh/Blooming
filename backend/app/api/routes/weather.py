from fastapi import APIRouter

from app.api.deps import CurrentUser, SessionDep
from app.services.user_settings_service import get_user_settings
from app.services.weather_service import current_weather

router = APIRouter(tags=["weather"])


@router.get("/me/weather")
async def read_weather(db: SessionDep, current_user: CurrentUser) -> dict[str, str]:
    settings = await get_user_settings(db, current_user.id)
    if not settings.weather_enabled or not settings.weather_location:
        return {"condition": "CLEAR"}
    return {"condition": await current_weather(settings.weather_location)}
