from datetime import time
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from pydantic import BaseModel, ConfigDict, Field, model_validator


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
