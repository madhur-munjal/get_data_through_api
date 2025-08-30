from typing import Literal, Optional

from pydantic import BaseModel

from .enums import Gender, TemperatureUnit


class PatientRecord(BaseModel):
    firstName: str  # Required
    lastName: Optional[str] = None
    age: Optional[int] = None
    mobile: str  # Required
    gender: Optional[Gender] = None
    address: Optional[str] = None
    bloodGroup: Optional[
        Literal["A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-"]
    ] = None
    weight: Optional[float] = None
    bloodPressureUpper: Optional[int] = None
    bloodPressureLower: Optional[int] = None
    temperature: Optional[float] = None
    temperatureType: Optional[TemperatureUnit] = None

    model_config = {"from_attributes": True}


class PatientUpdate(BaseModel):
    firstName: str  # Required
    lastName: Optional[str] = None
    age: Optional[int] = None
    mobile: str  # Required
    gender: Optional[Gender] = None
    address: Optional[str] = None
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
