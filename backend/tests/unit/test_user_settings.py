from decimal import Decimal

import pytest
from pydantic import ValidationError

from app.core.enums import SceneSeason
from app.schemas.user_settings import UserSettingsUpdate


def test_coordinates_are_rounded_and_paired():
    settings = UserSettingsUpdate(
        weather_location_name="London", weather_lat=51.5074, weather_lon=-0.1278
    )
    assert settings.weather_lat == Decimal("51.51")
    assert settings.weather_lon == Decimal("-0.13")
    for values in (
        {"weather_lat": 1},
        {"weather_lon": 1},
        {"weather_lat": 1, "weather_lon": 2},
        {"weather_location_name": " ", "weather_lat": 1, "weather_lon": 2},
        {"weather_location_name": "Place", "weather_lat": 91, "weather_lon": 2},
        {"weather_location_name": "Place", "weather_lat": 1, "weather_lon": -181},
        {
            "weather_location_name": "Place",
            "weather_lat": float("nan"),
            "weather_lon": 2,
        },
        {
            "weather_location_name": "Place",
            "weather_lat": float("inf"),
            "weather_lon": 2,
        },
    ):
        with pytest.raises(ValidationError):
            UserSettingsUpdate(**values)


def test_scene_season_bounds():
    assert (
        UserSettingsUpdate(scene_season=SceneSeason.AUTO).scene_season
        == SceneSeason.AUTO
    )
    with pytest.raises(ValidationError):
        UserSettingsUpdate(scene_season="INVALID")
