from datetime import date, time
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field

from src.models.patients import PatientRecord


class AppointmentType(str, Enum):
    new = "new"
    follow_up = "follow-up"


class AppointmentCreate(BaseModel):
    # patient_id: int
    # doctor_id: int
    patient: PatientRecord  # Nested patient data
    scheduled_date: date
    scheduled_time: time
    type: AppointmentType  # Optional[str] = Field(default="general")
    status: Optional[str] = Field(default="scheduled")
    model_config = {"from_attributes": True}


class AppointmentOut(BaseModel):
    patient_id: str
    doctor_id: str
    scheduled_date: date
    scheduled_time: time
    status: Optional[str] = Field(default="scheduled")

    model_config = {"from_attributes": True}
