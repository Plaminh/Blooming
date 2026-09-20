from datetime import date
from typing import List
from pydantic import BaseModel
from uuid import UUID

class SummaryMetrics(BaseModel):
    study_time_hours: int
    study_time_minutes: int
    study_day_count: int
    completed_plan_count: int
    unfinished_plan_count: int

class DailyStudyEntry(BaseModel):
    day_label: str
    hours: float
    date: date

class PlanHistoryItem(BaseModel):
    id: UUID
    date_label: str
    plan_name: str
    completed_tasks: int
    total_tasks: int
    status: str

class PlanHistoryResponse(BaseModel):
    items: List[PlanHistoryItem]
    total_items: int
    total_pages: int
    current_page: int
    items_per_page: int
