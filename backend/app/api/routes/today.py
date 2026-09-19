from datetime import date
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Query

from app.api.deps import CurrentUser, SessionDep
from app.schemas.planning import TaskResponse
from app.schemas.today import (
    TodayNoPlanResponse,
    TodayPreviewRequest,
    TodayPreviewResponse,
    TodayResponse,
    TodaySaveRequest,
    TodayTaskEdit,
    TodayTaskStatusUpdate,
)
from app.services.today_service import today_service

router = APIRouter(prefix="/today", tags=["today"])


@router.post("/preview", response_model=TodayPreviewResponse)
async def preview_today_draft(*, db: SessionDep, current_user: CurrentUser, obj_in: TodayPreviewRequest):
    return await today_service.preview_today_draft(db, current_user.id, obj_in)


@router.post("/save", response_model=TodayResponse)
async def save_today_draft(*, db: SessionDep, current_user: CurrentUser, obj_in: TodaySaveRequest):
    return await today_service.save_today_draft(db, current_user.id, obj_in)


@router.get("", response_model=TodayResponse | TodayNoPlanResponse)
async def get_today(
    *,
    db: SessionDep,
    current_user: CurrentUser,
    local_date: Annotated[date | None, Query(alias="date")] = None,
):
    return await today_service.get_today(
        db=db, user_id=current_user.id, local_date=local_date
    )


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


@router.post("/replan", response_model=TodayResponse | TodayNoPlanResponse)
async def replan_today(
    *,
    db: SessionDep,
    current_user: CurrentUser,
):
    return await today_service.replan_today(db=db, user_id=current_user.id)
