"""Scope: intended work before it is placed onto a concrete timeline."""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
    func,
    text,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

if TYPE_CHECKING:
    from app.db.models.daily_plans import PlanBlock
    from app.db.models.focus import FocusRun
    from app.db.models.garden import HeartEvent
    from app.db.models.goals import Milestone
    from app.db.models.users import User


class Task(Base):
    __tablename__ = "tasks"
    __table_args__ = (
        CheckConstraint("BTRIM(title) <> ''", name="tasks_title_not_blank"),
        CheckConstraint(
            "estimated_duration_minutes BETWEEN 1 AND 10080",
            name="tasks_duration_valid",
        ),
        CheckConstraint(
            "priority IN ('LOW', 'MEDIUM', 'HIGH', 'URGENT')",
            name="tasks_priority_valid",
        ),
        CheckConstraint(
            "importance IN ('CORE', 'OPTIONAL')", name="tasks_importance_valid"
        ),
        CheckConstraint(
            "scheduling_type IN ('FLEXIBLE', 'FIXED')",
            name="tasks_scheduling_type_valid",
        ),
        CheckConstraint(
            "source IN ('MANUAL', 'AI', 'MILESTONE', 'QUICK')",
            name="tasks_source_valid",
        ),
        CheckConstraint(
            "status IN ('DRAFT', 'PENDING', 'IN_PROGRESS', 'COMPLETED', 'SKIPPED',"
            " 'CANCELLED')",
            name="tasks_status_valid",
        ),
        CheckConstraint(
            "(scheduling_type = 'FIXED' AND fixed_start_at IS NOT NULL"
            " AND fixed_end_at IS NOT NULL AND fixed_end_at > fixed_start_at)"
            " OR (scheduling_type = 'FLEXIBLE' AND fixed_start_at IS NULL"
            " AND fixed_end_at IS NULL)",
            name="tasks_scheduling_window_valid",
        ),
        CheckConstraint(
            "(status = 'COMPLETED' AND completed_at IS NOT NULL)"
            " OR (status <> 'COMPLETED')",
            name="tasks_completion_valid",
        ),
        CheckConstraint(
            "min_split_duration_minutes IS NULL OR min_split_duration_minutes > 0",
            name="tasks_min_split_duration_valid",
        ),
        CheckConstraint(
            "preferred_break_duration_minutes IS NULL OR preferred_break_duration_minutes > 0",
            name="tasks_preferred_break_duration_valid",
        ),
        CheckConstraint(
            "min_split_duration_minutes IS NULL OR min_split_duration_minutes <= estimated_duration_minutes",
            name="tasks_min_split_duration_limit",
        ),
        Index("tasks_user_status_deadline_idx", "user_id", "status", "deadline_at"),
        Index(
            "tasks_milestone_idx",
            "milestone_id",
            postgresql_where=text("milestone_id IS NOT NULL"),
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
        ForeignKey("milestones.id", ondelete="SET NULL"),
    )
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    estimated_duration_minutes: Mapped[int] = mapped_column(Integer, nullable=False)
    priority: Mapped[str] = mapped_column(
        String(20), nullable=False, server_default=text("'MEDIUM'")
    )
    importance: Mapped[str] = mapped_column(
        String(20), nullable=False, server_default=text("'CORE'")
    )
    scheduling_type: Mapped[str] = mapped_column(
        String(20), nullable=False, server_default=text("'FLEXIBLE'")
    )
    source: Mapped[str] = mapped_column(
        String(20), nullable=False, server_default=text("'MANUAL'")
    )
    status: Mapped[str] = mapped_column(
        String(20), nullable=False, server_default=text("'DRAFT'")
    )
    deadline_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    is_splittable: Mapped[bool] = mapped_column(
        Boolean, nullable=False, server_default=text("FALSE")
    )
    min_split_duration_minutes: Mapped[int | None] = mapped_column(Integer)
    preferred_break_duration_minutes: Mapped[int | None] = mapped_column(Integer)
    fixed_start_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    fixed_end_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )

    user: Mapped[User] = relationship(back_populates="tasks")
    milestone: Mapped[Milestone | None] = relationship(back_populates="tasks")
    dependencies: Mapped[list[TaskDependency]] = relationship(
        back_populates="task",
        foreign_keys="TaskDependency.task_id",
        passive_deletes=True,
    )
    dependents: Mapped[list[TaskDependency]] = relationship(
        back_populates="depends_on_task",
        foreign_keys="TaskDependency.depends_on_task_id",
        passive_deletes=True,
    )
    plan_blocks: Mapped[list[PlanBlock]] = relationship(
        back_populates="task", passive_deletes=True
    )
    focus_runs: Mapped[list[FocusRun]] = relationship(
        back_populates="task", passive_deletes=True
    )
    heart_events: Mapped[list[HeartEvent]] = relationship(
        back_populates="source_task", passive_deletes=True
    )


class TaskDependency(Base):
    __tablename__ = "task_dependencies"
    __table_args__ = (
        CheckConstraint(
            "task_id <> depends_on_task_id", name="task_dependencies_not_self"
        ),
        Index("task_dependencies_prerequisite_idx", "depends_on_task_id"),
    )

    task_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("tasks.id", ondelete="CASCADE"),
        primary_key=True,
    )
    depends_on_task_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("tasks.id", ondelete="CASCADE"),
        primary_key=True,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )

    task: Mapped[Task] = relationship(
        back_populates="dependencies", foreign_keys=[task_id]
    )
    depends_on_task: Mapped[Task] = relationship(
        back_populates="dependents", foreign_keys=[depends_on_task_id]
    )
