from typing import Optional
from datetime import date, time
from pydantic import BaseModel, Field
from src.models.patients import PatientDTO, PatientOut


class AppointmentCreate(BaseModel):
    # patient_id: int
    # doctor_id: int
    patient: PatientDTO  # Nested patient data
    scheduled_date: date
    scheduled_time: time
    status: Optional[str] = Field(default="scheduled")

    model_config = {"from_attributes": True}


class AppointmentOut(BaseModel):
    patient_id: str
    doctor_id: str
    scheduled_date: date
    scheduled_time: time
    status: Optional[str] = Field(default="scheduled")

    model_config = {"from_attributes": True}
