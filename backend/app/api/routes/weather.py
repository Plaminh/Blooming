from fastapi import APIRouter, HTTPException, Query

from app.api.deps import CurrentUser, SessionDep
from app.models.enums import WeatherCondition, WeatherStatus
from app.schemas.weather import PlaceSearchResponse, WeatherResponse
from app.services.user_settings_service import get_user_settings
from app.services.weather_service import (
    WeatherProviderError,
    get_forecast,
    search_places,
)

router = APIRouter(prefix="/weather", tags=["weather"])
legacy_router = APIRouter(tags=["weather"])


@router.get("/search", response_model=PlaceSearchResponse)
async def api_search_places(
    current_user: CurrentUser,
    q: str = Query(..., min_length=2),
    lang: str = Query("en", min_length=2, max_length=2),
) -> PlaceSearchResponse:
    """Search for weather locations (up to 5 candidates)."""
    if len(q.strip()) < 2:
        raise HTTPException(status_code=422, detail="Search query is too short")
    try:
        return await search_places(q, language=lang)
    except WeatherProviderError as exc:
        raise HTTPException(
            status_code=503, detail="Place search is temporarily unavailable"
        ) from exc


@router.get("/current", response_model=WeatherResponse)
async def api_get_weather(db: SessionDep, current_user: CurrentUser) -> WeatherResponse:
    """Get the current weather forecast using the user's saved location coordinates."""
    settings = await get_user_settings(db, current_user.id)

    if not settings.weather_enabled:
        return WeatherResponse(
            condition=WeatherCondition.CLEAR,
            status=WeatherStatus.DISABLED,
            updated_at=None,
        )

    if settings.weather_lat is None or settings.weather_lon is None:
        return WeatherResponse(
            condition=WeatherCondition.CLEAR,
            status=WeatherStatus.UNAVAILABLE,
            updated_at=None,
        )

    # We no longer do legacy text-based geocoding.
    # If coordinates are missing, it's strictly UNAVAILABLE.

    return await get_forecast(settings.weather_lat, settings.weather_lon)


@legacy_router.get("/me/weather", include_in_schema=False)
async def legacy_weather(db: SessionDep, current_user: CurrentUser) -> WeatherResponse:
    return await api_get_weather(db, current_user)
