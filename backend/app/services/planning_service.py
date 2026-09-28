from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.errors import (
    CyclicDependencyError,
    ResourceNotFoundError,
    UnauthorizedOwnershipError,
    ValidationError,
)
from app.crud.crud_task import task as crud_task
from app.db.models.tasks import Task
from app.schemas.planning import TaskCreate, TaskUpdate


class PlanningService:
    async def validate_dependency_times(self, db, user_id, dependencies, fixed_start):
        for dep_id in dependencies:
            dep = await crud_task.get(db, id=dep_id, user_id=user_id)
            if not dep:
                raise ResourceNotFoundError("Dependency task not found")
            if (
                fixed_start
                and dep.status != "COMPLETED"
                and dep.fixed_end_at
                and dep.fixed_end_at > fixed_start
            ):
                raise ValidationError(
                    f"Dependency {dep_id} ends after the fixed task starts"
                )

    async def create_task(
        self, db: AsyncSession, obj_in: TaskCreate, user_id: UUID
    ) -> Task:
        if obj_in.dependencies:
            if len(set(obj_in.dependencies)) != len(obj_in.dependencies):
                raise ValidationError("Duplicate dependencies are not allowed")
            for dep_id in obj_in.dependencies:
                dep_task = await crud_task.get(db, id=dep_id, user_id=user_id)
                if not dep_task or dep_task.user_id != user_id:
                    raise ResourceNotFoundError("Dependency task not found")

        await self.validate_dependency_times(
            db, user_id, obj_in.dependencies, obj_in.fixed_start_at
        )
        task = await crud_task.create(db, obj_in=obj_in, user_id=user_id)
        await db.commit()
        return task

    async def update_task(
        self, db: AsyncSession, task_id: UUID, obj_in: TaskUpdate, user_id: UUID
    ) -> Task:
        db_obj = await crud_task.get(db, id=task_id, user_id=user_id)
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
            all_user_tasks = await crud_task.get_multi_by_user(
                db, user_id=user_id, limit=10000
            )
            user_task_ids = {t.id for t in all_user_tasks}

            for dep_id in obj_in.dependencies:
                if dep_id not in user_task_ids:
                    raise ResourceNotFoundError("Dependency task not found")

            task_dict = {
                t.id: [d.depends_on_task_id for d in t.dependencies]
                for t in all_user_tasks
            }
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

            visited: set[UUID] = set()
            path: set[UUID] = set()
            if dfs(task_id, visited, path):
                raise CyclicDependencyError("Cyclic dependency detected")

        # Validate merged state
        merged_scheduling_type = (
            obj_in.scheduling_type
            if obj_in.scheduling_type is not None
            else db_obj.scheduling_type
        )
        # obj_in can explicitly set these to None (e.g. changing FIXED to FLEXIBLE)
        merged_fixed_start = (
            obj_in.fixed_start_at
            if "fixed_start_at" in obj_in.model_fields_set
            else db_obj.fixed_start_at
        )
        merged_fixed_end = (
            obj_in.fixed_end_at
            if "fixed_end_at" in obj_in.model_fields_set
            else db_obj.fixed_end_at
        )

        if merged_scheduling_type == "FIXED":
            if not merged_fixed_start or not merged_fixed_end:
                raise ValidationError(
                    "FIXED tasks require fixed_start_at and fixed_end_at"
                )
            if merged_fixed_end <= merged_fixed_start:
                raise ValidationError(
                    "fixed_end_at must be strictly greater than fixed_start_at"
                )
        else:
            if merged_fixed_start or merged_fixed_end:
                raise ValidationError(
                    "FLEXIBLE tasks cannot have fixed start/end times"
                )

        merged_estimated_duration = (
            obj_in.estimated_duration_minutes
            if obj_in.estimated_duration_minutes is not None
            else db_obj.estimated_duration_minutes
        )
        merged_min_split = (
            obj_in.min_split_duration_minutes
            if "min_split_duration_minutes" in obj_in.model_fields_set
            else db_obj.min_split_duration_minutes
        )

        if merged_min_split is not None:
            if merged_min_split > merged_estimated_duration:
                raise ValidationError(
                    "min_split_duration_minutes cannot exceed estimated_duration_minutes"
                )

        dependencies = (
            obj_in.dependencies
            if obj_in.dependencies is not None
            else [d.depends_on_task_id for d in db_obj.dependencies]
        )
        await self.validate_dependency_times(
            db, user_id, dependencies, merged_fixed_start
        )
        task = await crud_task.update(db, db_obj=db_obj, obj_in=obj_in)
        await db.commit()
        return task

    async def get_task(self, db: AsyncSession, task_id: UUID, user_id: UUID) -> Task:
        db_obj = await crud_task.get(db, id=task_id, user_id=user_id)
        if not db_obj:
            raise ResourceNotFoundError("Task not found")
        if db_obj.user_id != user_id:
            raise UnauthorizedOwnershipError()
        return db_obj

    async def list_tasks(
        self, db: AsyncSession, user_id: UUID, skip: int = 0, limit: int = 100
    ) -> list[Task]:
        return await crud_task.get_multi_by_user(
            db, user_id=user_id, skip=skip, limit=limit
        )

    async def delete_task(self, db: AsyncSession, task_id: UUID, user_id: UUID) -> None:
        db_obj = await crud_task.get(db, id=task_id, user_id=user_id)
        if not db_obj:
            raise ResourceNotFoundError("Task not found")
        if db_obj.user_id != user_id:
            raise UnauthorizedOwnershipError()
        await crud_task.delete(db, id=task_id, user_id=user_id)
        await db.commit()

    from app.services.plans.timeline import generate_timeline, save_daily_plan

    generate_timeline = staticmethod(generate_timeline)
    save_daily_plan = staticmethod(save_daily_plan)


planning_service = PlanningService()
