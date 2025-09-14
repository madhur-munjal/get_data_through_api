from datetime import date
from typing import Literal, Optional, List

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
    list_of_appointments: Optional[List] = None  # List of appointment dates


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

    model_config = {"from_attributes": True}


class PatientOut(BaseModel):
    patient_id: str
    firstName: str  # Required
    lastName: Optional[str] = None
    age: Optional[int] = None
    mobile: str  # Required
    gender: Optional[Gender] = None
    address: Optional[str] = None
    lastVisit: Optional[date] = None
    bloodGroup: Optional[
        Literal["A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-"]
    ] = None
    weight: Optional[float] = None
    bloodPressureUpper: Optional[int] = None
    bloodPressureLower: Optional[int] = None
    temperature: Optional[float] = None
    temperatureType: Optional[TemperatureUnit] = None
    type: Optional[int] = None

    model_config = {"from_attributes": True}

    @classmethod
    def from_row(cls, row):
        return cls(
            patient_id=row.Patient.patient_id,
            firstName=row.Patient.firstName,
            lastName=row.Patient.lastName,
            age=row.Patient.age,
            mobile=row.Patient.mobile,
            gender=row.Patient.gender,
            address=row.Patient.address,
            lastVisit=row.Patient.lastVisit,
            bloodGroup=row.Patient.bloodGroup,
            weight=row.Patient.weight,
            bloodPressureUpper=row.Patient.bloodPressureUpper,
            bloodPressureLower=row.Patient.bloodPressureLower,
            temperature=row.Patient.temperature,
            temperatureType=row.Patient.temperatureType,
            type=row.latest_appointment_type
        )


class PaginatedPatientResponse(BaseModel):
    page: int
    page_size: int
    total_records: int
    patient_list: List[PatientOut]


class PatientUpdateWhileAppointment(BaseModel):
    patient_id: Optional[str] = None
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
