"""Scope: long-term direction. A goal and its ordered milestones form a roadmap."""

from __future__ import annotations

import uuid
from datetime import date, datetime
from typing import TYPE_CHECKING

from sqlalchemy import (
    CheckConstraint,
    Date,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
    UniqueConstraint,
    func,
    text,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

if TYPE_CHECKING:
    from app.db.models.garden import HeartEvent
    from app.db.models.reminders import Reminder
    from app.db.models.tasks import Task
    from app.db.models.users import User


class Goal(Base):
    __tablename__ = "goals"
    __table_args__ = (
        CheckConstraint("BTRIM(title) <> ''", name="goals_title_not_blank"),
        CheckConstraint(
            "status IN ('DRAFT', 'ACTIVE', 'ON_HOLD', 'COMPLETED', 'CANCELLED')",
            name="goals_status_valid",
        ),
        CheckConstraint(
            "(status = 'COMPLETED' AND completed_at IS NOT NULL)"
            " OR (status <> 'COMPLETED')",
            name="goals_completion_valid",
        ),
        Index("goals_user_status_idx", "user_id", "status", "target_date"),
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
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    roadmap_summary: Mapped[str | None] = mapped_column(Text)
    target_date: Mapped[date | None] = mapped_column(Date)
    status: Mapped[str] = mapped_column(
        String(20), nullable=False, server_default=text("'DRAFT'")
    )
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )

    user: Mapped[User] = relationship(back_populates="goals")
    milestones: Mapped[list[Milestone]] = relationship(
        back_populates="goal", passive_deletes=True
    )


class Milestone(Base):
    __tablename__ = "milestones"
    __table_args__ = (
        CheckConstraint("BTRIM(title) <> ''", name="milestones_title_not_blank"),
        CheckConstraint("position >= 0", name="milestones_position_valid"),
        CheckConstraint(
            "status IN ('PENDING', 'IN_PROGRESS', 'COMPLETED', 'SKIPPED', 'CANCELLED')",
            name="milestones_status_valid",
        ),
        CheckConstraint(
            "(status = 'COMPLETED' AND completed_at IS NOT NULL)"
            " OR (status <> 'COMPLETED')",
            name="milestones_completion_valid",
        ),
        UniqueConstraint(
            "goal_id", "position", name="milestones_goal_position_unique"
        ),
        Index("milestones_goal_due_idx", "goal_id", "due_at"),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default=text("gen_random_uuid()"),
    )
    goal_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("goals.id", ondelete="CASCADE"),
        nullable=False,
    )
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    expected_outcome: Mapped[str | None] = mapped_column(Text)
    due_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    position: Mapped[int] = mapped_column(Integer, nullable=False)
    status: Mapped[str] = mapped_column(
        String(20), nullable=False, server_default=text("'PENDING'")
    )
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )

    goal: Mapped[Goal] = relationship(back_populates="milestones")
    tasks: Mapped[list[Task]] = relationship(back_populates="milestone")
    reminders: Mapped[list[Reminder]] = relationship(
        back_populates="milestone", passive_deletes=True
    )
    heart_events: Mapped[list[HeartEvent]] = relationship(
        back_populates="source_milestone", passive_deletes=True
    )
