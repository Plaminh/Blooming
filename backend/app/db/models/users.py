"""Scope: user identity, account-wide preferences, and revocable login sessions."""

from __future__ import annotations

import uuid
from datetime import datetime, time
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
    Time,
    UniqueConstraint,
    func,
    text,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

if TYPE_CHECKING:
    from app.db.models.daily_plans import DailyPlan
    from app.db.models.focus import FocusRun
    from app.db.models.garden import GardenState, HeartEvent
    from app.db.models.goals import Goal
    from app.db.models.planning import PlanningSession
    from app.db.models.reminders import Reminder
    from app.db.models.tasks import Task


class User(Base):
    __tablename__ = "users"
    __table_args__ = (
        CheckConstraint("BTRIM(email) <> ''", name="users_email_not_blank"),
        CheckConstraint(
            "account_status IN ('ACTIVE', 'DISABLED')",
            name="users_account_status_valid",
        ),
        Index("users_email_lower_unique_idx", text("LOWER(email)"), unique=True),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default=text("gen_random_uuid()"),
    )
    email: Mapped[str] = mapped_column(String(320), nullable=False)
    password_hash: Mapped[str] = mapped_column(Text, nullable=False)
    display_name: Mapped[str | None] = mapped_column(String(100))
    account_status: Mapped[str] = mapped_column(
        String(20), nullable=False, server_default=text("'ACTIVE'")
    )
    last_login_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )

    settings: Mapped[UserSettings | None] = relationship(
        back_populates="user", passive_deletes=True
    )
    auth_sessions: Mapped[list[AuthSession]] = relationship(
        back_populates="user", passive_deletes=True
    )
    goals: Mapped[list[Goal]] = relationship(
        back_populates="user", passive_deletes=True
    )
    planning_sessions: Mapped[list[PlanningSession]] = relationship(
        back_populates="user", passive_deletes=True
    )
    tasks: Mapped[list[Task]] = relationship(
        back_populates="user", passive_deletes=True
    )
    daily_plans: Mapped[list[DailyPlan]] = relationship(
        back_populates="user", passive_deletes=True
    )
    focus_runs: Mapped[list[FocusRun]] = relationship(
        back_populates="user", passive_deletes=True
    )
    reminders: Mapped[list[Reminder]] = relationship(
        back_populates="user", passive_deletes=True
    )
    heart_events: Mapped[list[HeartEvent]] = relationship(
        back_populates="user", passive_deletes=True
    )
    garden_state: Mapped[GardenState | None] = relationship(
        back_populates="user", passive_deletes=True
    )


class UserSettings(Base):
    __tablename__ = "user_settings"
    __table_args__ = (
        CheckConstraint(
            "default_focus_minutes BETWEEN 1 AND 720",
            name="user_settings_focus_duration_valid",
        ),
        CheckConstraint(
            "default_break_minutes BETWEEN 0 AND 180",
            name="user_settings_break_duration_valid",
        ),
        CheckConstraint(
            "(quiet_hours_start IS NULL AND quiet_hours_end IS NULL)"
            " OR (quiet_hours_start IS NOT NULL AND quiet_hours_end IS NOT NULL)",
            name="user_settings_quiet_hours_pair",
        ),
        CheckConstraint(
            "BTRIM(mr_bloom_display_name) <> ''",
            name="user_settings_mr_bloom_name_not_blank",
        ),
    )

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        primary_key=True,
    )
    timezone: Mapped[str] = mapped_column(
        String(64), nullable=False, server_default=text("'UTC'")
    )
    default_focus_minutes: Mapped[int] = mapped_column(
        Integer, nullable=False, server_default=text("25")
    )
    default_break_minutes: Mapped[int] = mapped_column(
        Integer, nullable=False, server_default=text("5")
    )
    reminders_enabled: Mapped[bool] = mapped_column(
        Boolean, nullable=False, server_default=text("TRUE")
    )
    quiet_hours_enabled: Mapped[bool] = mapped_column(
        Boolean, nullable=False, server_default=text("FALSE")
    )
    quiet_hours_start: Mapped[time | None] = mapped_column(Time)
    quiet_hours_end: Mapped[time | None] = mapped_column(Time)
    mr_bloom_display_name: Mapped[str] = mapped_column(
        String(60), nullable=False, server_default=text("'Mr. Bloom'")
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )

    user: Mapped[User] = relationship(back_populates="settings")


class AuthSession(Base):
    __tablename__ = "auth_sessions"
    __table_args__ = (
        UniqueConstraint(
            "refresh_token_hash", name="auth_sessions_refresh_token_hash_key"
        ),
        CheckConstraint(
            "platform IS NULL OR platform IN ('WINDOWS', 'LINUX', 'OTHER')",
            name="auth_sessions_platform_valid",
        ),
        CheckConstraint("expires_at > created_at", name="auth_sessions_expiry_valid"),
        CheckConstraint(
            "revoked_at IS NULL OR revoked_at >= created_at",
            name="auth_sessions_revocation_valid",
        ),
        Index(
            "auth_sessions_user_active_idx",
            "user_id",
            "expires_at",
            postgresql_where=text("revoked_at IS NULL"),
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
    refresh_token_hash: Mapped[str] = mapped_column(Text, nullable=False)
    device_name: Mapped[str | None] = mapped_column(String(120))
    platform: Mapped[str | None] = mapped_column(String(20))
    expires_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )
    last_used_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    revoked_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )

    user: Mapped[User] = relationship(back_populates="auth_sessions")
