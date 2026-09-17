from fastapi import APIRouter
from app.api.deps import SessionDep, CurrentUser
from app.schemas.user import UserResponse, UserUpdate
from app.services import user_service

router = APIRouter(tags=["users"])

@router.get("/me", response_model=UserResponse)
async def read_user_me(current_user: CurrentUser):
    return current_user

@router.put("/me", response_model=UserResponse)
async def update_user_me(db: SessionDep, current_user: CurrentUser, user_in: UserUpdate):
    return await user_service.update_user(db, current_user, user_in)
