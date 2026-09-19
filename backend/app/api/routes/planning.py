from uuid import UUID

from fastapi import APIRouter, status, Depends

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
    return await planning_service.create_task(db=db, obj_in=task_in, user_id=current_user.id)

@router.patch("/tasks/{task_id}", response_model=TaskResponse)
async def update_task(
    *,
    db: SessionDep,
    current_user: CurrentUser,
    task_id: UUID,
    task_in: TaskUpdate,
):
    return await planning_service.update_task(db=db, task_id=task_id, obj_in=task_in, user_id=current_user.id)

@router.get("/tasks/{task_id}", response_model=TaskResponse)
async def get_task(
    *,
    db: SessionDep,
    current_user: CurrentUser,
    task_id: UUID,
):
    return await planning_service.get_task(db=db, task_id=task_id, user_id=current_user.id)

@router.get("/tasks", response_model=list[TaskResponse])
async def list_tasks(
    *,
    db: SessionDep,
    current_user: CurrentUser,
    skip: int = 0,
    limit: int = 100,
):
    return await planning_service.list_tasks(db=db, user_id=current_user.id, skip=skip, limit=limit)

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
    return await planning_service.generate_timeline(db=db, request=request, user_id=current_user.id)

@router.post("/daily-plans", response_model=DailyPlanResponse)
async def save_daily_plan(
    *,
    db: SessionDep,
    current_user: CurrentUser,
    request: SaveDailyPlanRequest,
):
    plan = await planning_service.save_daily_plan(db=db, request=request, user_id=current_user.id)
    # The return object from service is a DB DailyPlan model
    blocks = [
        {
            "block_type": b.block_type,
            "task_id": b.task_id,
            "title": b.title,
            "planned_start_at": b.planned_start_at,
            "planned_end_at": b.planned_end_at,
            "position": b.position,
            "status": b.status
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
        "blocks": blocks
    }

from app.models.ai_schemas import AIRequestContext
from app.models.api_schemas import PlanningDraftRequest
from app.services.ai_router import AIRouter

def get_ai_router() -> AIRouter:
    return AIRouter()

@router.post("/draft")
async def generate_planning_draft(
    *,
    request: PlanningDraftRequest,
    current_user: CurrentUser,
    db: SessionDep,
    ai_router: AIRouter = Depends(get_ai_router)
):
    from fastapi.responses import JSONResponse
    from app.services.ai_router import AIRouterException

    try:
        from datetime import datetime
        import zoneinfo
        from sqlalchemy import select
        from app.db.models.users import UserSettings

        # Extract basic info
        user_input = request.user_input
        context_type = request.context_type

        # Real server-side timezone resolution
        stmt = select(UserSettings).where(UserSettings.user_id == current_user.id)
        result = await db.execute(stmt)
        settings = result.scalars().first()
        
        if not settings or not settings.timezone:
            return JSONResponse(status_code=422, content={
                "status": "error",
                "meta": {},
                "error": {
                    "code": "TIMEZONE_NOT_CONFIGURED",
                    "message": "User timezone is not configured."
                }
            })
            
        user_tz_str = settings.timezone
        try:
            user_tz = zoneinfo.ZoneInfo(user_tz_str)
        except Exception:
            return JSONResponse(status_code=422, content={
                "status": "error",
                "meta": {},
                "error": {
                    "code": "INVALID_TIMEZONE",
                    "message": "The configured timezone is invalid."
                }
            })
            
        current_time = datetime.now(user_tz)

        req_context = AIRequestContext(
            user_input=user_input,
            context_type=context_type,
            current_time=current_time,
            timezone=user_tz_str
        )

        draft = await ai_router.generate_draft(req_context)
        return draft
    except AIRouterException as e:
        return JSONResponse(status_code=e.status_code, content={
            "status": "error",
            "meta": {
                "provider_used": e.provider_used,
                "fallback_triggered": e.fallback,
                "latency_ms": e.latency,
                "result_category": e.code
            },
            "error": {
                "code": e.code,
                "message": e.message
            }
        })
    except Exception as e:
        return JSONResponse(status_code=500, content={
            "status": "error",
            "meta": {},
            "error": {
                "code": "INTERNAL_SERVER_ERROR",
                "message": "An unexpected internal error occurred."
            }
        })

