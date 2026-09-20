from datetime import datetime, time, timezone
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.errors import ResourceNotFoundError, UnauthorizedOwnershipError
from app.core.time_utils import safe_timezone
from app.db.models.goals import Goal, Milestone
from app.db.models.planning import PlanningSession
from app.db.models.users import User, UserSettings
from app.schemas.goals import (
    GoalCreate,
    GoalUpdate,
    MilestoneCreate,
    MilestoneUpdate,
    RoadmapSave,
)


class GoalsService:
    async def create_from_roadmap(
        self, db: AsyncSession, obj_in: RoadmapSave, user_id: UUID
    ) -> Goal:
        """Create the full hierarchy in the caller's single transaction."""
        draft = obj_in.draft
        goal = Goal(
            user_id=user_id,
            title=draft.goalTitle,
            description=draft.goalDescription or None,
            roadmap_summary=draft.goalDescription or None,
            target_date=draft.targetDate,
            status="ACTIVE",
        )
        db.add(goal)
        await db.flush()
        from app.services.reminders_service import reminders_service

        user_settings = await db.scalar(
            select(UserSettings).where(UserSettings.user_id == user_id)
        )
        user_timezone = safe_timezone(user_settings.timezone if user_settings else "UTC")

        for position, item in enumerate(draft.milestones):
            due_at = datetime.combine(item.targetDate, time.max, tzinfo=user_timezone)
            due_at = due_at.astimezone(timezone.utc)
            milestone = Milestone(
                goal_id=goal.id,
                title=item.title,
                expected_outcome=item.expectedOutcome,
                due_at=due_at,
                status="PENDING",
                position=position,
            )
            db.add(milestone)
            await db.flush()
            await reminders_service.sync_milestone_reminder(
                db,
                user_id,
                milestone.id,
                milestone.title,
                milestone.due_at,
                milestone.status,
            )
        if obj_in.session_id:
            session = await db.scalar(
                select(PlanningSession).where(
                    PlanningSession.id == obj_in.session_id,
                    PlanningSession.user_id == user_id,
                )
            )
            if session is None:
                raise ResourceNotFoundError("Planning session not found")
            session.status = "COMPLETED"
            session.closed_at = datetime.now(timezone.utc)
        await db.flush()
        return await self.get_goal(db, goal.id, user_id)

    async def get_goal(self, db: AsyncSession, goal_id: UUID, user_id: UUID) -> Goal:
        result = await db.execute(
            select(Goal)
            .options(selectinload(Goal.milestones))
            .where(Goal.id == goal_id, Goal.user_id == user_id)
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

    async def create_goal(
        self, db: AsyncSession, obj_in: GoalCreate, user_id: UUID
    ) -> Goal:
        goal = Goal(
            user_id=user_id,
            title=obj_in.title,
            description=obj_in.description,
            roadmap_summary=obj_in.roadmap_summary,
            target_date=obj_in.target_date,
            status=obj_in.status,
        )
        db.add(goal)
        await db.flush()

        # Need to return with loaded milestones
        return await self.get_goal(db, goal.id, user_id)

    async def update_goal(
        self, db: AsyncSession, goal_id: UUID, obj_in: GoalUpdate, user_id: UUID
    ) -> Goal:
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
    async def get_milestone(
        self, db: AsyncSession, goal_id: UUID, milestone_id: UUID, user_id: UUID
    ) -> Milestone:
        await self.get_goal(db, goal_id, user_id)
        result = await db.execute(
            select(Milestone).where(
                Milestone.id == milestone_id, Milestone.goal_id == goal_id
            )
        )
        milestone = result.scalars().first()
        if not milestone:
            raise ResourceNotFoundError("Milestone not found in this goal")
        return milestone

    async def create_milestone(
        self, db: AsyncSession, goal_id: UUID, obj_in: MilestoneCreate, user_id: UUID
    ) -> Milestone:
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
            position=max_pos,
        )
        db.add(milestone)
        await db.flush()

        from app.services.reminders_service import reminders_service

        await reminders_service.sync_milestone_reminder(
            db,
            user_id,
            milestone.id,
            milestone.title,
            milestone.due_at,
            milestone.status,
        )

        return milestone

    async def update_milestone(
        self,
        db: AsyncSession,
        goal_id: UUID,
        milestone_id: UUID,
        obj_in: MilestoneUpdate,
        user_id: UUID,
    ) -> Milestone:
        await db.execute(select(User.id).where(User.id == user_id).with_for_update())
        milestone = await self.get_milestone(db, goal_id, milestone_id, user_id)

        update_data = obj_in.model_dump(exclude_unset=True)

        for field, value in update_data.items():
            setattr(milestone, field, value)

        if "status" in update_data:
            milestone.completed_at = (
                datetime.now(timezone.utc) if milestone.status == "COMPLETED" else None
            )
            if milestone.status == "COMPLETED":
                from app.core.economy import LEAVES_PER_MILESTONE
                from app.services.garden_service import award_resources

                await award_resources(
                    db,
                    user_id,
                    "LEAVES",
                    LEAVES_PER_MILESTONE,
                    "MILESTONE_COMPLETED",
                    f"milestone_completed_{milestone.id}",
                    milestone.id,
                )
        if {"due_at", "status", "title"} & update_data.keys():
            from app.services.reminders_service import reminders_service

            await reminders_service.sync_milestone_reminder(
                db,
                user_id,
                milestone.id,
                milestone.title,
                milestone.due_at,
                milestone.status,
                reactivate="status" in update_data
                and milestone.status not in ("COMPLETED", "CANCELLED"),
            )

        await db.flush()
        return milestone

    async def delete_milestone(
        self, db: AsyncSession, goal_id: UUID, milestone_id: UUID, user_id: UUID
    ) -> None:
        milestone = await self.get_milestone(db, goal_id, milestone_id, user_id)
        await db.delete(milestone)
        await db.flush()


goals_service = GoalsService()
