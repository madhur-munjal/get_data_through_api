from enum import Enum
from typing import Literal, Optional

from pydantic import BaseModel


class Gender(str, Enum):
    male = "male"
    female = "female"
    other = "other"


class TemperatureUnit(str, Enum):
    celsius = "celsius"
    fahrenheit = "fahrenheit"


class PatientRecord(BaseModel):
    firstName: str
    lastName: Optional[str] = None
    age: Optional[int] = None
    mobile: str
    gender: Gender
    address: Optional[str] = None
    # currentVisit: datetime
    # lastVisit: datetime = None
    bloodGroup: Optional[
        Literal["A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-"]
    ] = None
    weight: Optional[float] = None
    bloodPressureUpper: Optional[int] = None
    bloodPressureLower: Optional[int] = None
    temperature: Optional[float] = None
    temperatureType: Optional[TemperatureUnit] = None


class PatientUpdate(BaseModel):
    firstName: str
    lastName: Optional[str] = None
    age: Optional[int] = None
    mobile: str
    gender: Gender
    address: Optional[str] = None
    # currentVisit: datetime = None
    # lastVisit: datetime = None
    bloodGroup: Optional[Literal["A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-"]] = (
        None
    )
    weight: Optional[float] = None
    bloodPressureUpper: Optional[int] = None
    bloodPressureLower: Optional[int] = None
    temperature: Optional[float] = None
    temperatureType: Optional[TemperatureUnit] = None


class PatientOut(PatientRecord):
    name: str
    age: int

    model_config = {"from_attributes": True}
