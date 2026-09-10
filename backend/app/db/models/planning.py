"""Scope: natural-language planning conversations in the full application."""

from __future__ import annotations

import uuid
from datetime import date, datetime
from typing import Any, TYPE_CHECKING

from sqlalchemy import (
    CheckConstraint,
    Date,
    DateTime,
    ForeignKey,
    Index,
    String,
    Text,
    func,
    text,
)
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

if TYPE_CHECKING:
    from app.db.models.daily_plans import DailyPlan
    from app.db.models.users import User


class PlanningSession(Base):
    __tablename__ = "planning_sessions"
    __table_args__ = (
        CheckConstraint(
            "session_type IN ('DAILY_PLAN', 'PLAN_EDIT', 'REPLAN', 'ROADMAP')",
            name="planning_sessions_type_valid",
        ),
        CheckConstraint(
            "status IN ('OPEN', 'AWAITING_CLARIFICATION', 'COMPLETED', 'CANCELLED')",
            name="planning_sessions_status_valid",
        ),
        CheckConstraint(
            "closed_at IS NULL OR closed_at >= created_at",
            name="planning_sessions_closed_at_valid",
        ),
        Index(
            "planning_sessions_user_recent_idx",
            "user_id",
            text("created_at DESC"),
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default=text("gen_random_uuid()"),
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )
    session_type: Mapped[str] = mapped_column(String(20), nullable=False)
    status: Mapped[str] = mapped_column(
        String(30), nullable=False, server_default=text("'OPEN'")
    )
    context_date: Mapped[date | None] = mapped_column(Date)
    closed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )

    user: Mapped[User] = relationship(back_populates="planning_sessions")
    messages: Mapped[list[PlanningMessage]] = relationship(
        back_populates="planning_session", passive_deletes=True
    )
    daily_plans: Mapped[list[DailyPlan]] = relationship(
        back_populates="planning_session", passive_deletes=True
    )


class PlanningMessage(Base):
    __tablename__ = "planning_messages"
    __table_args__ = (
        CheckConstraint(
            "role IN ('USER', 'ASSISTANT', 'SYSTEM')",
            name="planning_messages_role_valid",
        ),
        CheckConstraint(
            "BTRIM(content) <> ''", name="planning_messages_content_not_blank"
        ),
        CheckConstraint(
            "structured_payload IS NULL"
            " OR jsonb_typeof(structured_payload) = 'object'",
            name="planning_messages_payload_object",
        ),
        Index(
            "planning_messages_session_chronological_idx",
            "planning_session_id",
            "created_at",
            "id",
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default=text("gen_random_uuid()"),
    )
    planning_session_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("planning_sessions.id", ondelete="CASCADE"),
        nullable=False,
    )
    role: Mapped[str] = mapped_column(String(20), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    structured_payload: Mapped[dict[str, Any] | None] = mapped_column(JSONB)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )

    planning_session: Mapped[PlanningSession] = relationship(
        back_populates="messages"
    )
