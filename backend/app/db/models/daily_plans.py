"""Scope: a user's confirmed daily schedule and its revision history."""

from __future__ import annotations

import uuid
from datetime import date, datetime
from typing import Any, TYPE_CHECKING

from sqlalchemy import (
    Boolean,
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
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

if TYPE_CHECKING:
    from app.db.models.focus import FocusRun
    from app.db.models.garden import RewardEvent
    from app.db.models.planning import PlanningSession
    from app.db.models.reminders import Reminder
    from app.db.models.tasks import Task
    from app.db.models.users import User


class DailyPlan(Base):
    __tablename__ = "daily_plans"
    __table_args__ = (
        CheckConstraint(
            "status IN ('DRAFT', 'CONFIRMED', 'ACTIVE', 'COMPLETED', 'ARCHIVED')",
            name="daily_plans_status_valid",
        ),
        CheckConstraint(
            "reality_check IS NULL"
            " OR reality_check IN ('COMFORTABLE', 'TIGHT', 'OVERLOADED')",
            name="daily_plans_reality_check_valid",
        ),
        CheckConstraint(
            "BTRIM(timezone_snapshot) <> ''", name="daily_plans_timezone_not_blank"
        ),
        CheckConstraint(
            "status = 'DRAFT' OR confirmed_at IS NOT NULL",
            name="daily_plans_confirmation_valid",
        ),
        CheckConstraint(
            "(status = 'COMPLETED' AND completed_at IS NOT NULL)"
            " OR (status <> 'COMPLETED')",
            name="daily_plans_completion_valid",
        ),
        Index(
            "daily_plans_one_active_per_local_date",
            "user_id",
            "plan_date",
            unique=True,
            postgresql_where=text("status IN ('DRAFT', 'CONFIRMED', 'ACTIVE')"),
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
    planning_session_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("planning_sessions.id", ondelete="SET NULL"),
    )
    plan_date: Mapped[date] = mapped_column(Date, nullable=False)
    status: Mapped[str] = mapped_column(
        String(20), nullable=False, server_default=text("'DRAFT'")
    )
    reality_check: Mapped[str | None] = mapped_column(String(20))
    timezone_snapshot: Mapped[str] = mapped_column(String(64), nullable=False)
    confirmed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )

    user: Mapped[User] = relationship(back_populates="daily_plans")
    planning_session: Mapped[PlanningSession | None] = relationship(
        back_populates="daily_plans"
    )
    availability_windows: Mapped[list[AvailabilityWindow]] = relationship(
        back_populates="daily_plan", passive_deletes=True
    )
    plan_blocks: Mapped[list[PlanBlock]] = relationship(
        back_populates="daily_plan", passive_deletes=True
    )
    revisions: Mapped[list[PlanRevision]] = relationship(
        back_populates="daily_plan", passive_deletes=True
    )


class AvailabilityWindow(Base):
    __tablename__ = "availability_windows"
    __table_args__ = (
        CheckConstraint(
            "available_end_at > available_start_at",
            name="availability_windows_range_valid",
        ),
        UniqueConstraint(
            "daily_plan_id",
            "available_start_at",
            "available_end_at",
            name="availability_windows_unique",
        ),
        Index(
            "availability_windows_plan_start_idx",
            "daily_plan_id",
            "available_start_at",
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default=text("gen_random_uuid()"),
    )
    daily_plan_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("daily_plans.id", ondelete="CASCADE"),
        nullable=False,
    )
    available_start_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )
    available_end_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )

    daily_plan: Mapped[DailyPlan] = relationship(
        back_populates="availability_windows"
    )


