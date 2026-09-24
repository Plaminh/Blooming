"""Scope: intended work before it is placed onto a concrete timeline."""

from __future__ import annotations

import uuid
from datetime import date, datetime, time
from typing import TYPE_CHECKING

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    Date,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    SmallInteger,
    String,
    Text,
    Time,
    func,
    text,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

if TYPE_CHECKING:
    from app.db.models.daily_plans import PlanBlock
    from app.db.models.focus import FocusRun
    from app.db.models.garden import RewardEvent
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
            "category IS NULL OR category IN ('Learning', 'Work', 'Personal')",
            name="tasks_category_valid",
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
            "tasks_user_planned_date_idx",
            "user_id",
            "planned_date",
            postgresql_where=text("planned_date IS NOT NULL"),
        ),
        Index(
            "tasks_recurring_idx",
            "recurring_task_id",
            "planned_date",
            postgresql_where=text("recurring_task_id IS NOT NULL"),
        ),
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
    category: Mapped[str | None] = mapped_column(String(50))
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
    # Local date the task is meant for before it is scheduled: work moved to a
    # later day, or one occurrence of a recurring task.
    planned_date: Mapped[date | None] = mapped_column(Date)
    recurring_task_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("recurring_tasks.id", ondelete="SET NULL"),
    )
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
    reward_events: Mapped[list[RewardEvent]] = relationship(
        back_populates="source_task", passive_deletes=True
    )


WEEKDAY_COUNT = 7


class RecurringTask(Base):
    """A repeating task template; concrete tasks are created per planned day."""

    __tablename__ = "recurring_tasks"
    __table_args__ = (
        CheckConstraint("BTRIM(title) <> ''", name="recurring_tasks_title_not_blank"),
        CheckConstraint(
            "estimated_duration_minutes BETWEEN 5 AND 480",
            name="recurring_tasks_duration_valid",
        ),
        CheckConstraint(
            "priority IN ('LOW', 'MEDIUM', 'HIGH', 'URGENT')",
            name="recurring_tasks_priority_valid",
        ),
        CheckConstraint(
            "importance IN ('CORE', 'OPTIONAL')", name="recurring_tasks_importance_valid"
        ),
        CheckConstraint(
            "category IS NULL OR category IN ('Learning', 'Work', 'Personal')",
            name="recurring_tasks_category_valid",
        ),
        CheckConstraint(
            "frequency IN ('DAILY', 'WEEKLY')", name="recurring_tasks_frequency_valid"
        ),
        CheckConstraint(
            "weekday_mask BETWEEN 0 AND 127 AND (frequency = 'DAILY' OR weekday_mask > 0)",
            name="recurring_tasks_weekday_mask_valid",
        ),
        CheckConstraint(
            "until_date IS NULL OR until_date >= start_date",
            name="recurring_tasks_until_valid",
        ),
        Index(
            "recurring_tasks_user_active_idx",
            "user_id",
            postgresql_where=text("is_active"),
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
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    estimated_duration_minutes: Mapped[int] = mapped_column(Integer, nullable=False)
    priority: Mapped[str] = mapped_column(
        String(20), nullable=False, server_default=text("'MEDIUM'")
    )
    importance: Mapped[str] = mapped_column(
        String(20), nullable=False, server_default=text("'CORE'")
    )
    category: Mapped[str | None] = mapped_column(String(50))
    frequency: Mapped[str] = mapped_column(String(10), nullable=False)
    # Bit i set = repeats on weekday i (0 = Monday ... 6 = Sunday).
    weekday_mask: Mapped[int] = mapped_column(
        SmallInteger, nullable=False, server_default=text("0")
    )
    fixed_start_time: Mapped[time | None] = mapped_column(Time)
    start_date: Mapped[date] = mapped_column(Date, nullable=False)
    until_date: Mapped[date | None] = mapped_column(Date)
    is_active: Mapped[bool] = mapped_column(
        Boolean, nullable=False, server_default=text("TRUE")
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )

    def occurs_on(self, day: date) -> bool:
        if not self.is_active or day < self.start_date:
            return False
        if self.until_date is not None and day > self.until_date:
            return False
        if self.frequency == "DAILY":
            return True
        return bool(self.weekday_mask & (1 << day.weekday()))


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
