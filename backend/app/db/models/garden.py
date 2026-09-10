"""Scope: append-only Heart Progress ledger and current garden projection."""

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
    Text,
    UniqueConstraint,
    func,
    text,
)
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

if TYPE_CHECKING:
    from app.db.models.daily_plans import PlanRevision
    from app.db.models.focus import FocusRun
    from app.db.models.goals import Milestone
    from app.db.models.tasks import Task
    from app.db.models.users import User


class HeartEvent(Base):
    __tablename__ = "heart_events"
    __table_args__ = (
        UniqueConstraint(
            "idempotency_key", name="heart_events_idempotency_key_key"
        ),
        CheckConstraint(
            "event_type IN ('FOCUS_COMPLETED', 'TASK_COMPLETED',"
            " 'CORE_OBJECTIVE_COMPLETED', 'MILESTONE_COMPLETED',"
            " 'RECOVERY_PLAN_COMPLETED')",
            name="heart_events_type_valid",
        ),
        CheckConstraint("heart_amount > 0", name="heart_events_amount_valid"),
        CheckConstraint(
            "BTRIM(idempotency_key) <> ''",
            name="heart_events_idempotency_key_not_blank",
        ),
        CheckConstraint(
            "num_nonnulls(source_focus_run_id, source_task_id, source_milestone_id,"
            " source_plan_revision_id) = 1",
            name="heart_events_exactly_one_source",
        ),
        CheckConstraint(
            "(event_type = 'FOCUS_COMPLETED' AND source_focus_run_id IS NOT NULL)"
            " OR (event_type IN ('TASK_COMPLETED', 'CORE_OBJECTIVE_COMPLETED')"
            " AND source_task_id IS NOT NULL)"
            " OR (event_type = 'MILESTONE_COMPLETED'"
            " AND source_milestone_id IS NOT NULL)"
            " OR (event_type = 'RECOVERY_PLAN_COMPLETED'"
            " AND source_plan_revision_id IS NOT NULL)",
            name="heart_events_source_matches_type",
        ),
        CheckConstraint(
            "metadata IS NULL OR jsonb_typeof(metadata) = 'object'",
            name="heart_events_metadata_object",
        ),
        Index("heart_events_user_chronological_idx", "user_id", "created_at", "id"),
        Index(
            "heart_events_focus_run_idx",
            "source_focus_run_id",
            postgresql_where=text("source_focus_run_id IS NOT NULL"),
        ),
        Index(
            "heart_events_task_idx",
            "source_task_id",
            postgresql_where=text("source_task_id IS NOT NULL"),
        ),
        Index(
            "heart_events_milestone_idx",
            "source_milestone_id",
            postgresql_where=text("source_milestone_id IS NOT NULL"),
        ),
        Index(
            "heart_events_plan_revision_idx",
            "source_plan_revision_id",
            postgresql_where=text("source_plan_revision_id IS NOT NULL"),
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
    event_type: Mapped[str] = mapped_column(String(40), nullable=False)
    heart_amount: Mapped[int] = mapped_column(Integer, nullable=False)
    idempotency_key: Mapped[str] = mapped_column(Text, nullable=False)
    source_focus_run_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("focus_runs.id", ondelete="CASCADE"),
    )
    source_task_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("tasks.id", ondelete="CASCADE"),
    )
    source_milestone_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("milestones.id", ondelete="CASCADE"),
    )
    source_plan_revision_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("plan_revisions.id", ondelete="CASCADE"),
    )
    # "metadata" is reserved on the declarative base, so the attribute is renamed
    # while the mapped column keeps the database name.
    event_metadata: Mapped[dict[str, Any] | None] = mapped_column("metadata", JSONB)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )

    user: Mapped[User] = relationship(back_populates="heart_events")
    source_focus_run: Mapped[FocusRun | None] = relationship(
        back_populates="heart_events"
    )
    source_task: Mapped[Task | None] = relationship(back_populates="heart_events")
    source_milestone: Mapped[Milestone | None] = relationship(
        back_populates="heart_events"
    )
    source_plan_revision: Mapped[PlanRevision | None] = relationship(
        back_populates="heart_events"
    )


class GardenState(Base):
    __tablename__ = "garden_states"
    __table_args__ = (
        CheckConstraint("total_heart >= 0", name="garden_states_total_valid"),
        CheckConstraint(
            "stage IN ('DORMANT', 'SPROUTING', 'GROWING', 'BLOOMING', 'FRUITING')",
            name="garden_states_stage_valid",
        ),
        CheckConstraint(
            "leaf_count >= 0 AND flower_count >= 0 AND fruit_count >= 0",
            name="garden_states_visual_counts_valid",
        ),
        CheckConstraint("version >= 1", name="garden_states_version_valid"),
    )

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        primary_key=True,
    )
    total_heart: Mapped[int] = mapped_column(
        Integer, nullable=False, server_default=text("0")
    )
    stage: Mapped[str] = mapped_column(
        String(20), nullable=False, server_default=text("'DORMANT'")
    )
    leaf_count: Mapped[int] = mapped_column(
        Integer, nullable=False, server_default=text("0")
    )
    flower_count: Mapped[int] = mapped_column(
        Integer, nullable=False, server_default=text("0")
    )
    fruit_count: Mapped[int] = mapped_column(
        Integer, nullable=False, server_default=text("0")
    )
    version: Mapped[int] = mapped_column(
        Integer, nullable=False, server_default=text("1")
    )
    stage_changed_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )

    user: Mapped[User] = relationship(back_populates="garden_state")
