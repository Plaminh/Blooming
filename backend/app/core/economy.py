from datetime import datetime, timezone
import math

# Reward Constants
WATER_PER_POMODORO = 1
LEAVES_PER_TASK = 1
LEAVES_PER_MILESTONE = 1

# Economy Constants
WATERING_COST = 1

# Vitality Constants
VITALITY_MAX = 100
VITALITY_DECAY_PER_DAY = 10


def calculate_vitality(
    last_watered_at: datetime | None, current_time: datetime | None = None
) -> int:
    """
    Lazily calculate the current vitality based on the time elapsed since last_watered_at.
    Vitality starts at VITALITY_MAX and decays by VITALITY_DECAY_PER_DAY per 24 hours.
    Returns an integer clamped between 0 and 100.
    """
    if last_watered_at is None:
        return 0

    if current_time is None:
        current_time = datetime.now(timezone.utc)

    # Ensure last_watered_at is aware
    if last_watered_at.tzinfo is None:
        last_watered_at = last_watered_at.replace(tzinfo=timezone.utc)
    if current_time.tzinfo is None:
        current_time = current_time.replace(tzinfo=timezone.utc)

    if current_time <= last_watered_at:
        return VITALITY_MAX

    elapsed_seconds = (current_time - last_watered_at).total_seconds()
    elapsed_days = elapsed_seconds / 86400.0

    decay = math.floor(elapsed_days * VITALITY_DECAY_PER_DAY)
    current_vitality = VITALITY_MAX - decay

    # Clamp to [0, VITALITY_MAX]
    return max(0, min(VITALITY_MAX, current_vitality))
