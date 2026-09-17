from datetime import date, datetime, timezone
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from app.crud.crud_daily_plan import daily_plan as crud_daily_plan
from app.crud.crud_task import task as crud_task
from app.schemas.today import TodayTaskEdit, TodayTaskStatusUpdate
from app.core.errors import ResourceNotFoundError, UnauthorizedOwnershipError
from app.db.models.users import User
from app.db.models.tasks import Task
from app.db.models.daily_plans import PlanBlock
from app.core.scheduler import DeterministicScheduler, ScheduleTask, ScheduleWindow
import zoneinfo

class TodayService:
    async def get_today(self, db: AsyncSession, user_id: UUID, local_date: date | None = None) -> dict:
        if local_date is None:
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

    async def replan_today(self, db: AsyncSession, user_id: UUID, commit: bool = True) -> dict:
        user = await db.get(User, user_id)
        tz = zoneinfo.ZoneInfo(user.timezone) if user and hasattr(user, 'timezone') and user.timezone else timezone.utc
        local_date = datetime.now(tz).date()

        plan = await crud_daily_plan.get_by_date(db, user_id, local_date)
        if not plan or plan.status == "DRAFT":
            return {"plan_date": local_date, "status": "NO_PLAN"}

        now = datetime.now(timezone.utc)
        
        # 1. Gather existing blocks
        blocks = sorted(plan.plan_blocks, key=lambda b: b.planned_start_at)
        
        # Load tasks for the blocks
        block_task_ids = [b.task_id for b in blocks if b.task_id]
        tasks_result = await db.execute(select(Task).options(selectinload(Task.dependencies)).where(Task.id.in_(block_task_ids)))
        tasks_dict = {t.id: t for t in tasks_result.scalars().all()}
        
        preserved_blocks = []
        flexible_task_ids = []
        
        for b in blocks:
            b_task = tasks_dict.get(b.task_id) if b.task_id else None
            # Check if block is in the past, or completed/skipped/cancelled, or is a fixed event/task
            if b.planned_end_at <= now or b.status in ("COMPLETED", "SKIPPED", "CANCELLED", "ACTIVE"):
                preserved_blocks.append(b)
            elif b_task and b_task.scheduling_type == 'FIXED':
                preserved_blocks.append(b)
            elif b.block_type == "FIXED_EVENT":
                preserved_blocks.append(b)
            else:
                if b_task and b_task.status not in ("COMPLETED", "SKIPPED", "CANCELLED"):
                    if b.task_id not in flexible_task_ids:
                        flexible_task_ids.append(b.task_id)

        # 2. Prepare windows from now
        windows = []
        for w in plan.availability_windows:
            if w.available_end_at > now:
                windows.append(ScheduleWindow(
                    start_at=max(w.available_start_at, now),
                    end_at=w.available_end_at
                ))
                
        # 3. Load tasks for scheduler
        schedule_tasks = []
        for tid in flexible_task_ids:
            t = tasks_dict.get(tid)
            if t:
                # Add dummy dependency if needed? The scheduler handles it.
                schedule_tasks.append(ScheduleTask(
                    id=t.id,
                    title=t.title,
                    estimated_duration_minutes=t.estimated_duration_minutes,
                    priority=t.priority,
                    scheduling_type=t.scheduling_type,
                    is_splittable=t.is_splittable,
                    min_split_duration_minutes=t.min_split_duration_minutes,
                    preferred_break_duration_minutes=t.preferred_break_duration_minutes,
                    fixed_start_at=t.fixed_start_at,
                    fixed_end_at=t.fixed_end_at,
                    dependencies=[d.depends_on_task_id for d in t.dependencies],
                    created_at=t.created_at
                ))
        
        # Add preserved blocks as fixed tasks so scheduler schedules around them
        for b in preserved_blocks:
            if b.planned_end_at > now:
                # Need to block this time
                schedule_tasks.append(ScheduleTask(
                    id=b.id, # use block id as dummy task id
                    title=b.title or "Reserved",
                    estimated_duration_minutes=int((b.planned_end_at - b.planned_start_at).total_seconds() // 60),
                    priority="URGENT",
                    scheduling_type="FIXED",
                    fixed_start_at=b.planned_start_at,
                    fixed_end_at=b.planned_end_at,
                    created_at=now
                ))

        scheduler = DeterministicScheduler()
        result = scheduler.schedule(schedule_tasks, windows)

        # 4. Apply changes
        # Delete unpreserved blocks
        for b in blocks:
            if b not in preserved_blocks:
                await db.delete(b)

        # Add new blocks (ignore dummy tasks used for reservation)
        dummy_ids = {b.id for b in preserved_blocks}
        new_blocks = []
        for rb in result.blocks:
            if rb.task_id not in dummy_ids and rb.block_type != "FIXED_EVENT":
                new_blocks.append(PlanBlock(
                    daily_plan_id=plan.id,
                    task_id=rb.task_id if rb.block_type == "TASK" else None,
                    block_type=rb.block_type,
                    title=rb.title,
                    planned_start_at=rb.start_at,
                    planned_end_at=rb.end_at,
                    status="PLANNED",
                    created_by="SCHEDULER"
                ))
        
        for nb in new_blocks:
            db.add(nb)

        await db.flush()

        # Update positions
        all_blocks = preserved_blocks + new_blocks
        all_blocks.sort(key=lambda x: x.planned_start_at)
        
        for i, b in enumerate(all_blocks):
            b.position = i
            db.add(b)
            
        if commit:
            await db.commit()
            
        return await self.get_today(db, user_id, local_date)

today_service = TodayService()
