from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.errors import ResourceNotFoundError, UnauthorizedOwnershipError, ValidationError
from app.db.models.reminders import Reminder, ReminderAction
from app.schemas.reminders import ReminderActionRequest

class RemindersService:
    async def sync_milestone_reminder(
        self,
        db: AsyncSession,
        user_id: UUID,
        milestone_id: UUID,
        milestone_title: str,
        new_due_at: datetime | None,
        milestone_status: str
    ) -> None:
        now = datetime.now(timezone.utc)
        result = await db.execute(
            select(Reminder)
            .where(Reminder.milestone_id == milestone_id, Reminder.reminder_type == "MILESTONE_DUE")
            .where(Reminder.status.in_(("SCHEDULED", "DUE")))
        )
        reminders = result.scalars().all()
        
        if milestone_status == "COMPLETED":
            for r in reminders:
                r.status = "COMPLETED"
                r.completed_at = now
                db.add(r)
            return

        if new_due_at is None:
            for r in reminders:
                r.status = "CANCELLED"
                db.add(r)
            return

        if reminders:
            for r in reminders:
                r.due_at = new_due_at
                r.original_due_at = new_due_at
                r.status = "SCHEDULED" if new_due_at > now else "DUE"
                db.add(r)
        else:
            reminder = Reminder(
                user_id=user_id,
                milestone_id=milestone_id,
                reminder_type="MILESTONE_DUE",
                message=f"Milestone Due: {milestone_title}",
                due_at=new_due_at,
                original_due_at=new_due_at,
                status="SCHEDULED" if new_due_at > now else "DUE"
            )
            db.add(reminder)

    async def get_due_reminders(self, db: AsyncSession, user_id: UUID) -> list[Reminder]:
        now = datetime.now(timezone.utc)
        result = await db.execute(
            select(Reminder)
            .where(
                Reminder.user_id == user_id,
                Reminder.status.in_(("SCHEDULED", "DUE")),
                Reminder.due_at <= now
            )
            .order_by(Reminder.due_at.asc())
        )
        return list(result.scalars().all())

    async def execute_action(self, db: AsyncSession, reminder_id: UUID, obj_in: ReminderActionRequest, user_id: UUID) -> Reminder:
        result = await db.execute(select(Reminder).where(Reminder.id == reminder_id))
        reminder = result.scalars().first()
        
        if not reminder:
            raise ResourceNotFoundError("Reminder not found")
        if reminder.user_id != user_id:
            raise UnauthorizedOwnershipError()

        if reminder.status in ("COMPLETED", "DISMISSED", "CANCELLED"):
            # Idempotent return or error, the spec says "prevent duplicate execution"
            # Return current state to be idempotent
            return reminder
            
        action_type = obj_in.action_type
        now = datetime.now(timezone.utc)
        
        # Record the action
        action_record = ReminderAction(
            reminder_id=reminder.id,
            action_type=action_type,
            previous_due_at=reminder.due_at,
            new_due_at=obj_in.new_due_at,
            payload=obj_in.payload
        )
        db.add(action_record)

        if action_type == "MARK_COMPLETED":
            reminder.status = "COMPLETED"
            reminder.completed_at = now
            # Update milestone status if applicable
            if reminder.milestone_id:
                from app.db.models.goals import Milestone
                ms_result = await db.execute(select(Milestone).where(Milestone.id == reminder.milestone_id))
                ms = ms_result.scalars().first()
                if ms:
                    ms.status = "COMPLETED"
                    ms.completed_at = now
                    db.add(ms)

        elif action_type == "MOVE_MILESTONE" or action_type == "REMIND_LATER":
            if not obj_in.new_due_at:
                raise ValidationError(f"{action_type} requires new_due_at")
            reminder.due_at = obj_in.new_due_at
            if action_type == "MOVE_MILESTONE":
                reminder.original_due_at = obj_in.new_due_at
                if reminder.milestone_id:
                    from app.db.models.goals import Milestone
                    ms_result = await db.execute(select(Milestone).where(Milestone.id == reminder.milestone_id))
                    ms = ms_result.scalars().first()
                    if ms:
                        ms.due_at = obj_in.new_due_at
                        db.add(ms)
                        
            # If the new date is in the future, set to SCHEDULED
            if obj_in.new_due_at > now:
                reminder.status = "SCHEDULED"

        elif action_type == "CREATE_PLAN":
            # Delegate plan creation to planning service if needed, or inline for small scope
            # "Define the smallest valid plan that can be created from reminder context."
            reminder.status = "COMPLETED"
            reminder.completed_at = now
            
            from app.db.models.tasks import Task
            from app.db.models.daily_plans import DailyPlan, PlanBlock
            
            task = Task(
                user_id=user_id,
                milestone_id=reminder.milestone_id,
                title=f"Work on {reminder.message}",
                estimated_duration_minutes=30,
                priority="HIGH",
                status="DRAFT"
            )
            db.add(task)
            await db.flush()
            
            plan = DailyPlan(
                user_id=user_id,
                plan_date=now.date(),
                status="DRAFT",
                reality_check="COMFORTABLE"
            )
            db.add(plan)
            await db.flush()
            
            block = PlanBlock(
                daily_plan_id=plan.id,
                task_id=task.id,
                title=task.title,
                block_type="FLEXIBLE",
                status="PLANNED"
            )
            db.add(block)

        db.add(reminder)
        await db.flush()
        return reminder

reminders_service = RemindersService()
