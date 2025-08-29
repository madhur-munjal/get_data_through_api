from datetime import date, time
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field

from src.models.patients import PatientRecord


class AppointmentStatus(str, Enum):
    UPCOMING = 0
    COMPLETED = 1
    NO_SHOW = 2


class AppointmentType(str, Enum):
    NEW = 0
    FOLLOW_UP = 1
    EMERGENCY = 2


class AppointmentCreate(BaseModel):
    patient: PatientRecord  # Nested patient data
    scheduled_date: date
    scheduled_time: time

    model_config = {"from_attributes": True}


class AppointmentOut(BaseModel):
    """Schema for appointment output, used in response of create_appointment and update appointment API"""
    patient_id: str
    doctor_id: str
    scheduled_date: date
    scheduled_time: time
    status: int = Field(default=AppointmentStatus.UPCOMING) # AppointmentStatus

    model_config = {"from_attributes": True}


class AppointmentResponse(BaseModel):
    """Schema for appointment output., used in get_appointment_list API"""
    appointment_id: str
    scheduled_date: date
    scheduled_time: time
    patient_id: str
    type: int
    status: int #AppointmentStatus
    firstName: Optional[str] = None
    lastName: Optional[str] = None

    model_config = {"from_attributes": True}

    @classmethod
    def from_row(cls, row):
        return cls(
            appointment_id=row.id,
            scheduled_date=row.scheduled_date,
            scheduled_time=row.scheduled_time,  # datetime.strptime( "%H:%M"),
            patient_id=row.patient_id,
            firstName=row.patient.firstName,
            lastName=row.patient.lastName,
            type=row.type,
            status=row.status
        )

    model_config = {"from_attributes": True}
