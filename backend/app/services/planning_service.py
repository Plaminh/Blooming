from typing import Any
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.errors import CyclicDependencyError, ResourceNotFoundError, UnauthorizedOwnershipError, ValidationError
from app.core.scheduler import DeterministicScheduler, ScheduleTask, ScheduleWindow
from app.crud.crud_task import task as crud_task
from app.db.models.tasks import Task
from app.schemas.planning import TaskCreate, TaskUpdate

class PlanningService:
    async def create_task(self, db: AsyncSession, obj_in: TaskCreate, user_id: UUID) -> Task:
        if obj_in.dependencies:
            if len(set(obj_in.dependencies)) != len(obj_in.dependencies):
                raise ValidationError("Duplicate dependencies are not allowed")
            for dep_id in obj_in.dependencies:
                dep_task = await crud_task.get(db, id=dep_id)
                if not dep_task or dep_task.user_id != user_id:
                    raise UnauthorizedOwnershipError("Dependency task not found or unauthorized")

        return await crud_task.create(db, obj_in=obj_in, user_id=user_id)

    async def update_task(self, db: AsyncSession, task_id: UUID, obj_in: TaskUpdate, user_id: UUID) -> Task:
        db_obj = await crud_task.get(db, id=task_id)
        if not db_obj:
            raise ResourceNotFoundError("Task not found")
        if db_obj.user_id != user_id:
            raise UnauthorizedOwnershipError()

        if obj_in.dependencies is not None:
            # Reject duplicate dependencies
            if len(set(obj_in.dependencies)) != len(obj_in.dependencies):
                raise ValidationError("Duplicate dependencies are not allowed")

            # Check for self-dependency
            if task_id in obj_in.dependencies:
                raise CyclicDependencyError("Task cannot depend on itself")

            # Load all tasks for the user to detect cycles efficiently
            all_user_tasks = await crud_task.get_multi_by_user(db, user_id=user_id, limit=10000)
            user_task_ids = {t.id for t in all_user_tasks}

            for dep_id in obj_in.dependencies:
                if dep_id not in user_task_ids:
                    raise UnauthorizedOwnershipError("Dependency task not found or unauthorized")

            task_dict = {t.id: [d.depends_on_task_id for d in t.dependencies] for t in all_user_tasks}
            task_dict[task_id] = list(obj_in.dependencies)

            def dfs(node: UUID, visited: set, path: set) -> bool:
                if node in path:
                    return True
                if node in visited:
                    return False
                visited.add(node)
                path.add(node)
                for neighbor in task_dict.get(node, []):
                    if dfs(neighbor, visited, path):
                        return True
                path.remove(node)
                return False

            visited = set()
            path = set()
            if dfs(task_id, visited, path):
                raise CyclicDependencyError("Cyclic dependency detected")

        # Validate merged state
        merged_scheduling_type = obj_in.scheduling_type if obj_in.scheduling_type is not None else db_obj.scheduling_type
        # obj_in can explicitly set these to None (e.g. changing FIXED to FLEXIBLE)
        merged_fixed_start = obj_in.fixed_start_at if "fixed_start_at" in obj_in.model_fields_set else db_obj.fixed_start_at
        merged_fixed_end = obj_in.fixed_end_at if "fixed_end_at" in obj_in.model_fields_set else db_obj.fixed_end_at

        if merged_scheduling_type == 'FIXED':
            if not merged_fixed_start or not merged_fixed_end:
                raise ValidationError("FIXED tasks require fixed_start_at and fixed_end_at")
            if merged_fixed_end <= merged_fixed_start:
                raise ValidationError("fixed_end_at must be strictly greater than fixed_start_at")
        else:
            if merged_fixed_start or merged_fixed_end:
                raise ValidationError("FLEXIBLE tasks cannot have fixed start/end times")

        merged_estimated_duration = obj_in.estimated_duration_minutes if obj_in.estimated_duration_minutes is not None else db_obj.estimated_duration_minutes
        merged_min_split = obj_in.min_split_duration_minutes if "min_split_duration_minutes" in obj_in.model_fields_set else db_obj.min_split_duration_minutes

        if merged_min_split is not None:
            if merged_min_split > merged_estimated_duration:
                raise ValidationError("min_split_duration_minutes cannot exceed estimated_duration_minutes")

        return await crud_task.update(db, db_obj=db_obj, obj_in=obj_in)

    async def get_task(self, db: AsyncSession, task_id: UUID, user_id: UUID) -> Task:
        db_obj = await crud_task.get(db, id=task_id)
        if not db_obj:
            raise ResourceNotFoundError("Task not found")
        if db_obj.user_id != user_id:
            raise UnauthorizedOwnershipError()
        return db_obj

    async def list_tasks(self, db: AsyncSession, user_id: UUID, skip: int = 0, limit: int = 100) -> list[Task]:
        return await crud_task.get_multi_by_user(db, user_id=user_id, skip=skip, limit=limit)

    async def delete_task(self, db: AsyncSession, task_id: UUID, user_id: UUID) -> None:
        db_obj = await crud_task.get(db, id=task_id)
        if not db_obj:
            raise ResourceNotFoundError("Task not found")
        if db_obj.user_id != user_id:
            raise UnauthorizedOwnershipError()
        await crud_task.delete(db, id=task_id)

    async def generate_timeline(self, db: AsyncSession, request: Any, user_id: UUID) -> Any:
        if len(set(request.task_ids)) != len(request.task_ids):
            raise ValidationError("Duplicate task IDs are not allowed")

        from sqlalchemy import select
        from sqlalchemy.orm import selectinload

        # Load exactly the requested tasks
        result = await db.execute(
            select(Task)
            .options(selectinload(Task.dependencies))
            .where(Task.user_id == user_id, Task.id.in_(request.task_ids))
        )
        db_tasks = list(result.scalars().all())

        if len(db_tasks) != len(set(request.task_ids)):
            raise ValidationError("One or more requested tasks were not found or are not owned by the user")

        schedule_tasks = []
        for t in db_tasks:
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

        windows = [ScheduleWindow(start_at=w.start_at, end_at=w.end_at) for w in request.availability_windows]

        scheduler = DeterministicScheduler()
        result = scheduler.schedule(schedule_tasks, windows)

        from app.db.models.daily_plans import PlanBlock, AvailabilityWindow as DbAvailabilityWindow
        from app.crud.crud_daily_plan import daily_plan as crud_daily_plan

        # Determine reality check
        if result.unscheduled_tasks or any(r["code"] == "FIXED_TASK_OVERLAP" for r in result.reasons):
            reality_check = "OVERLOADED"
        else:
            buffer_ratio = 1.0
            if result.available_minutes > 0:
                buffer_ratio = (result.available_minutes - result.workload_minutes) / result.available_minutes
            if buffer_ratio >= 0.2:
                reality_check = "COMFORTABLE"
            else:
                reality_check = "TIGHT"

        # Persist draft
        draft_plan = await crud_daily_plan.create_draft(
            db,
            user_id=user_id,
            plan_date=request.plan_date,
            timezone_snapshot=request.timezone_snapshot,
            reality_check=reality_check
        )

        for w in request.availability_windows:
            db_w = DbAvailabilityWindow(
                daily_plan_id=draft_plan.id,
                available_start_at=w.start_at,
                available_end_at=w.end_at
            )
            db.add(db_w)

        draft_blocks = []
        for i, b in enumerate(result.blocks):
            db_b = PlanBlock(
                daily_plan_id=draft_plan.id,
                task_id=b.task_id,
                block_type=b.block_type,
                title=b.title,
                planned_start_at=b.start_at,
                planned_end_at=b.end_at,
                position=i,
                status="PLANNED",
                created_by="SCHEDULER"
            )
            db.add(db_b)
            draft_blocks.append(db_b)

        await db.flush()

        return {
            "draft_id": draft_plan.id,
            "blocks": [
                {
                    "block_type": b.block_type,
                    "planned_start_at": b.planned_start_at,
                    "planned_end_at": b.planned_end_at,
                    "task_id": b.task_id,
                    "title": b.title,
                    "position": b.position
                } for b in draft_blocks
            ],
            "reality_check": reality_check,
            "reality_check_reasons": result.reasons,
            "unscheduled_tasks": result.unscheduled_tasks
        }

    async def save_daily_plan(self, db: AsyncSession, request: Any, user_id: UUID) -> Any:
        from app.crud.crud_daily_plan import daily_plan as crud_daily_plan
        from app.core.errors import PlanAlreadyExistsError, ValidationError
        from datetime import datetime, timezone

        draft = await crud_daily_plan.get(db, request.draft_id)
        if not draft:
            raise ResourceNotFoundError("Timeline Draft not found")
        if draft.user_id != user_id:
            raise UnauthorizedOwnershipError("Unauthorized ownership")

        # Idempotency: if already confirmed, just return
        if draft.status in ("CONFIRMED", "ACTIVE"):
            return draft

        # Check for duplicate active plans
        existing_plan = await crud_daily_plan.get_by_date(db, user_id, draft.plan_date)
        if existing_plan and existing_plan.id != draft.id:
            if existing_plan.status in ("CONFIRMED", "ACTIVE"):
                if not getattr(request, "replace_existing", False):
                    raise PlanAlreadyExistsError("An active plan already exists for this date. Provide replace_existing=True to replace it.")
                # Replace existing plan
                existing_plan.status = "ARCHIVED"
                db.add(existing_plan)

        # Transition to CONFIRMED
        draft.status = "CONFIRMED"
        draft.confirmed_at = datetime.now(timezone.utc)
        db.add(draft)

        await db.commit()

        # Eager load plan_blocks before returning
        from sqlalchemy import select
        from sqlalchemy.orm import selectinload
        from app.db.models.daily_plans import DailyPlan
        result = await db.execute(
            select(DailyPlan)
            .options(selectinload(DailyPlan.plan_blocks))
            .where(DailyPlan.id == draft.id)
        )
        return result.scalars().first()

planning_service = PlanningService()
