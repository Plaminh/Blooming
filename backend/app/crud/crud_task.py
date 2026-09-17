from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.db.models.tasks import Task, TaskDependency
from app.schemas.planning import TaskCreate, TaskUpdate


class CRUDTask:
    async def create(
        self, db: AsyncSession, *, obj_in: TaskCreate, user_id: UUID
    ) -> Task:
        db_obj = Task(
            user_id=user_id,
            title=obj_in.title,
            description=obj_in.description,
            category=obj_in.category,
            estimated_duration_minutes=obj_in.estimated_duration_minutes,
            priority=obj_in.priority,
            scheduling_type=obj_in.scheduling_type,
            is_splittable=obj_in.is_splittable,
            min_split_duration_minutes=obj_in.min_split_duration_minutes,
            preferred_break_duration_minutes=obj_in.preferred_break_duration_minutes,
            fixed_start_at=obj_in.fixed_start_at,
            fixed_end_at=obj_in.fixed_end_at,
            deadline_at=obj_in.deadline_at,
            status="DRAFT",
        )
        db.add(db_obj)
        await db.flush()

        for dep_id in obj_in.dependencies:
            dep_obj = TaskDependency(task_id=db_obj.id, depends_on_task_id=dep_id)
            db.add(dep_obj)

        await db.flush()
        # Return loaded instance
        return await self.get(db, id=db_obj.id)

    async def get(self, db: AsyncSession, id: UUID) -> Task | None:
        result = await db.execute(
            select(Task).options(selectinload(Task.dependencies)).where(Task.id == id)
        )
        return result.scalars().first()

    async def get_with_plan_blocks(self, db: AsyncSession, id: UUID) -> Task | None:
        result = await db.execute(
            select(Task).options(
                selectinload(Task.dependencies),
                selectinload(Task.plan_blocks)
            ).where(Task.id == id)
        )
        return result.scalars().first()

    async def get_multi_by_user(
        self, db: AsyncSession, user_id: UUID, skip: int = 0, limit: int = 100
    ) -> list[Task]:
        result = await db.execute(
            select(Task)
            .options(selectinload(Task.dependencies))
            .where(Task.user_id == user_id)
            .offset(skip)
            .limit(limit)
        )
        return list(result.scalars().all())

    async def update(self, db: AsyncSession, *, db_obj: Task, obj_in: TaskUpdate) -> Task:
        update_data = obj_in.model_dump(exclude_unset=True)
        deps = update_data.pop("dependencies", None)

        if update_data:
            for field, value in update_data.items():
                setattr(db_obj, field, value)
            db.add(db_obj)

        if deps is not None:
            # Clear existing dependencies
            for existing_dep in list(db_obj.dependencies):
                await db.delete(existing_dep)
            # Add new ones
            for dep_id in deps:
                dep_obj = TaskDependency(task_id=db_obj.id, depends_on_task_id=dep_id)
                db.add(dep_obj)

        await db.flush()
        return await self.get(db, id=db_obj.id)

    async def delete(self, db: AsyncSession, *, id: UUID) -> Task | None:
        obj = await db.get(Task, id)
        if obj:
            await db.delete(obj)
            await db.flush()
        return obj


task = CRUDTask()
