"""ORM models for the Blooming tables, split by the database baseline scopes.

Importing this package attaches every table to ``Base.metadata``.
"""

from app.db.models.daily_plans import (
    AvailabilityWindow,
    DailyPlan,
    PlanBlock,
    PlanRevision,
)
from app.db.models.focus import FocusRun, FocusRunEvent
from app.db.models.garden import GardenState, RewardEvent, Plant, PlantOwnership
from app.db.models.goals import Goal, Milestone
from app.db.models.planning import PlanningMessage, PlanningSession
from app.db.models.reminders import Reminder, ReminderAction
from app.db.models.tasks import Task, TaskDependency
from app.db.models.users import AuthSession, EmailVerificationToken, User, UserSettings
from app.db.models.ai_usage import AiUsageLog

__all__ = [
    "AiUsageLog",
    "AuthSession",
    "AvailabilityWindow",
    "DailyPlan",
    "EmailVerificationToken",
    "FocusRun",
    "FocusRunEvent",
    "GardenState",
    "Goal",
    "Plant",
    "PlantOwnership",
    "RewardEvent",
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
