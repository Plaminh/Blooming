from datetime import date, datetime, timezone
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from app.crud.crud_daily_plan import daily_plan as crud_daily_plan
from app.crud.crud_task import task as crud_task
from app.schemas.today import TodayTaskEdit, TodayTaskStatusUpdate
from app.core.errors import ResourceNotFoundError, UnauthorizedOwnershipError
import zoneinfo

class TodayService:
    async def get_today(self, db: AsyncSession, user_id: UUID, local_date: date | None = None) -> dict:
        if local_date is None:
            from app.db.models.users import User
            user = await db.get(User, user_id)
            tz = zoneinfo.ZoneInfo(user.timezone) if user and hasattr(user, 'timezone') and user.timezone else timezone.utc
            local_date = datetime.now(tz).date()

        plan = await crud_daily_plan.get_by_date(db, user_id, local_date)
        if not plan or plan.status == "DRAFT":
            return {"plan_date": local_date, "status": "NO_PLAN"}
        
        blocks = sorted(plan.plan_blocks, key=lambda b: b.position)
        return {
            "plan_date": plan.plan_date,
            "status": plan.status,
            "reality_check": plan.reality_check,
            "blocks": blocks
        }

    async def update_task_from_today(self, db: AsyncSession, user_id: UUID, task_id: UUID, obj_in: TodayTaskEdit) -> dict:
        task_db = await crud_task.get_with_plan_blocks(db, id=task_id)
        if not task_db:
            raise ResourceNotFoundError("Task not found")
        if task_db.user_id != user_id:
            raise UnauthorizedOwnershipError()

        if obj_in.title is not None:
            task_db.title = obj_in.title
        if obj_in.estimated_duration_minutes is not None:
            task_db.estimated_duration_minutes = obj_in.estimated_duration_minutes
        
        db.add(task_db)
        
        # update title in plan blocks as well
        if obj_in.title is not None:
            for b in task_db.plan_blocks:
                b.title = obj_in.title
                db.add(b)
                
        await db.commit()
        return task_db

    async def update_task_status_from_today(self, db: AsyncSession, user_id: UUID, task_id: UUID, obj_in: TodayTaskStatusUpdate) -> dict:
        task_db = await crud_task.get_with_plan_blocks(db, id=task_id)
        if not task_db:
            raise ResourceNotFoundError("Task not found")
        if task_db.user_id != user_id:
            raise UnauthorizedOwnershipError()
            
        if task_db.status == obj_in.status:
            return task_db # Idempotent

        task_db.status = obj_in.status
        if obj_in.status == "COMPLETED":
            task_db.completed_at = datetime.now(timezone.utc)
        else:
            task_db.completed_at = None

        db.add(task_db)
        
        # update plan blocks
        block_status_map = {
            "DRAFT": "PLANNED",
            "PENDING": "PLANNED",
            "IN_PROGRESS": "ACTIVE",
            "COMPLETED": "COMPLETED",
            "SKIPPED": "SKIPPED",
            "CANCELLED": "CANCELLED"
        }
        b_status = block_status_map.get(obj_in.status, "PLANNED")

        for b in task_db.plan_blocks:
            b.status = b_status
            if obj_in.status == "COMPLETED":
                b.completed_at = task_db.completed_at
            else:
                b.completed_at = None
            db.add(b)

        await db.commit()
        return task_db

today_service = TodayService()
