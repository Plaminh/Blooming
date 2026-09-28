from fastapi import APIRouter
from app.api.deps import SessionDep, CurrentUser
from app.schemas.user_settings import UserSettingsResponse, UserSettingsUpdate
from app.services import user_settings_service

router = APIRouter(tags=["settings"])


@router.get("/me/settings", response_model=UserSettingsResponse)
async def read_settings(db: SessionDep, current_user: CurrentUser):
    return await user_settings_service.get_user_settings(db, current_user.id)


@router.put("/me/settings", response_model=UserSettingsResponse)
async def update_settings(
    db: SessionDep, current_user: CurrentUser, settings_in: UserSettingsUpdate
):
    return await user_settings_service.update_user_settings(
        db, current_user.id, settings_in
    )
