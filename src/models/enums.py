from enum import Enum


class AppointmentStatus(str, Enum):
    UPCOMING = 0
    COMPLETED = 1
    NO_SHOW = 2


class AppointmentType(str, Enum):
    NEW = 0
    FOLLOW_UP = 1
    EMERGENCY = 2


class Gender(str, Enum):
    male = "male"
    female = "female"
    other = "other"


class TemperatureUnit(str, Enum):
    celsius = "celsius"
    fahrenheit = "fahrenheit"
