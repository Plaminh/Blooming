"""Event driven, quiet hour aware proactive suggestions."""

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from uuid import UUID

from app.core.config import settings
from app.core.time_utils import is_in_quiet_hours


@dataclass
class NudgeGate:
    cooldown: timedelta = timedelta(minutes=30)
    _last_by_user: dict[UUID, datetime] = field(default_factory=dict)
    _seen_events: set[tuple[UUID, str]] = field(default_factory=set)
    _streaks: dict[UUID, tuple[str, int]] = field(default_factory=dict)

    def evaluate(
        self,
        *,
        user_id: UUID,
        event_id: str,
        event_name: str,
        local_now: datetime,
        quiet_start=None,
        quiet_end=None,
        quiet_enabled: bool = False,
        consecutive_count: int | None = None,
    ) -> dict | None:
        key = (user_id, event_id)
        if key in self._seen_events:
            return None
        self._seen_events.add(key)
        if event_name not in {
            "NEED_MORE_TIME",
            "SKIP",
            "BEHIND_SCHEDULE",
            "MORNING_NO_PLAN",
        }:
            return None
        if event_name in {"NEED_MORE_TIME", "SKIP"}:
            if consecutive_count is None:
                previous_name, count = self._streaks.get(user_id, ("", 0))
                count = count + 1 if previous_name == event_name else 1
                self._streaks[user_id] = (event_name, count)
            else:
                count = consecutive_count
            if count < 2:
                return None
            if consecutive_count is None:
                self._streaks[user_id] = (event_name, 0)
        else:
            self._streaks.pop(user_id, None)
        if event_name == "MORNING_NO_PLAN" and local_now.hour >= 12:
            return None
        if (
            quiet_enabled
            and quiet_start
            and quiet_end
            and is_in_quiet_hours(local_now, quiet_start, quiet_end)
        ):
            return None
        previous = self._last_by_user.get(user_id)
        if previous and local_now - previous < self.cooldown:
            return None
        self._last_by_user[user_id] = local_now
        return {
            "id": event_id,
            "message": (
                "Would you like to make a plan for today?"
                if event_name == "MORNING_NO_PLAN"
                else "Your schedule changed. Would you like to replan the rest of today?"
            ),
            "action": "PLAN_TODAY"
            if event_name == "MORNING_NO_PLAN"
            else "REPLAN_TODAY",
        }


nudge_gate = NudgeGate(cooldown=timedelta(minutes=settings.AI_NUDGE_COOLDOWN_MINUTES))
