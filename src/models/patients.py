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

    model_config = {"from_attributes": True}

    @classmethod
    def from_row(cls, row):
        return cls(
            patient_id=row.patient_id,
            firstName=row.patient.firstName,
            lastName=row.patient.lastName,
            age=row.patient.age,
            mobile=row.patient.mobile,
            gender=row.patient.gender,
            address=row.patient.address,
            lastVisit=row.patient.lastVisit,
            bloodGroup=row.patient.bloodGroup,
            weight=row.patient.weight,
            bloodPressureUpper=row.patient.bloodPressureUpper,
            bloodPressureLower=row.patient.bloodPressureLower,
            temperature=row.patient.temperature,
            temperatureType=row.patient.temperatureType
        )


class PatientAppointmentResponse(BaseModel):
    patient_details: PatientRecord
    list_of_appointments: List


class PaginatedPatientResponse(BaseModel):
    page: int
    page_size: int
    total_records: int
    patient_list: List[PatientOut]

