from enum import Enum


class WeatherCondition(str, Enum):
    CLEAR = "CLEAR"
    CLOUDY = "CLOUDY"
    OVERCAST = "OVERCAST"
    RAIN = "RAIN"
    THUNDERSTORM = "THUNDERSTORM"


class WeatherStatus(str, Enum):
    OK = "OK"
    STALE = "STALE"
    UNAVAILABLE = "UNAVAILABLE"
    DISABLED = "DISABLED"


class SceneSeason(str, Enum):
    AUTO = "AUTO"
    SPRING = "SPRING"
    SUMMER = "SUMMER"
    AUTUMN = "AUTUMN"
    WINTER = "WINTER"
