from datetime import date
from typing import Optional, List
from fastapi import APIRouter, Depends, Query, HTTPException

from app.api.deps import SessionDep, CurrentUser
from app.schemas.statistics import SummaryMetrics, DailyStudyEntry, PlanHistoryResponse
from app.services import statistics_service

router = APIRouter(prefix="/statistics", tags=["statistics"])

def validate_dates(start_date: date, end_date: date):
    if start_date > end_date:
        raise HTTPException(status_code=400, detail="start_date must be less than or equal to end_date")
    if (end_date - start_date).days > 366:
        raise HTTPException(status_code=400, detail="Date range cannot exceed one year")

@router.get("/summary", response_model=SummaryMetrics)
async def get_summary(
    start_date: date,
    end_date: date,
    current_user: CurrentUser,
    db: SessionDep,
    timezone: Optional[str] = None
):
    validate_dates(start_date, end_date)
    return await statistics_service.get_statistics_summary(
        db=db,
        user_id=current_user.id,
        start_date=start_date,
        end_date=end_date,
        requested_tz=timezone
    )

@router.get("/daily", response_model=List[DailyStudyEntry])
async def get_daily(
    start_date: date,
    end_date: date,
    current_user: CurrentUser,
    db: SessionDep,
    timezone: Optional[str] = None
):
    validate_dates(start_date, end_date)
    return await statistics_service.get_daily_statistics(
        db=db,
        user_id=current_user.id,
        start_date=start_date,
        end_date=end_date,
        requested_tz=timezone
    )

@router.get("/plan-history", response_model=PlanHistoryResponse)
async def get_plan_history(
    start_date: date,
    end_date: date,
    current_user: CurrentUser,
    db: SessionDep,
    status: str = Query("All", description="Status filter: All, Completed, Unfinished"),
    page: int = Query(1, ge=1),
    page_size: int = Query(4, ge=1, le=50)
):
    validate_dates(start_date, end_date)
    if status not in ("All", "Completed", "Unfinished"):
        raise HTTPException(status_code=422, detail="Invalid status filter")
        
    return await statistics_service.get_plan_history(
        db=db,
        user_id=current_user.id,
        start_date=start_date,
        end_date=end_date,
        status_filter=status,
        page=page,
        page_size=page_size
    )
