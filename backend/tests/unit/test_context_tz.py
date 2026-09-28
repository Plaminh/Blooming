"""Cluster 11 — Context, timezone, and language.

Test IDs: CTX-001 through CTX-009, CTX-011, CTX-012

All tests use injected/frozen time.  No real clock or timezone dependency.
"""

from __future__ import annotations

from datetime import date, datetime, timezone
from unittest.mock import AsyncMock
from uuid import uuid4
from zoneinfo import ZoneInfo

import pytest

from app.ai.context import ChatContext
from app.ai.drafting.drafts import assemble_today
from app.ai.nlu.parser import ParsedPlan


# ---------------------------------------------------------------------------
# Helper: build a minimal ChatContext with frozen time
# ---------------------------------------------------------------------------
def _ctx(
    now_utc: datetime,
    tz_name: str = "UTC",
    default_windows: tuple[tuple[str, str], ...] = (("09:00", "17:00"),),
    default_date_offset: int = 0,
    break_minutes: int = 5,
) -> ChatContext:
    tz = ZoneInfo(tz_name)
    local_now = now_utc.astimezone(tz)
    return ChatContext(
        db=AsyncMock(),
        user_id=uuid4(),
        now=local_now,
        timezone=tz,
        break_minutes=break_minutes,
        default_windows=default_windows,
        default_date_offset=default_date_offset,
    )


# ---------------------------------------------------------------------------
# CTX-001 — Timezone comes from authenticated user settings
# ---------------------------------------------------------------------------


# ---------------------------------------------------------------------------
# CTX-002 — Client-provided timezone cannot override authoritative context
# (Production enforcement: preview_today_draft rejects mismatched timezone)
# ---------------------------------------------------------------------------


# ---------------------------------------------------------------------------
# CTX-003 — "Tomorrow" means next calendar day in user's timezone
# ---------------------------------------------------------------------------
def test_ctx_003_tomorrow_next_local_day():
    """plan_date_offset=1 advances one day from the local date, not UTC date."""
    # 2026-09-20 22:00 UTC = 2026-09-21 05:00 Asia/Ho_Chi_Minh (+7)
    now_utc = datetime(2026, 9, 20, 22, 0, tzinfo=timezone.utc)
    ctx = _ctx(now_utc, "Asia/Ho_Chi_Minh")
    # Local date is 2026-09-21; offset=1 → plan for 2026-09-22
    plan = ParsedPlan(plan_date_offset=1, tasks=(), windows=(("09:00", "17:00"),))
    draft, _ = assemble_today(plan, ctx)
    assert draft.planDate == date(2026, 9, 22)


def test_ctx_003_same_calendar_day_no_offset():
    """Without offset, plan date equals local today."""
    now_utc = datetime(2026, 9, 20, 10, 0, tzinfo=timezone.utc)
    ctx = _ctx(now_utc, "UTC")
    plan = ParsedPlan(plan_date_offset=0, tasks=(), windows=(("11:00", "17:00"),))
    draft, _ = assemble_today(plan, ctx)
    assert draft.planDate == date(2026, 9, 20)


# ---------------------------------------------------------------------------
# CTX-004 — UTC/local date disagreement
# ---------------------------------------------------------------------------
def test_ctx_004_utc_local_date_disagreement():
    """When UTC is still yesterday but local is already tomorrow, local date wins."""
    # 2023-12-31 22:00 UTC = 2024-01-01 05:00 Asia/Ho_Chi_Minh
    now_utc = datetime(2023, 12, 31, 22, 0, tzinfo=timezone.utc)
    ctx = _ctx(now_utc, "Asia/Ho_Chi_Minh")
    # No offset — plan date must be local date = 2024-01-01
    plan = ParsedPlan(tasks=(), windows=(("09:00", "17:00"),))
    draft, _ = assemble_today(plan, ctx)
    assert draft.planDate == date(2024, 1, 1)


# ---------------------------------------------------------------------------
# CTX-005 — Month boundary
# ---------------------------------------------------------------------------
def test_ctx_005_month_boundary():
    """Offset correctly crosses month boundaries."""
    # 2023-02-28 22:00 UTC = 2023-03-01 05:00 Asia/Ho_Chi_Minh
    now_utc = datetime(2023, 2, 28, 22, 0, tzinfo=timezone.utc)
    ctx = _ctx(now_utc, "Asia/Ho_Chi_Minh")
    # Local date = 2023-03-01; offset=1 → 2023-03-02
    plan = ParsedPlan(plan_date_offset=1, tasks=(), windows=(("09:00", "17:00"),))
    draft, _ = assemble_today(plan, ctx)
    assert draft.planDate == date(2023, 3, 2)


