from uuid import UUID

from fastapi import APIRouter, status

from app.api.deps import CurrentUser, SessionDep
from app.schemas.planning import (
    TaskCreate,
    TaskResponse,
    TaskUpdate,
    TimelineDraftResponse,
    TimelineGenerateRequest,
    SaveDailyPlanRequest,
    DailyPlanResponse,
)
from app.services.planning_service import planning_service

router = APIRouter(prefix="/planning", tags=["planning"])


@router.post("/tasks", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
async def create_task(
    *,
    db: SessionDep,
    current_user: CurrentUser,
    task_in: TaskCreate,
):
    return await planning_service.create_task(
        db=db, obj_in=task_in, user_id=current_user.id
    )


@router.patch("/tasks/{task_id}", response_model=TaskResponse)
async def update_task(
    *,
    db: SessionDep,
    current_user: CurrentUser,
    task_id: UUID,
    task_in: TaskUpdate,
):
    return await planning_service.update_task(
        db=db, task_id=task_id, obj_in=task_in, user_id=current_user.id
    )


@router.get("/tasks/{task_id}", response_model=TaskResponse)
async def get_task(
    *,
    db: SessionDep,
    current_user: CurrentUser,
    task_id: UUID,
):
    return await planning_service.get_task(
        db=db, task_id=task_id, user_id=current_user.id
    )


@router.get("/tasks", response_model=list[TaskResponse])
async def list_tasks(
    *,
    db: SessionDep,
    current_user: CurrentUser,
    skip: int = 0,
    limit: int = 100,
):
    return await planning_service.list_tasks(
        db=db, user_id=current_user.id, skip=skip, limit=limit
    )


@router.delete("/tasks/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_task(
    *,
    db: SessionDep,
    current_user: CurrentUser,
    task_id: UUID,
):
    await planning_service.delete_task(db=db, task_id=task_id, user_id=current_user.id)


@router.post("/timeline/generate", response_model=TimelineDraftResponse)
async def generate_timeline(
    *,
    db: SessionDep,
    current_user: CurrentUser,
    request: TimelineGenerateRequest,
):
    return await planning_service.generate_timeline(
        db=db, request=request, user_id=current_user.id
    )


@router.post("/daily-plans", response_model=DailyPlanResponse)
async def save_daily_plan(
    *,
    db: SessionDep,
    current_user: CurrentUser,
    request: SaveDailyPlanRequest,
):
    plan = await planning_service.save_daily_plan(
        db=db, request=request, user_id=current_user.id
    )
    # The return object from service is a DB DailyPlan model
    blocks = [
        {
            "block_type": b.block_type,
            "task_id": b.task_id,
            "title": b.title,
            "planned_start_at": b.planned_start_at,
            "planned_end_at": b.planned_end_at,
            "position": b.position,
            "status": b.status,
        }
        for b in plan.plan_blocks
    ]
    return {
        "id": plan.id,
        "user_id": plan.user_id,
        "plan_date": plan.plan_date,
        "status": plan.status,
        "reality_check": plan.reality_check,
        "timezone_snapshot": plan.timezone_snapshot,
        "blocks": blocks,
    }
