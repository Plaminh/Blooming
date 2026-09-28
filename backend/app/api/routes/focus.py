from fastapi import APIRouter
from app.api.deps import CurrentUser, SessionDep
from app.schemas.focus import FocusSessionStart, FocusSessionFinish, FocusRunResponse
from app.services.focus_service import focus_service
from app.core.errors import ResourceNotFoundError

router = APIRouter(prefix="/focus", tags=["focus"])


@router.post("/start", response_model=FocusRunResponse)
async def start_session(
    *,
    db: SessionDep,
    current_user: CurrentUser,
    obj_in: FocusSessionStart,
):
    return await focus_service.start_session(
        db=db, user_id=current_user.id, obj_in=obj_in
    )


@router.post("/pause", response_model=FocusRunResponse)
async def pause_session(
    *,
    db: SessionDep,
    current_user: CurrentUser,
):
    return await focus_service.pause_session(db=db, user_id=current_user.id)


@router.post("/resume", response_model=FocusRunResponse)
async def resume_session(
    *,
    db: SessionDep,
    current_user: CurrentUser,
):
    return await focus_service.resume_session(db=db, user_id=current_user.id)


@router.get("/active", response_model=FocusRunResponse)
async def get_active_session(
    *,
    db: SessionDep,
    current_user: CurrentUser,
):
    run = await focus_service.get_active_session(db, current_user.id)
    if not run:
        raise ResourceNotFoundError("No active focus session")
    return run


@router.post("/finish", response_model=FocusRunResponse)
async def finish_session(
    *,
    db: SessionDep,
    current_user: CurrentUser,
    obj_in: FocusSessionFinish,
):
    return await focus_service.finish_session(
        db=db, user_id=current_user.id, obj_in=obj_in
    )
