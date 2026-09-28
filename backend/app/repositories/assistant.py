from datetime import datetime, timedelta, timezone
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.db.models.planning import PlanningMessage, PlanningSession
from app.db.models.users import User, UserSettings


class AssistantRepository:
    async def check_rate_limit(
        self, db: AsyncSession, user_id: UUID, limit: int, window_seconds: int = 60
    ) -> bool:
        now = datetime.now(timezone.utc)
        await db.execute(select(User.id).where(User.id == user_id).with_for_update())
        recent_count = await db.scalar(
            select(func.count(PlanningMessage.id))
            .join(
                PlanningSession,
                PlanningSession.id == PlanningMessage.planning_session_id,
            )
            .where(
                PlanningSession.user_id == user_id,
                PlanningMessage.role == "USER",
                PlanningMessage.created_at > now - timedelta(seconds=window_seconds),
            )
        )
        return int(recent_count or 0) >= limit

    async def get_session_by_id(
        self, db: AsyncSession, user_id: UUID, session_id: UUID
    ) -> PlanningSession | None:
        return await db.scalar(
            select(PlanningSession).where(
                PlanningSession.id == session_id,
                PlanningSession.user_id == user_id,
            )
        )

    async def create_session(
        self, db: AsyncSession, user_id: UUID, session_type: str = "DAILY_PLAN"
    ) -> PlanningSession:
        value = PlanningSession(
            user_id=user_id, session_type=session_type, status="OPEN"
        )
        db.add(value)
        await db.flush()
        return value

    async def get_session(
        self, db: AsyncSession, session_id: UUID, user_id: UUID
    ) -> PlanningSession | None:
        return await db.scalar(
            select(PlanningSession)
            .options(selectinload(PlanningSession.messages))
            .where(
                PlanningSession.id == session_id,
                PlanningSession.user_id == user_id,
            )
        )

    async def get_latest_session(
        self, db: AsyncSession, user_id: UUID
    ) -> PlanningSession | None:
        return await db.scalar(
            select(PlanningSession)
            .options(selectinload(PlanningSession.messages))
            .where(
                PlanningSession.user_id == user_id,
                PlanningSession.status.in_({"OPEN", "AWAITING_CLARIFICATION"}),
                PlanningSession.updated_at
                >= datetime.now(timezone.utc) - timedelta(hours=12),
            )
            .order_by(
                PlanningSession.updated_at.desc(), PlanningSession.created_at.desc()
            )
            .limit(1)
        )

    async def add_message(
        self,
        db: AsyncSession,
        session_id: UUID,
        role: str,
        content: str,
        payload: dict | None = None,
    ) -> PlanningMessage:
        kwargs = {"planning_session_id": session_id, "role": role, "content": content}
        if payload is not None:
            kwargs["structured_payload"] = payload
        else:
            from sqlalchemy import null

            kwargs["structured_payload"] = null()
        msg = PlanningMessage(**kwargs)
        db.add(msg)
        return msg

    async def get_recent_messages(
        self, db: AsyncSession, session_id: UUID, limit: int = 12
    ) -> list[PlanningMessage]:
        return list(
            (
                await db.scalars(
                    select(PlanningMessage)
                    .where(PlanningMessage.planning_session_id == session_id)
                    .order_by(
                        PlanningMessage.created_at.desc(), PlanningMessage.id.desc()
                    )
                    .limit(limit)
                )
            ).all()
        )

    async def get_user_settings(
        self, db: AsyncSession, user_id: UUID
    ) -> UserSettings | None:
        return await db.scalar(
            select(UserSettings).where(UserSettings.user_id == user_id)
        )

    async def get_optional_tasks(
        self, db: AsyncSession, user_id: UUID, task_ids: list[UUID]
    ):
        from app.db.models.tasks import Task

        return (
            await db.scalars(
                select(Task).where(
                    Task.id.in_(task_ids),
                    Task.user_id == user_id,
                    Task.importance == "OPTIONAL",
                )
            )
        ).all()

    async def get_recent_focus_outcomes(
        self, db: AsyncSession, user_id: UUID, limit: int = 2
    ):
        from app.db.models.focus import FocusRun

        return (
            await db.execute(
                select(FocusRun.id, FocusRun.outcome)
                .where(FocusRun.user_id == user_id, FocusRun.status == "ENDED")
                .order_by(FocusRun.ended_at.desc(), FocusRun.id.desc())
                .limit(limit)
            )
        ).all()


assistant_repo = AssistantRepository()
