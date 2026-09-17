from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.core.errors import ResourceNotFoundError, UnauthorizedOwnershipError
from app.db.models.goals import Goal, Milestone
from app.schemas.goals import GoalCreate, GoalUpdate, MilestoneCreate, MilestoneUpdate

class GoalsService:
    async def get_goal(self, db: AsyncSession, goal_id: UUID, user_id: UUID) -> Goal:
        result = await db.execute(
            select(Goal)
            .options(selectinload(Goal.milestones))
            .where(Goal.id == goal_id)
        )
        goal = result.scalars().first()
        if not goal:
            raise ResourceNotFoundError("Goal not found")
        if goal.user_id != user_id:
            raise UnauthorizedOwnershipError()
        return goal

    async def get_goals(self, db: AsyncSession, user_id: UUID) -> list[Goal]:
        result = await db.execute(
            select(Goal)
            .options(selectinload(Goal.milestones))
            .where(Goal.user_id == user_id)
            .order_by(Goal.created_at.desc())
        )
        return list(result.scalars().all())

    async def create_goal(self, db: AsyncSession, obj_in: GoalCreate, user_id: UUID) -> Goal:
        goal = Goal(
            user_id=user_id,
            title=obj_in.title,
            description=obj_in.description,
            roadmap_summary=obj_in.roadmap_summary,
            target_date=obj_in.target_date,
            status=obj_in.status
        )
        db.add(goal)
        await db.flush()
        
        # Need to return with loaded milestones
        return await self.get_goal(db, goal.id, user_id)

    async def update_goal(self, db: AsyncSession, goal_id: UUID, obj_in: GoalUpdate, user_id: UUID) -> Goal:
        goal = await self.get_goal(db, goal_id, user_id)
        
        update_data = obj_in.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(goal, field, value)
            
        await db.flush()
        return goal

    async def delete_goal(self, db: AsyncSession, goal_id: UUID, user_id: UUID) -> None:
        goal = await self.get_goal(db, goal_id, user_id)
        await db.delete(goal)
        await db.flush()

    # Milestone operations
    async def get_milestone(self, db: AsyncSession, goal_id: UUID, milestone_id: UUID, user_id: UUID) -> Milestone:
        goal = await self.get_goal(db, goal_id, user_id)
        result = await db.execute(
            select(Milestone).where(Milestone.id == milestone_id, Milestone.goal_id == goal_id)
        )
        milestone = result.scalars().first()
        if not milestone:
            raise ResourceNotFoundError("Milestone not found in this goal")
        return milestone

    async def create_milestone(self, db: AsyncSession, goal_id: UUID, obj_in: MilestoneCreate, user_id: UUID) -> Milestone:
        goal = await self.get_goal(db, goal_id, user_id)
        
        # Determine position (max + 1)
        max_pos = 0
        if goal.milestones:
            max_pos = max(m.position for m in goal.milestones) + 1
            
        milestone = Milestone(
            goal_id=goal_id,
            title=obj_in.title,
            description=obj_in.description,
            expected_outcome=obj_in.expected_outcome,
            due_at=obj_in.due_at,
            status=obj_in.status,
            position=max_pos
        )
        db.add(milestone)
        await db.flush()
        
        from datetime import datetime, timezone
        if milestone.due_at:
            # Auto-create reminder
            from app.db.models.reminders import Reminder
            reminder = Reminder(
                user_id=user_id,
                milestone_id=milestone.id,
                reminder_type="MILESTONE_DUE",
                message=f"Milestone Due: {milestone.title}",
                due_at=milestone.due_at,
                original_due_at=milestone.due_at,
                status="SCHEDULED" if milestone.due_at > datetime.now(timezone.utc) else "DUE"
            )
            db.add(reminder)
            await db.flush()
            
        return milestone

    async def update_milestone(self, db: AsyncSession, goal_id: UUID, milestone_id: UUID, obj_in: MilestoneUpdate, user_id: UUID) -> Milestone:
        milestone = await self.get_milestone(db, goal_id, milestone_id, user_id)
        
        update_data = obj_in.model_dump(exclude_unset=True)
        if 'due_at' in update_data and update_data['due_at'] != milestone.due_at:
            # Handle reminder sync if we move milestone
            # The spec says "Move milestone and synchronize its reminder."
            # We also need to update existing reminder if due_at changes
            pass # We will handle reminder syncing here or in reminders_service?
            # We'll just update it here for simplicity
            from app.db.models.reminders import Reminder
            result = await db.execute(
                select(Reminder).where(Reminder.milestone_id == milestone.id, Reminder.reminder_type == "MILESTONE_DUE")
            )
            reminders = result.scalars().all()
            for r in reminders:
                if r.status in ("SCHEDULED", "DUE"):
                    r.due_at = update_data['due_at']
                    r.original_due_at = update_data['due_at']
                    db.add(r)
        
        for field, value in update_data.items():
            setattr(milestone, field, value)
            
        await db.flush()
        return milestone

    async def delete_milestone(self, db: AsyncSession, goal_id: UUID, milestone_id: UUID, user_id: UUID) -> None:
        milestone = await self.get_milestone(db, goal_id, milestone_id, user_id)
        await db.delete(milestone)
        await db.flush()

goals_service = GoalsService()
