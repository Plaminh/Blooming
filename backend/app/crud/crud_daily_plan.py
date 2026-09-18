from datetime import date
from uuid import UUID

from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.db.models.daily_plans import DailyPlan, PlanBlock


class CRUDDailyPlan:
    async def create_draft(self, db: AsyncSession, *, user_id: UUID, plan_date: date, timezone_snapshot: str, reality_check: str) -> DailyPlan:
        from app.core.errors import PlanAlreadyExistsError

        existing_plan = await self.get_by_date(db, user_id, plan_date)
        if existing_plan:
            if existing_plan.status in ("CONFIRMED", "ACTIVE"):
                raise PlanAlreadyExistsError("An active plan already exists for this date.")
            if existing_plan.status == "DRAFT":
                existing_plan.timezone_snapshot = timezone_snapshot
                existing_plan.reality_check = reality_check

                # cascade delete existing draft blocks/windows manually to be safe before replacing
                for b in list(existing_plan.plan_blocks):
                    await db.delete(b)
                for w in list(existing_plan.availability_windows):
                    await db.delete(w)

                await db.flush()
                return existing_plan

        db_obj = DailyPlan(
            user_id=user_id,
            plan_date=plan_date,
            timezone_snapshot=timezone_snapshot,
            reality_check=reality_check,
            status="DRAFT"
        )
        db.add(db_obj)
        await db.flush()
        return db_obj

    async def get_by_date(
        self, db: AsyncSession, user_id: UUID, plan_date: date
    ) -> DailyPlan | None:
        result = await db.execute(
            select(DailyPlan)
            .options(
                selectinload(DailyPlan.plan_blocks).selectinload(PlanBlock.task),
                selectinload(DailyPlan.availability_windows),
            )
            .where(and_(DailyPlan.user_id == user_id, DailyPlan.plan_date == plan_date))
        )
        return result.scalars().first()

    async def get(self, db: AsyncSession, id: UUID, user_id: UUID) -> DailyPlan | None:
        result = await db.execute(
            select(DailyPlan)
            .options(
                selectinload(DailyPlan.plan_blocks).selectinload(PlanBlock.task),
                selectinload(DailyPlan.availability_windows),
            )
            .where(DailyPlan.id == id, DailyPlan.user_id == user_id)
        )
        return result.scalars().first()


daily_plan = CRUDDailyPlan()