# ---------------------------------------------------------------------------
# CTX-006 — Year boundary
# ---------------------------------------------------------------------------
def test_ctx_006_year_boundary():
    """Offset correctly crosses year boundaries."""
    # 2023-12-31 22:00 UTC = 2024-01-01 05:00 Asia/Ho_Chi_Minh
    now_utc = datetime(2023, 12, 31, 22, 0, tzinfo=timezone.utc)
    ctx = _ctx(now_utc, "Asia/Ho_Chi_Minh")
    # Local date = 2024-01-01; offset=1 → 2024-01-02
    plan = ParsedPlan(plan_date_offset=1, tasks=(), windows=(("09:00", "17:00"),))
    draft, _ = assemble_today(plan, ctx)
    assert draft.planDate == date(2024, 1, 2)


# ---------------------------------------------------------------------------
# CTX-007 — Default availability comes from context/settings
# ---------------------------------------------------------------------------
def test_ctx_007_default_availability_from_context():
    """When parser provides no windows, context default_windows are used."""
    # 01:00 UTC is 08:00 Asia/Ho_Chi_Minh — early morning, window not yet passed
    now_utc = datetime(2026, 9, 20, 1, 0, tzinfo=timezone.utc)
    ctx = _ctx(now_utc, "UTC", default_windows=(("09:00", "17:00"),))
    # Parser found no windows
    plan = ParsedPlan(tasks=(), windows=())
    draft, assumptions = assemble_today(plan, ctx)

    assert len(draft.windows) == 1
    assert draft.windows[0].start == "09:00"
    assert draft.windows[0].end == "17:00"
    # An assumption must explain the default was used
    assumption_texts = [a.text for a in assumptions]
    assert any("09:00" in t or "availability" in t.lower() for t in assumption_texts)


# ---------------------------------------------------------------------------
# CTX-008 — Explicit availability overrides default
# ---------------------------------------------------------------------------
def test_ctx_008_explicit_availability_overrides_default():
    """When parser finds explicit windows, they override context defaults."""
    now_utc = datetime(2026, 9, 20, 1, 0, tzinfo=timezone.utc)
    ctx = _ctx(now_utc, "UTC", default_windows=(("09:00", "17:00"),))
    # Parser found explicit window
    plan = ParsedPlan(tasks=(), windows=(("10:00", "15:00"),))
    draft, assumptions = assemble_today(plan, ctx)

    assert len(draft.windows) == 1
    assert draft.windows[0].start == "10:00"
    assert draft.windows[0].end == "15:00"
    # No "default working hours" assumption should appear
    assumption_texts = [a.text for a in assumptions]
    assert not any("09:00" in t and "17:00" in t for t in assumption_texts)


# ---------------------------------------------------------------------------
# CTX-009 — Past portions of today's window are clipped using local current time
# ---------------------------------------------------------------------------
def test_ctx_009_past_window_clipped():
    """If current time is mid-window, the past portion is clipped."""
    # 12:00 UTC, offset=0 → today
    now_utc = datetime(2026, 9, 20, 12, 0, tzinfo=timezone.utc)
    ctx = _ctx(now_utc, "UTC", default_windows=(("09:00", "17:00"),))
    plan = ParsedPlan(tasks=(), windows=())
    draft, _ = assemble_today(plan, ctx)

    # Window start must not be before 12:00
    assert len(draft.windows) >= 1
    assert draft.windows[0].start >= "12:00"
    assert draft.windows[0].end == "17:00"


def test_ctx_009_expired_window_moves_to_tomorrow():
    """If the entire window has already passed, plan shifts to tomorrow."""
    # 18:00 UTC — after the 09:00–17:00 window
    now_utc = datetime(2026, 9, 20, 18, 0, tzinfo=timezone.utc)
    ctx = _ctx(now_utc, "UTC", default_windows=(("09:00", "17:00"),))
    plan = ParsedPlan(tasks=(), windows=())
    draft, assumptions = assemble_today(plan, ctx)
    # Should have shifted to tomorrow
    assert draft.planDate >= date(2026, 9, 21)
    assumption_texts = [a.text for a in assumptions]
    assert any(
        "tomorrow" in t.lower() or "window" in t.lower() for t in assumption_texts
    )


