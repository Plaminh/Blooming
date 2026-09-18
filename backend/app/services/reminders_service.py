from datetime import datetime, timedelta, timezone
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.errors import (
    ResourceNotFoundError,
    UnauthorizedOwnershipError,
    ValidationError,
)
from app.core.time_utils import is_in_quiet_hours, safe_timezone
from app.db.models.reminders import Reminder, ReminderAction
from app.db.models.users import User, UserSettings
from app.schemas.reminders import ReminderActionRequest


class RemindersService:
    async def sync_milestone_reminder(
        self,
        db: AsyncSession,
        user_id: UUID,
        milestone_id: UUID,
        milestone_title: str,
        new_due_at: datetime | None,
        milestone_status: str,
        reactivate: bool = False,
    ) -> None:
        # User lock also serializes settings changes and concurrent milestone edits.
        await db.execute(select(User.id).where(User.id == user_id).with_for_update())
        now = datetime.now(timezone.utc)
        settings = await db.scalar(
            select(UserSettings).where(UserSettings.user_id == user_id)
        )
        lead = settings.milestone_reminder_lead_time_minutes if settings else 1440
        reminder_due_at = new_due_at - timedelta(minutes=lead) if new_due_at else None
        reminders = list(
            (
                await db.scalars(
                    select(Reminder)
                    .where(
                        Reminder.user_id == user_id,
                        Reminder.milestone_id == milestone_id,
                        Reminder.reminder_type == "MILESTONE_DUE",
                    )
                    .order_by(Reminder.created_at, Reminder.id)
                )
            ).all()
        )
        active = [r for r in reminders if r.status in ("SCHEDULED", "DUE")]
        if milestone_status in ("COMPLETED", "CANCELLED") or reminder_due_at is None:
            for reminder in active:
                reminder.status = (
                    "COMPLETED" if milestone_status == "COMPLETED" else "CANCELLED"
                )
                reminder.completed_at = now if milestone_status == "COMPLETED" else None
            await db.flush()
            return
        # Keep a single reminder per milestone; dismissed/completed actions stay acknowledged.
        reminder = (
            active[0]
            if active
            else next(
                (
                    r
                    for r in reminders
                    if r.status == "CANCELLED"
                    or (reactivate and r.status == "COMPLETED")
                ),
                None,
            )
        )
        for duplicate in active[1:]:
            duplicate.status = "CANCELLED"
        if reminder is None:
            if reminders:
                return
            reminder = Reminder(
                user_id=user_id,
                milestone_id=milestone_id,
                reminder_type="MILESTONE_DUE",
            )
            db.add(reminder)
        reminder.message = f"Milestone Due: {milestone_title}"
        reminder.due_at = reminder_due_at
        reminder.original_due_at = new_due_at
        reminder.status = "SCHEDULED" if reminder_due_at > now else "DUE"
        reminder.completed_at = None
        await db.flush()

    async def get_due_reminders(
        self, db: AsyncSession, user_id: UUID
    ) -> list[Reminder]:
        now = datetime.now(timezone.utc)
        settings = await db.scalar(
            select(UserSettings).where(UserSettings.user_id == user_id)
        )
        if settings:
            if not settings.reminders_enabled:
                return []
            local_time = now.astimezone(safe_timezone(settings.timezone))
            if settings.quiet_hours_enabled and is_in_quiet_hours(
                local_time, settings.quiet_hours_start, settings.quiet_hours_end
            ):
                return []

        result = await db.execute(
            select(Reminder)
            .where(
                Reminder.user_id == user_id,
                Reminder.status.in_(("SCHEDULED", "DUE")),
                Reminder.due_at <= now,
            )
            .order_by(Reminder.due_at.asc())
        )
        return list(result.scalars().all())

    async def execute_action(
        self,
        db: AsyncSession,
        reminder_id: UUID,
        obj_in: ReminderActionRequest,
        user_id: UUID,
    ) -> Reminder:
        await db.execute(select(User.id).where(User.id == user_id).with_for_update())
        result = await db.execute(select(Reminder).where(Reminder.id == reminder_id, Reminder.user_id == user_id))
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
            payload=obj_in.payload or {},
        )
        db.add(action_record)

        if action_type == "MARK_COMPLETED":
            reminder.status = "COMPLETED"
            reminder.completed_at = now
            # Update milestone status if applicable
            if reminder.milestone_id:
                from app.db.models.goals import Milestone

                ms_result = await db.execute(
                    select(Milestone).where(Milestone.id == reminder.milestone_id)
                )
                ms = ms_result.scalars().first()
                if ms:
                    ms.status = "COMPLETED"
                    ms.completed_at = now
                    db.add(ms)
                    from app.core.economy import LEAVES_PER_MILESTONE
                    from app.services.garden_service import award_resources

                    await award_resources(
                        db,
                        user_id,
                        "LEAVES",
                        LEAVES_PER_MILESTONE,
                        "MILESTONE_COMPLETED",
                        f"milestone_completed_{ms.id}",
                        ms.id,
                    )

        elif action_type == "MOVE_MILESTONE" or action_type == "REMIND_LATER":
            if not obj_in.new_due_at:
                raise ValidationError(f"{action_type} requires new_due_at")
            if action_type == "MOVE_MILESTONE" and reminder.milestone_id:
                from app.db.models.goals import Milestone

                ms = await db.get(Milestone, reminder.milestone_id)
                if ms:
                    ms.due_at = obj_in.new_due_at
                    await self.sync_milestone_reminder(
                        db, user_id, ms.id, ms.title, ms.due_at, ms.status
                    )
            else:
                reminder.due_at = obj_in.new_due_at
                reminder.status = "SCHEDULED" if reminder.due_at > now else "DUE"

        elif action_type == "CREATE_PLAN":
            from app.db.models.daily_plans import PlanBlock
            from app.db.models.tasks import Task
            from app.crud.crud_daily_plan import daily_plan as crud_daily_plan
            from app.core.errors import PlanAlreadyExistsError

            settings = await db.scalar(
                select(UserSettings).where(UserSettings.user_id == user_id)
            )
            tz = safe_timezone(settings.timezone if settings else "UTC")
            local_date = now.astimezone(tz).date()

            try:
                plan = await crud_daily_plan.create_draft(
                    db,
                    user_id=user_id,
                    plan_date=local_date,
                    timezone_snapshot=settings.timezone if settings else "UTC",
                    reality_check="COMFORTABLE",
                )
                plan_created = True
            except PlanAlreadyExistsError:
                plan_created = False

            reminder.status = "COMPLETED"
            reminder.completed_at = now

            if plan_created:
                task = Task(
                    user_id=user_id,
                    milestone_id=reminder.milestone_id,
                    title=f"Work on {reminder.message}",
                    estimated_duration_minutes=30,
                    priority="HIGH",
                    status="DRAFT",
                )
                db.add(task)
                await db.flush()

                block = PlanBlock(
                    daily_plan_id=plan.id,
                    task_id=task.id,
                    title=task.title,
                    block_type="TASK",
                    planned_start_at=now,
                    planned_end_at=now + timedelta(minutes=30),
                    position=0,
                    status="PLANNED",
                )
                db.add(block)

        db.add(reminder)
        await db.flush()
        return reminder


reminders_service = RemindersService()
