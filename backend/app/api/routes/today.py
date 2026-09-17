from typing import Union
from uuid import UUID
from datetime import date
from fastapi import APIRouter, Query

from app.api.deps import CurrentUser, SessionDep
from app.schemas.today import TodayResponse, TodayNoPlanResponse, TodayTaskEdit, TodayTaskStatusUpdate
from app.schemas.planning import TaskResponse
from app.services.today_service import today_service

router = APIRouter(prefix="/today", tags=["today"])

@router.get("", response_model=Union[TodayResponse, TodayNoPlanResponse])
async def get_today(
    *,
    db: SessionDep,
    current_user: CurrentUser,
    local_date: date | None = Query(default=None, alias="date"),
):
    return await today_service.get_today(db=db, user_id=current_user.id, local_date=local_date)

@router.patch("/tasks/{task_id}", response_model=TaskResponse)
async def update_today_task(
    *,
    db: SessionDep,
    current_user: CurrentUser,
    task_id: UUID,
    obj_in: TodayTaskEdit,
):
    return await today_service.update_task_from_today(db=db, user_id=current_user.id, task_id=task_id, obj_in=obj_in)

@router.patch("/tasks/{task_id}/status", response_model=TaskResponse)
async def update_today_task_status(
    *,
    db: SessionDep,
    current_user: CurrentUser,
    task_id: UUID,
    obj_in: TodayTaskStatusUpdate,
):
    return await today_service.update_task_status_from_today(db=db, user_id=current_user.id, task_id=task_id, obj_in=obj_in)
