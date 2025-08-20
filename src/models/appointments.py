from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field
from src.models.patients import PatentCreate


class AppointmentCreate(BaseModel):
    # patient_id: int
    # doctor_id: int
    patient: PatentCreate # Nested patient data
    scheduled_time: datetime
    status: Optional[str] = Field(default="scheduled")



class AppointmentRead(BaseModel):
    id: int
    patient_id: int
    doctor_id: int
    scheduled_time: datetime
    status: str
    created_at: datetime

    model_config = {"from_attributes": True}
