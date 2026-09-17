"""ORM models for the 19 Blooming tables, split by the database baseline scopes.

Importing this package attaches every table to ``Base.metadata`` so Alembic and
SQLAlchemy see the full schema.
"""

from app.db.models.daily_plans import (
    AvailabilityWindow,
    DailyPlan,
    PlanBlock,
    PlanRevision,
)
from app.db.models.focus import FocusRun, FocusRunEvent
from app.db.models.garden import GardenState, HeartEvent
from app.db.models.goals import Goal, Milestone
from app.db.models.planning import PlanningMessage, PlanningSession
from app.db.models.reminders import Reminder, ReminderAction
from app.db.models.tasks import Task, TaskDependency
from app.db.models.users import AuthSession, EmailVerificationToken, User, UserSettings

__all__ = [
    "AuthSession",
    "AvailabilityWindow",
    "DailyPlan",
    "EmailVerificationToken",
    "FocusRun",
    "FocusRunEvent",
    "GardenState",
    "Goal",
    "HeartEvent",
    "Milestone",
    "PlanBlock",
    "PlanRevision",
    "PlanningMessage",
    "PlanningSession",
    "Reminder",
    "ReminderAction",
    "Task",
    "TaskDependency",
    "User",
    "UserSettings",
]