class PlanBlock(Base):
    __tablename__ = "plan_blocks"
    __table_args__ = (
        CheckConstraint(
            "block_type IN ('TASK', 'BREAK', 'BUFFER', 'FIXED_EVENT')",
            name="plan_blocks_type_valid",
        ),
        CheckConstraint(
            "planned_end_at > planned_start_at", name="plan_blocks_range_valid"
        ),
        CheckConstraint("position >= 0", name="plan_blocks_position_valid"),
        CheckConstraint(
            "status IN ('PLANNED', 'ACTIVE', 'COMPLETED', 'SKIPPED', 'CANCELLED')",
            name="plan_blocks_status_valid",
        ),
        CheckConstraint(
            "created_by IN ('SCHEDULER', 'USER')", name="plan_blocks_creator_valid"
        ),
        CheckConstraint(
            "(block_type = 'TASK' AND task_id IS NOT NULL)"
            " OR (block_type <> 'TASK' AND task_id IS NULL)",
            name="plan_blocks_task_link_valid",
        ),
        CheckConstraint(
            "block_type = 'TASK' OR (title IS NOT NULL AND BTRIM(title) <> '')",
            name="plan_blocks_non_task_title",
        ),
        CheckConstraint(
            "(status = 'COMPLETED' AND completed_at IS NOT NULL)"
            " OR (status <> 'COMPLETED')",
            name="plan_blocks_completion_valid",
        ),
        UniqueConstraint(
            "daily_plan_id", "position", name="plan_blocks_position_unique"
        ),
        Index(
            "plan_blocks_plan_timeline_idx",
            "daily_plan_id",
            "planned_start_at",
            "planned_end_at",
        ),
        Index(
            "plan_blocks_task_idx",
            "task_id",
            postgresql_where=text("task_id IS NOT NULL"),
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default=text("gen_random_uuid()"),
    )
    daily_plan_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("daily_plans.id", ondelete="CASCADE"),
        nullable=False,
    )
    task_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("tasks.id", ondelete="CASCADE"),
    )
    block_type: Mapped[str] = mapped_column(String(20), nullable=False)
    title: Mapped[str | None] = mapped_column(String(200))
    planned_start_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )
    planned_end_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )
    position: Mapped[int] = mapped_column(Integer, nullable=False)
    status: Mapped[str] = mapped_column(
        String(20), nullable=False, server_default=text("'PLANNED'")
    )
    is_locked: Mapped[bool] = mapped_column(
        Boolean, nullable=False, server_default=text("FALSE")
    )
    created_by: Mapped[str] = mapped_column(
        String(20), nullable=False, server_default=text("'SCHEDULER'")
    )
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )

    daily_plan: Mapped[DailyPlan] = relationship(back_populates="plan_blocks")
    task: Mapped[Task | None] = relationship(back_populates="plan_blocks")
    focus_runs: Mapped[list[FocusRun]] = relationship(back_populates="plan_block")
    reminders: Mapped[list[Reminder]] = relationship(
        back_populates="plan_block", passive_deletes=True
    )


class PlanRevision(Base):
    __tablename__ = "plan_revisions"
    __table_args__ = (
        CheckConstraint("revision_number >= 1", name="plan_revisions_number_valid"),
        CheckConstraint(
            "BTRIM(reason) <> ''", name="plan_revisions_reason_not_blank"
        ),
        CheckConstraint(
            "trigger_type IN ('MANUAL_EDIT', 'DELAY', 'NEED_MORE_TIME', 'SKIP',"
            " 'CONFLICT', 'RECOVERY')",
            name="plan_revisions_trigger_valid",
        ),
        CheckConstraint(
            "generated_by IN ('USER', 'SYSTEM', 'AI')",
            name="plan_revisions_generated_by_valid",
        ),
        CheckConstraint(
            "jsonb_typeof(before_snapshot) = 'object'",
            name="plan_revisions_before_object",
        ),
        CheckConstraint(
            "jsonb_typeof(after_snapshot) = 'object'",
            name="plan_revisions_after_object",
        ),
        UniqueConstraint(
            "daily_plan_id", "revision_number", name="plan_revisions_number_unique"
        ),
        Index(
            "plan_revisions_plan_recent_idx",
            "daily_plan_id",
            text("revision_number DESC"),
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default=text("gen_random_uuid()"),
    )
    daily_plan_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("daily_plans.id", ondelete="CASCADE"),
        nullable=False,
    )
    revision_number: Mapped[int] = mapped_column(Integer, nullable=False)
    reason: Mapped[str] = mapped_column(Text, nullable=False)
    trigger_type: Mapped[str] = mapped_column(String(30), nullable=False)
    generated_by: Mapped[str] = mapped_column(String(20), nullable=False)
    before_snapshot: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=False)
    after_snapshot: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )

    daily_plan: Mapped[DailyPlan] = relationship(back_populates="revisions")
    reward_events: Mapped[list[RewardEvent]] = relationship(
        back_populates="source_plan_revision", passive_deletes=True
    )
