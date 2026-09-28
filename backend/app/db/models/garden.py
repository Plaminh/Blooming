"""Scope: append-only Reward Progress ledger, current garden projection, and catalog."""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import TYPE_CHECKING, Any

from sqlalchemy import (
    Boolean,
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


class Plant(Base):
    __tablename__ = "plants"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default=text("gen_random_uuid()"),
    )
    species: Mapped[str] = mapped_column(String(50), nullable=False, unique=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    unlock_cost: Mapped[int] = mapped_column(Integer, nullable=False)
    is_active: Mapped[bool] = mapped_column(
        Boolean, nullable=False, server_default=text("TRUE")
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )


class PlantOwnership(Base):
    __tablename__ = "plant_ownerships"
    __table_args__ = (
        UniqueConstraint("user_id", "plant_id", name="plant_ownerships_user_plant_key"),
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
    plant_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("plants.id", ondelete="CASCADE"),
        nullable=False,
    )
    unlocked_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )


class RewardEvent(Base):
    __tablename__ = "reward_events"
    __table_args__ = (
        UniqueConstraint("idempotency_key", name="reward_events_idempotency_key_key"),
        CheckConstraint(
            "event_type IN ('FOCUS_COMPLETED', 'TASK_COMPLETED',"
            " 'CORE_OBJECTIVE_COMPLETED', 'MILESTONE_COMPLETED',"
            " 'RECOVERY_PLAN_COMPLETED', 'PLANT_UNLOCK', 'WATER_PLANT')",
            name="reward_events_type_valid",
        ),
        CheckConstraint(
            "resource_type IN ('WATER', 'LEAVES')",
            name="reward_events_resource_type_valid",
        ),
        CheckConstraint(
            "BTRIM(idempotency_key) <> ''",
            name="reward_events_idempotency_key_not_blank",
        ),
        CheckConstraint(
            "num_nonnulls(source_focus_run_id, source_task_id, source_milestone_id,"
            " source_plan_revision_id) <= 1",
            name="reward_events_max_one_source",
        ),
        CheckConstraint(
            "metadata IS NULL OR jsonb_typeof(metadata) = 'object'",
            name="reward_events_metadata_object",
        ),
        Index("reward_events_user_chronological_idx", "user_id", "created_at", "id"),
        Index(
            "reward_events_focus_run_idx",
            "source_focus_run_id",
            postgresql_where=text("source_focus_run_id IS NOT NULL"),
        ),
        Index(
            "reward_events_task_idx",
            "source_task_id",
            postgresql_where=text("source_task_id IS NOT NULL"),
        ),
        Index(
            "reward_events_milestone_idx",
            "source_milestone_id",
            postgresql_where=text("source_milestone_id IS NOT NULL"),
        ),
        Index(
            "reward_events_plan_revision_idx",
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
    resource_type: Mapped[str] = mapped_column(String(20), nullable=False)
    amount: Mapped[int] = mapped_column(Integer, nullable=False)
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
    event_metadata: Mapped[dict[str, Any] | None] = mapped_column("metadata", JSONB)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )

    user: Mapped[User] = relationship(back_populates="reward_events")
    source_focus_run: Mapped[FocusRun | None] = relationship(
        back_populates="reward_events"
    )
    source_task: Mapped[Task | None] = relationship(back_populates="reward_events")
    source_milestone: Mapped[Milestone | None] = relationship(
        back_populates="reward_events"
    )
    source_plan_revision: Mapped[PlanRevision | None] = relationship(
        back_populates="reward_events"
    )


class GardenState(Base):
    __tablename__ = "garden_states"
    __table_args__ = (
        CheckConstraint("water_balance >= 0", name="garden_states_water_valid"),
        CheckConstraint("leaves_balance >= 0", name="garden_states_leaves_valid"),
        CheckConstraint("growth_points >= 0", name="garden_states_growth_points_valid"),
    )

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        primary_key=True,
    )
    water_balance: Mapped[int] = mapped_column(
        Integer, nullable=False, server_default=text("0")
    )
    leaves_balance: Mapped[int] = mapped_column(
        Integer, nullable=False, server_default=text("0")
    )
    selected_plant_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("plants.id", ondelete="SET NULL")
    )
    growth_points: Mapped[int] = mapped_column(
        Integer, nullable=False, server_default=text("0")
    )
    last_watered_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )

    user: Mapped[User] = relationship(back_populates="garden_state")
