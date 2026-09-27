from datetime import datetime, time, timezone
import hashlib
from uuid import UUID
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

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
        settings_row = await db.scalar(
            select(UserSettings).where(UserSettings.user_id == user_id)
        )
        try:
            user_timezone = ZoneInfo(settings_row.timezone if settings_row else "UTC")
        except ZoneInfoNotFoundError:
            user_timezone = ZoneInfo("UTC")
        if draft.targetDate < datetime.now(user_timezone).date():
            raise ValueError("Roadmap target date cannot be in the past")
        await db.execute(select(User.id).where(User.id == user_id).with_for_update())
        key = obj_in.idempotency_key or (
            str(obj_in.session_id)
            if obj_in.session_id
            else hashlib.sha256(draft.model_dump_json().encode()).hexdigest()
        )
        existing = await db.scalar(
            select(Goal).where(
                Goal.user_id == user_id,
                Goal.source_idempotency_key == key,
            )
        )
        if existing is not None:
            return await self.get_goal(db, existing.id, user_id)

        session: PlanningSession | None = None
        if obj_in.session_id:
            session = await db.scalar(
                select(PlanningSession).where(
                    PlanningSession.id == obj_in.session_id,
                    PlanningSession.user_id == user_id,
                )
            )
            if session is None:
                raise ResourceNotFoundError("Planning session not found")
            if session.status not in {"OPEN", "AWAITING_CLARIFICATION"}:
                raise ValueError("Planning session is not open for saving")
        goal = Goal(
            user_id=user_id,
            title=draft.goalTitle,
            description=draft.goalDescription or None,
            roadmap_summary=draft.goalDescription or None,
            target_date=draft.targetDate,
            status="ACTIVE",
            source_idempotency_key=key,
        )
        db.add(goal)
        await db.flush()
        from app.services.reminders_service import reminders_service

        user_settings = await db.scalar(
            select(UserSettings).where(UserSettings.user_id == user_id)
        )
        user_timezone = safe_timezone(
            user_settings.timezone if user_settings else "UTC"
        )

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
        if session is not None:
            session.status = "COMPLETED"
            session.closed_at = datetime.now(timezone.utc)
        await db.flush()
        return await self.get_goal(db, goal.id, user_id)

    async def update_from_roadmap(
        self, db: AsyncSession, goal_id: UUID, obj_in: RoadmapSave, user_id: UUID
    ) -> Goal:
        from app.services.reminders_service import reminders_service
        from app.db.models.planning import PlanningSession
        from app.core.time_utils import safe_timezone
        from datetime import datetime, time, timezone
        from app.db.models.tasks import Task
        from sqlalchemy import update
        import hashlib

        draft = obj_in.draft
        goal = await self.get_goal(db, goal_id, user_id)

        key = obj_in.idempotency_key or (
            str(obj_in.session_id)
            if obj_in.session_id
            else hashlib.sha256(draft.model_dump_json().encode()).hexdigest()
        )
        if goal.source_idempotency_key == key:
            return goal

        session: PlanningSession | None = None
        if obj_in.session_id:
            session = await db.scalar(
                select(PlanningSession).where(
                    PlanningSession.id == obj_in.session_id,
                    PlanningSession.user_id == user_id,
                )
            )
            if session is None:
                raise ResourceNotFoundError("Planning session not found")
            if session.status not in {"OPEN", "AWAITING_CLARIFICATION"}:
                raise ValueError("Planning session is not open for saving")
                
        user_settings = await db.scalar(
            select(UserSettings).where(UserSettings.user_id == user_id)
        )
        user_timezone = safe_timezone(
            user_settings.timezone if user_settings else "UTC"
        )
        
        goal.title = draft.goalTitle
        goal.description = draft.goalDescription or None
        goal.target_date = draft.targetDate
        goal.source_idempotency_key = key
        
        existing_milestones = {str(m.id): m for m in goal.milestones}
        draft_milestone_ids = {str(i.id) for i in draft.milestones if i.id}
        preserved_completed = [
            m for m in goal.milestones 
            if m.status == "COMPLETED" and str(m.id) not in draft_milestone_ids
        ]
        
        if goal.milestones:
            offset = max((m.position for m in goal.milestones), default=0) + 1
            for m in goal.milestones:
                m.position = m.position + offset
            
            await db.flush()

        new_ids = set()
        
        current_position = 0
        for m in preserved_completed:
            m.position = current_position
            new_ids.add(str(m.id))
            current_position += 1
            
        for item in draft.milestones:
            due_at = datetime.combine(item.targetDate, time.max, tzinfo=user_timezone)
            due_at = due_at.astimezone(timezone.utc)
            
            if item.id and item.id in existing_milestones:
                m = existing_milestones[item.id]
                m.position = current_position
                new_ids.add(item.id)
                
                if m.status != "COMPLETED":
                    m.title = item.title
                    m.expected_outcome = item.expectedOutcome
                    m.due_at = due_at
                    
                    await reminders_service.sync_milestone_reminder(
                        db, user_id, m.id, m.title, m.due_at, m.status, reactivate=True
                    )
            else:
                m = Milestone(
                    goal_id=goal.id,
                    title=item.title,
                    expected_outcome=item.expectedOutcome,
                    due_at=due_at,
                    status="PENDING",
                    position=current_position,
                )
                db.add(m)
                await db.flush()
                await reminders_service.sync_milestone_reminder(
                    db, user_id, m.id, m.title, m.due_at, m.status
                )
            current_position += 1
        
        for m in goal.milestones:
            if str(m.id) not in new_ids:
                m.status = "CANCELLED"
                await reminders_service.sync_milestone_reminder(
                    db, user_id, m.id, m.title, m.due_at, m.status
                )
                await db.execute(
                    update(Task).where(Task.milestone_id == m.id).values(milestone_id=None)
                )
                await db.delete(m)
                
        if session is not None:
            session.status = "COMPLETED"
            session.closed_at = datetime.now(timezone.utc)
            
        await db.flush()
        return await self.get_goal(db, goal.id, user_id)

    async def get_goal(self, db: AsyncSession, goal_id: UUID, user_id: UUID) -> Goal:
        result = await db.execute(
            select(Goal)
            .options(selectinload(Goal.milestones))
            .where(Goal.id == goal_id, Goal.user_id == user_id)
            .execution_options(populate_existing=True)
        )
        goal = result.scalars().first()
        if not goal:
            raise ResourceNotFoundError("Goal not found")
        if goal.user_id != user_id:
            raise UnauthorizedOwnershipError()
            
        from app.core.time_utils import safe_timezone
        user_settings = await db.scalar(
            select(UserSettings).where(UserSettings.user_id == user_id)
        )
        user_tz = safe_timezone(user_settings.timezone if user_settings else "UTC")
        
        for m in goal.milestones:
            if m.due_at:
                m.target_date = m.due_at.astimezone(user_tz).date()
            else:
                m.target_date = None
                
        return goal

    async def get_goal_draft(self, db: AsyncSession, goal_id: UUID, user_id: UUID) -> "RoadmapDraft":
        from app.schemas.drafts import RoadmapDraft, MilestoneDraft
        from app.core.time_utils import safe_timezone
        goal = await self.get_goal(db, goal_id, user_id)
        
        user_settings = await db.scalar(
            select(UserSettings).where(UserSettings.user_id == user_id)
        )
        user_timezone = safe_timezone(
            user_settings.timezone if user_settings else "UTC"
        )
        
        milestones = sorted(goal.milestones, key=lambda m: m.position)
        
        return RoadmapDraft(
            type="roadmap",
            goalId=str(goal.id),
            goalTitle=goal.title,
            goalDescription=goal.description or "",
            targetDate=goal.target_date,
            milestones=[
                MilestoneDraft(
                    id=str(m.id),
                    title=m.title,
                    targetDate=m.due_at.astimezone(user_timezone).date() if m.due_at else m.due_at,
                    expectedOutcome=m.expected_outcome,
                    status=m.status,
                    completedAt=m.completed_at
                ) for m in milestones
            ]
        )

    async def get_goals(self, db: AsyncSession, user_id: UUID) -> list[Goal]:
        result = await db.execute(
            select(Goal)
            .options(selectinload(Goal.milestones))
            .where(Goal.user_id == user_id)
            .order_by(Goal.created_at.desc())
        )
        goals = list(result.scalars().all())
        
        from app.core.time_utils import safe_timezone
        user_settings = await db.scalar(
            select(UserSettings).where(UserSettings.user_id == user_id)
        )
        user_tz = safe_timezone(user_settings.timezone if user_settings else "UTC")
        
        for goal in goals:
            for m in goal.milestones:
                if m.due_at:
                    m.target_date = m.due_at.astimezone(user_tz).date()
                else:
                    m.target_date = None
                    
        return goals

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

        due_at = obj_in.due_at
        if getattr(obj_in, "target_date", None):
            from app.core.time_utils import safe_timezone
            user_settings = await db.scalar(
                select(UserSettings).where(UserSettings.user_id == user_id)
            )
            user_tz = safe_timezone(user_settings.timezone if user_settings else "UTC")
            due_at = datetime.combine(obj_in.target_date, time.max, tzinfo=user_tz).astimezone(timezone.utc)

        milestone = Milestone(
            goal_id=goal_id,
            title=obj_in.title,
            description=obj_in.description,
            expected_outcome=obj_in.expected_outcome,
            due_at=due_at,
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

        if "target_date" in update_data:
            target_date = update_data.pop("target_date")
            if target_date:
                from app.core.time_utils import safe_timezone
                user_settings = await db.scalar(
                    select(UserSettings).where(UserSettings.user_id == user_id)
                )
                user_tz = safe_timezone(user_settings.timezone if user_settings else "UTC")
                due_at = datetime.combine(target_date, time.max, tzinfo=user_tz)
                update_data["due_at"] = due_at.astimezone(timezone.utc)
            else:
                update_data["due_at"] = None

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
