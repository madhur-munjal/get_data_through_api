from datetime import datetime
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
    lastName: str = None
    age: int = None
    mobile: str
    gender: Gender
    address: str = None
    currentVisit: datetime
    lastVisit: datetime = None
    bloodGroup: Optional[Literal["A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-"]] = (
        None
    )
    weight: float = None
    bloodPressureUpper: int = None
    bloodPressureLower: int = None
    temperature: float = None
    temperatureType: TemperatureUnit = None

    # @validator("currentVisit", "lastVisit", pre=True)
    # def parse_date(cls, value):
    #     return datetime.strptime(value, "%b %d, %Y")
    #
    # @validator("tests", pre=True)
    # def split_tests(cls, value):
    #     if isinstance(value, str):
    #         return [test.strip() for test in value.split(",")]
    #     return value

class PatientUpdate(BaseModel):
    firstName: str
    lastName: Optional[str] = None
    age: Optional[int] = None
    mobile: str
    gender: Gender
    address: Optional[str] = None
    currentVisit: datetime = None
    lastVisit: datetime = None
    bloodGroup: Optional[Literal["A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-"]] = (
        None
    )
    weight: Optional[float] = None
    bloodPressureUpper: Optional[int] = None
    bloodPressureLower: Optional[int] = None
    temperature: Optional[float] = None
    temperatureType: Optional[TemperatureUnit] = None

# class PatientDTO(BaseModel):
#     # patient_id: UUID
#     # Personal Info
#     first_name: str = Field(..., max_length=50)
#     last_name: Optional[str] = Field(None, max_length=50)
#     gender: Optional[Literal["male", "female", "other"]] = None
#     date_of_birth: Optional[date] = None
#     mobile: Optional[str] = Field(None, max_length=15)
#     email: Optional[EmailStr] = None
#     address: Optional[str] = None
#
#     # Medical Info
#     blood_group: Optional[Literal["A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-"]] = (
#         None
#     )
#     # allergies: Optional[str] = None
#     # chronic_conditions: Optional[str] = None
#     # medications: Optional[str] = None
#     notes: Optional[str] = None
#
#     # Metadata
#     # is_active: bool = True
#     created_at: datetime
#     updated_at: Optional[datetime] = None
#
#     # Relationships & Extensibility
#     # assigned_doctor_id: Optional[UUID] = None
#     extra_data: Optional[Dict[str, str]] = None


class PatientOut(PatientRecord):
    name: str
    age: int

    model_config = {"from_attributes": True}
