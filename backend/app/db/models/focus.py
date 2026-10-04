"""Scope: accurate Pomodoro execution independent of whether a window is visible."""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any, TYPE_CHECKING

from sqlalchemy import (
    CheckConstraint,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    String,
    func,
    text,
)
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

if TYPE_CHECKING:
    from app.db.models.daily_plans import PlanBlock
    from app.db.models.garden import RewardEvent
    from app.db.models.tasks import Task
    from app.db.models.users import User


class FocusRun(Base):
    __allow_unmapped__ = True
    replan: Any | None = None
    __tablename__ = "focus_runs"
    __table_args__ = (
        CheckConstraint(
            "task_id IS NOT NULL"
            " OR (quick_task_title IS NOT NULL AND BTRIM(quick_task_title) <> '')",
            name="focus_runs_subject_valid",
        ),
        CheckConstraint(
            "status IN ('READY', 'FOCUSING', 'PAUSED', 'ENDED')",
            name="focus_runs_status_valid",
        ),
        CheckConstraint(
            "outcome IS NULL"
            " OR outcome IN ('DONE', 'NEED_MORE_TIME', 'SKIP', 'FINISHED_EARLY')",
            name="focus_runs_outcome_valid",
        ),
        CheckConstraint(
            "planned_focus_seconds BETWEEN 1 AND 86400",
            name="focus_runs_focus_duration_valid",
        ),
        CheckConstraint(
            "planned_break_seconds BETWEEN 0 AND 21600",
            name="focus_runs_break_duration_valid",
        ),
        CheckConstraint(
            "total_paused_seconds >= 0", name="focus_runs_pause_duration_valid"
        ),
        CheckConstraint(
            "actual_duration_seconds IS NULL OR actual_duration_seconds >= 0",
            name="focus_runs_actual_duration_valid",
        ),
        CheckConstraint(
            "started_at IS NULL OR expected_end_at IS NULL"
            " OR expected_end_at >= started_at",
            name="focus_runs_expected_end_valid",
        ),
        CheckConstraint(
            "ended_at IS NULL OR (started_at IS NOT NULL AND ended_at >= started_at)",
            name="focus_runs_end_valid",
        ),
        CheckConstraint(
            "status <> 'ENDED'"
            " OR (ended_at IS NOT NULL AND actual_duration_seconds IS NOT NULL)",
            name="focus_runs_ended_state_valid",
        ),
        Index("focus_runs_user_recent_idx", "user_id", text("created_at DESC")),
        Index("idx_focus_runs_user_status", "user_id", "status"),
        Index(
            "focus_runs_user_active_idx",
            "user_id",
            "status",
            postgresql_where=text("status IN ('READY', 'FOCUSING', 'PAUSED')"),
        ),
        Index(
            "focus_runs_task_idx",
            "task_id",
            postgresql_where=text("task_id IS NOT NULL"),
        ),
        Index(
            "focus_runs_plan_block_idx",
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
    task_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("tasks.id", ondelete="CASCADE"),
    )
    plan_block_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("plan_blocks.id", ondelete="SET NULL"),
    )
    quick_task_title: Mapped[str | None] = mapped_column(String(200))
    status: Mapped[str] = mapped_column(
        String(20), nullable=False, server_default=text("'READY'")
    )
    outcome: Mapped[str | None] = mapped_column(String(30))
    planned_focus_seconds: Mapped[int] = mapped_column(Integer, nullable=False)
    planned_break_seconds: Mapped[int] = mapped_column(
        Integer, nullable=False, server_default=text("0")
    )
    started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    expected_end_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    paused_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    total_paused_seconds: Mapped[int] = mapped_column(
        Integer, nullable=False, server_default=text("0")
    )
    ended_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    actual_duration_seconds: Mapped[int | None] = mapped_column(Integer)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )

    user: Mapped[User] = relationship(back_populates="focus_runs")
    task: Mapped[Task | None] = relationship(back_populates="focus_runs")
    plan_block: Mapped[PlanBlock | None] = relationship(back_populates="focus_runs")
    events: Mapped[list[FocusRunEvent]] = relationship(
        back_populates="focus_run", passive_deletes=True
    )
    reward_events: Mapped[list[RewardEvent]] = relationship(
        back_populates="source_focus_run", passive_deletes=True
    )


class FocusRunEvent(Base):
    __tablename__ = "focus_run_events"
    __table_args__ = (
        CheckConstraint(
            "event_type IN ('STARTED', 'PAUSED', 'RESUMED', 'ENDED',"
            " 'OUTCOME_RECORDED')",
            name="focus_run_events_type_valid",
        ),
        CheckConstraint(
            "payload IS NULL OR jsonb_typeof(payload) = 'object'",
            name="focus_run_events_payload_object",
        ),
        Index(
            "focus_run_events_run_chronological_idx",
            "focus_run_id",
            "occurred_at",
            "id",
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default=text("gen_random_uuid()"),
    )
    focus_run_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("focus_runs.id", ondelete="CASCADE"),
        nullable=False,
    )
    event_type: Mapped[str] = mapped_column(String(30), nullable=False)
    occurred_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    payload: Mapped[dict[str, Any] | None] = mapped_column(JSONB)

    focus_run: Mapped[FocusRun] = relationship(back_populates="events")
