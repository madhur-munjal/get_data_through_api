from datetime import date, time, datetime
from .enums import AppointmentStatus
from typing import Optional

from pydantic import BaseModel, Field

from src.models.patients import PatientRecord
from src.utility import get_appointment_status



class AppointmentCreate(BaseModel):
    patient: PatientRecord  # Nested patient data
    # scheduled_date_time: datetime
    scheduled_date: str # "08/25/2025"
    scheduled_time: str # "16:00:00"

    model_config = {"from_attributes": True}


class AppointmentOut(BaseModel):
    """Schema for appointment output, used in response of create_appointment and update appointment API"""
    patient_id: str
    doctor_id: str
    # scheduled_date_time: datetime
    scheduled_date: date
    scheduled_time: time
    status: int = Field(default=AppointmentStatus.UPCOMING) # AppointmentStatus

    model_config = {"from_attributes": True}


class AppointmentResponse(BaseModel):
    """Schema for appointment output., used in get_appointment_list API"""
    appointment_id: str
    scheduled_date: str
    scheduled_time: str
    patient_id: str
    mobile: str  # Required
    type: int
    status: int #AppointmentStatus
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
            status=get_appointment_status(datetime.combine(row.scheduled_date, row.scheduled_time))
            # get_appointment_status(row.scheduled_date_time) if row.scheduled_date_time else None
        )

    model_config = {"from_attributes": True}
