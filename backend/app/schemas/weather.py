from datetime import datetime

from pydantic import BaseModel, Field, field_validator

from app.models.enums import WeatherCondition, WeatherStatus


class PlaceCandidate(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    lat: float = Field(ge=-90, le=90, allow_inf_nan=False)
    lon: float = Field(ge=-180, le=180, allow_inf_nan=False)

    @field_validator("lat", "lon")
    @classmethod
    def round_coordinates(cls, v: float) -> float:
        return round(v, 2)


class PlaceSearchResponse(BaseModel):
    candidates: list[PlaceCandidate] = Field(max_length=5)


class WeatherResponse(BaseModel):
    condition: WeatherCondition
    status: WeatherStatus
    updated_at: datetime | None = None
