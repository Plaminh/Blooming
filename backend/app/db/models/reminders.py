"""Scope: server-stored reminder definitions synchronized to Tauri for local timing."""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any, TYPE_CHECKING

from sqlalchemy import (
    CheckConstraint,
    DateTime,
    ForeignKey,
    Index,
    String,
    func,
    text,
)
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

if TYPE_CHECKING:
    from app.db.models.daily_plans import PlanBlock
    from app.db.models.goals import Milestone
    from app.db.models.users import User


class Reminder(Base):
    __tablename__ = "reminders"
    __table_args__ = (
        CheckConstraint(
            "reminder_type IN ('PLAN_BLOCK_START', 'MILESTONE_DUE', 'CUSTOM')",
            name="reminders_type_valid",
        ),
        CheckConstraint("BTRIM(message) <> ''", name="reminders_message_not_blank"),
        CheckConstraint(
            "status IN ('SCHEDULED', 'DUE', 'COMPLETED', 'DISMISSED', 'CANCELLED')",
            name="reminders_status_valid",
        ),
        CheckConstraint(
            "(reminder_type = 'PLAN_BLOCK_START' AND plan_block_id IS NOT NULL"
            " AND milestone_id IS NULL)"
            " OR (reminder_type = 'MILESTONE_DUE' AND milestone_id IS NOT NULL"
            " AND plan_block_id IS NULL)"
            " OR (reminder_type = 'CUSTOM' AND milestone_id IS NULL"
            " AND plan_block_id IS NULL)",
            name="reminders_target_valid",
        ),
        CheckConstraint(
            "(status = 'COMPLETED' AND completed_at IS NOT NULL)"
            " OR status <> 'COMPLETED'",
            name="reminders_completion_valid",
        ),
        CheckConstraint(
            "(status = 'DISMISSED' AND dismissed_at IS NOT NULL)"
            " OR status <> 'DISMISSED'",
            name="reminders_dismissal_valid",
        ),
        Index(
            "reminders_user_sync_idx",
            "user_id",
            "due_at",
            postgresql_where=text("status IN ('SCHEDULED', 'DUE')"),
        ),
        Index(
            "reminders_user_unread_due_idx",
            "user_id",
            "due_at",
            postgresql_where=text("status = 'DUE' AND viewed_at IS NULL"),
        ),
        Index(
            "reminders_milestone_idx",
            "milestone_id",
            postgresql_where=text("milestone_id IS NOT NULL"),
        ),
        Index(
            "reminders_plan_block_idx",
            "plan_block_id",
            postgresql_where=text("plan_block_id IS NOT NULL"),
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
    milestone_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("milestones.id", ondelete="CASCADE"),
    )
    plan_block_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("plan_blocks.id", ondelete="CASCADE"),
    )
    reminder_type: Mapped[str] = mapped_column(String(30), nullable=False)
    message: Mapped[str] = mapped_column(String(300), nullable=False)
    due_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    original_due_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )
    status: Mapped[str] = mapped_column(
        String(20), nullable=False, server_default=text("'SCHEDULED'")
    )
    viewed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    dismissed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )

    user: Mapped[User] = relationship(back_populates="reminders")
    milestone: Mapped[Milestone | None] = relationship(back_populates="reminders")
    plan_block: Mapped[PlanBlock | None] = relationship(back_populates="reminders")
    actions: Mapped[list[ReminderAction]] = relationship(
        back_populates="reminder", passive_deletes=True
    )


class ReminderAction(Base):
    __tablename__ = "reminder_actions"
    __table_args__ = (
        CheckConstraint(
            "action_type IN ('VIEWED', 'START_FOCUS', 'REMIND_LATER',"
            " 'OPEN_BLOOMING', 'CREATE_PLAN', 'MARK_COMPLETED', 'MOVE_MILESTONE',"
            " 'DISMISS', 'COMPLETE')",
            name="reminder_actions_type_valid",
        ),
        CheckConstraint(
            "action_type <> 'REMIND_LATER'"
            " OR (new_due_at IS NOT NULL AND previous_due_at IS NOT NULL"
            " AND new_due_at > previous_due_at)",
            name="reminder_actions_snooze_time_valid",
        ),
        CheckConstraint(
            "payload IS NULL OR jsonb_typeof(payload) = 'object'",
            name="reminder_actions_payload_object",
        ),
        Index(
            "reminder_actions_reminder_recent_idx",
            "reminder_id",
            text("created_at DESC"),
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default=text("gen_random_uuid()"),
    )
    reminder_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("reminders.id", ondelete="CASCADE"),
        nullable=False,
    )
    action_type: Mapped[str] = mapped_column(String(30), nullable=False)
    previous_due_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    new_due_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    payload: Mapped[dict[str, Any] | None] = mapped_column(JSONB)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )

    reminder: Mapped[Reminder] = relationship(back_populates="actions")
