from datetime import date
from typing import Literal, Optional, List, Dict, Any

from pydantic import BaseModel, field_validator

from .enums import Gender, TemperatureUnit


class PatientRecord(BaseModel):
    patient_code: str
    firstName: str  # Required
    lastName: Optional[str] = None
    age: Optional[int] = None
    mobile: str  # Required
    gender: Optional[Gender] = None
    address: Optional[str] = None
    list_of_appointments: Optional[List] = None  # List of appointment dates

    model_config = {"from_attributes": True}


class PatientUpdate(BaseModel):
    firstName: str  # Required
    lastName: Optional[str] = None
    age: Optional[int] = None
    mobile: str  # Required
    gender: Optional[Gender] = None
    address: Optional[str] = None

    model_config = {"from_attributes": True}


class PatientOut(BaseModel):
    patient_id: str
    patient_code: str
    firstName: str  # Required
    lastName: Optional[str] = None
    age: Optional[int] = None
    mobile: str  # Required
    gender: Optional[Gender] = None
    address: Optional[str] = None
    lastVisit: Optional[date] = None
    type: Optional[int] = None

    model_config = {"from_attributes": True}

    @classmethod
    def from_row(cls, row):
        return cls(
            patient_id=row.Patient.patient_id,
            patient_code=row.Patient.patient_code,
            firstName=row.Patient.firstName,
            lastName=row.Patient.lastName,
            age=row.Patient.age,
            mobile=row.Patient.mobile,
            gender=row.Patient.gender,
            address=row.Patient.address,
            lastVisit=row.Patient.lastVisit,
            type=row.latest_appointment_type,
        )


class PaginatedPatientResponse(BaseModel):
    page: Optional[int] = None
    page_size: Optional[int] = None
    total_records: int
    patient_list: List[PatientOut]


class PatientUpdateWhileAppointment(BaseModel):
    patient_id: Optional[str] = None
    firstName: Optional[str]  # Required
    lastName: Optional[str] = None
    age: Optional[int] = None
    mobile: Optional[str]  # Required
    gender: Optional[Gender] = None
    address: Optional[str] = None

    model_config = {"from_attributes": True}