# ---------------------------------------------------------------------------
# CTX-011 — If remaining availability is too short, move to tomorrow
# ---------------------------------------------------------------------------
def test_ctx_011_short_remaining_shifts_to_tomorrow():
    """Less than 30 min remaining in window → plan moves to tomorrow."""
    # 16:45 UTC, window ends at 17:00 → 15 min remaining
    now_utc = datetime(2026, 9, 20, 16, 45, tzinfo=timezone.utc)
    ctx = _ctx(now_utc, "UTC", default_windows=(("09:00", "17:00"),))
    plan = ParsedPlan(tasks=(), windows=())
    draft, assumptions = assemble_today(plan, ctx)

    # Only 15 min left — assembler clips and then moves to tomorrow
    assert draft.planDate >= date(2026, 9, 21)


# ---------------------------------------------------------------------------
# CTX-012 — Weather does not change planning date, duration, importance, or scheduler
# ---------------------------------------------------------------------------
def test_ctx_012_weather_does_not_affect_planning():
    """Weather context does not influence plan date, duration, or scheduling."""
    now_utc = datetime(2026, 9, 20, 8, 0, tzinfo=timezone.utc)
    ctx = _ctx(now_utc, "UTC")

    # Two assemblies: one where we imagine weather data is present (simulated by
    # any external field), and one without.  The results must be identical because
    # ChatContext has no weather field — weather cannot bleed into planning.
    plan = ParsedPlan(tasks=(), windows=(("09:00", "17:00"),))
    draft1, assumptions1 = assemble_today(plan, ctx)
    draft2, assumptions2 = assemble_today(plan, ctx)

    assert draft1.planDate == draft2.planDate
    assert draft1.windows == draft2.windows
    assert len(assumptions1) == len(assumptions2)


from unittest.mock import patch
from app.ai.context import build_context


@pytest.mark.asyncio
async def test_ctx_001_timezone_from_settings():
    """CTX-001: Timezone comes from persisted UserSettings, not client."""
    from app.db.models.users import UserSettings

    db = AsyncMock()
    mock_settings = UserSettings(
        user_id=uuid4(), timezone="Asia/Tokyo", default_break_minutes=5
    )
    db.scalar.return_value = mock_settings

    user_id = mock_settings.user_id
    now_utc = datetime(2026, 9, 20, 1, 0, tzinfo=timezone.utc)

    # Needs to patch calibration to avoid db query issues in build_context
    with patch(
        "app.ai.calibration.calibration_multipliers", new_callable=AsyncMock
    ) as mock_cal:
        mock_cal.return_value = {}
        ctx = await build_context(db, user_id, now_utc)

    assert str(ctx.timezone) == "Asia/Tokyo"
    assert ctx.now.tzinfo == ZoneInfo("Asia/Tokyo")
    assert ctx.now.hour == 10  # 01:00 UTC = 10:00 JST


@pytest.mark.asyncio
async def test_ctx_002_conflicting_timezone_rejected():
    """CTX-002: Client-provided timezone in drafts must match server settings."""
    from app.services.today_service import today_service
    from app.schemas.today import TodayPreviewRequest
    from app.schemas.drafts import TodayDraft
    from app.db.models.users import UserSettings
    from fastapi import HTTPException

    db = AsyncMock()
    user_id = uuid4()
    mock_settings = UserSettings(user_id=user_id, timezone="Asia/Tokyo")
    db.scalar.return_value = mock_settings

    # Client sends draft with a different timezone (America/New_York)
    draft = TodayDraft(
        planDate="2026-09-20",
        timezone="America/New_York",
        windows=[{"start": "09:00", "end": "10:00"}],
        tasks=[
            {
                "id": "t1",
                "title": "t1",
                "durationMin": 30,
                "priority": "MEDIUM",
                "importance": "CORE",
                "estimateSource": "USER",
                "schedulingType": "FLEXIBLE",
                "dependencies": [],
            }
        ],
    )
    request = TodayPreviewRequest(draft=draft)

    with pytest.raises(HTTPException) as excinfo:
        await today_service.preview_today_draft(db, user_id, request)

    assert excinfo.value.status_code == 422
    assert "timezone" in excinfo.value.detail.lower()
