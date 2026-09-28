import logging
from datetime import datetime, time, timezone
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError


def safe_timezone(name: str):
    try:
        return ZoneInfo(name)
    except (ZoneInfoNotFoundError, ValueError, TypeError):
        logging.getLogger(__name__).warning(
            "invalid_timezone_fallback", extra={"fallback": "UTC"}
        )
        return timezone.utc


def is_in_quiet_hours(
    local_time: datetime, quiet_hours_start: time | None, quiet_hours_end: time | None
) -> bool:
    """Local wall-clock interval, inclusive start and exclusive end."""
    if (
        quiet_hours_start is None
        or quiet_hours_end is None
        or quiet_hours_start == quiet_hours_end
    ):
        return False
    current = local_time.time()
    if quiet_hours_start < quiet_hours_end:
        return quiet_hours_start <= current < quiet_hours_end
    return current >= quiet_hours_start or current < quiet_hours_end
