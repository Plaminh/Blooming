from datetime import time
from decimal import ROUND_HALF_UP, Decimal
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from app.models.enums import SceneSeason


class UserSettingsUpdate(BaseModel):
    timezone: str | None = Field(default=None)
    default_focus_minutes: int | None = Field(default=None, ge=1, le=720)
    default_break_minutes: int | None = Field(default=None, ge=0, le=180)
    quiet_hours_enabled: bool | None = Field(default=None)
    quiet_hours_start: time | None = Field(default=None)
    quiet_hours_end: time | None = Field(default=None)
    milestone_reminder_lead_time_minutes: int | None = Field(
        default=None, ge=0, le=43200
    )
    mr_bloom_display_name: str | None = Field(default=None, min_length=1, max_length=60)
    widget_visibility: bool | None = Field(default=None)
    widget_always_on_top: bool | None = Field(default=None)
    launch_on_startup: bool | None = Field(default=None)
    weather_enabled: bool | None = Field(default=None)
    weather_location: str | None = Field(default=None, max_length=100)
    weather_animation_enabled: bool | None = Field(default=None)
    weather_location_name: str | None = Field(default=None, max_length=255)
    weather_lat: Decimal | None = Field(
        default=None, ge=-90, le=90, allow_inf_nan=False
    )
    weather_lon: Decimal | None = Field(
        default=None, ge=-180, le=180, allow_inf_nan=False
    )
    scene_season: SceneSeason | None = Field(default=None)

    @field_validator("weather_lat", "weather_lon")
    @classmethod
    def round_coordinate(cls, value: Decimal | None) -> Decimal | None:
        if value is None:
            return None
        if not value.is_finite():
            raise ValueError("Coordinate must be finite")
        return value.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

    @model_validator(mode="after")
    def validate_non_nullable_and_timezone(self) -> "UserSettingsUpdate":
        # Reject explicit null for non-nullable fields
        non_nullable = [
            "timezone",
            "default_focus_minutes",
            "default_break_minutes",
            "quiet_hours_enabled",
            "mr_bloom_display_name",
            "widget_visibility",
            "widget_always_on_top",
            "launch_on_startup",
            "weather_enabled",
            "weather_animation_enabled",
            "milestone_reminder_lead_time_minutes",
        ]
        for field in non_nullable:
            if field in self.model_fields_set and getattr(self, field) is None:
                raise ValueError(f"{field} cannot be null")

        if self.timezone is not None:
            try:
                ZoneInfo(self.timezone)
            except ZoneInfoNotFoundError:
                raise ValueError("Invalid timezone")
        fields = {"weather_lat", "weather_lon"}
        if self.model_fields_set & fields and not fields <= self.model_fields_set:
            raise ValueError("Both weather coordinates must be supplied together")
        if fields <= self.model_fields_set:
            if (self.weather_lat is None) != (self.weather_lon is None):
                raise ValueError("Both weather coordinates must be supplied together")
            if (
                self.weather_lat is not None
                and not (self.weather_location_name or "").strip()
            ):
                raise ValueError("Coordinates require a selected place name")
        return self


class UserSettingsResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    timezone: str
    default_focus_minutes: int
    default_break_minutes: int
    quiet_hours_enabled: bool
    quiet_hours_start: time | None
    quiet_hours_end: time | None
    milestone_reminder_lead_time_minutes: int = Field(ge=0, le=43200)
    mr_bloom_display_name: str
    widget_visibility: bool
    widget_always_on_top: bool
    launch_on_startup: bool
    weather_enabled: bool
    weather_location: str | None
    weather_animation_enabled: bool
    weather_location_name: str | None
    weather_lat: float | None
    weather_lon: float | None
    scene_season: SceneSeason
