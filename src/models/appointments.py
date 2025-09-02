from datetime import date, time, datetime
from typing import Optional, Literal

from pydantic import BaseModel, Field

from src.models.patients import PatientRecord
from src.utility import get_appointment_status
from .enums import AppointmentStatus
from .enums import Gender, TemperatureUnit


class AppointmentCreate(BaseModel):
    patient: PatientRecord  # Nested patient data
    # scheduled_date_time: datetime
    scheduled_date: str  # "08/25/2025"
    scheduled_time: str  # "16:00:00"

    model_config = {"from_attributes": True}


class AppointmentOut(BaseModel):
    """Schema for appointment output, used in response of create_appointment and update appointment API"""
    patient_id: str
    doctor_id: str
    # scheduled_date_time: datetime
    scheduled_date: date
    scheduled_time: time
    status: int = Field(default=AppointmentStatus.UPCOMING)  # AppointmentStatus

    model_config = {"from_attributes": True}


class AppointmentResponse(BaseModel):
    """Schema for appointment output., used in get_appointment_list API"""
    appointment_id: str
    scheduled_date: str
    scheduled_time: str
    patient_id: str
    mobile: str  # Required
    type: int
    status: int  # AppointmentStatus
    firstName: Optional[str] = None
    lastName: Optional[str] = None

    model_config = {"from_attributes": True}

    @classmethod
    def from_row(cls, row):
        return cls(
            appointment_id=row.id,
            scheduled_date=row.scheduled_date.strftime("%m/%d/%Y"),
            scheduled_time=row.scheduled_time.strftime("%H:%M:%S"),  # datetime.strptime( "%H:%M"),
            patient_id=row.patient_id,
            mobile=row.patient.mobile,
            firstName=row.patient.firstName,
            lastName=row.patient.lastName,
            type=row.type,
            status=get_appointment_status(datetime.combine(row.scheduled_date, row.scheduled_time)) if str(
                row.status) != AppointmentStatus.COMPLETED.value else row.status
        )


class AppointmentUpdate(BaseModel):
    # patient: PatientRecord  # Nested patient data
    # scheduled_date_time: datetime
    scheduled_date: str  # "08/25/2025"
    scheduled_time: str  # "16:00:00"


class AppointmentById(BaseModel):
    """Schema to get patient and appointment details by appointment id"""
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
    # patient: PatientOut
    type: int
    status: int

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
            temperatureType=row.patient.temperatureType,
            type=row.type,
            status=row.status
        )

    @classmethod
    def from_visit_row(cls, row):
        return cls(
            appointment_id=row.id,
            scheduled_date=row.appointments.scheduled_date.strftime("%m/%d/%Y"),
            scheduled_time=row.appointments.scheduled_time.strftime("%H:%M:%S"),  # datetime.strptime( "%H:%M"),
            patient_id=row.patient_id,
            mobile=row.patient.mobile,
            firstName=row.patient.firstName,
            lastName=row.patient.lastName,
            type=row.appointments.type,
            status=get_appointment_status(datetime.combine(row.appointments.scheduled_date, row.appointments.scheduled_time)) if str(
                row.appointments.status) != AppointmentStatus.COMPLETED.value else row.appointments.status
        )
