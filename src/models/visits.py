from datetime import datetime
from typing import Optional

from pydantic import BaseModel
from .patients import PatientOut


class VisitCreate(BaseModel):
    id: int
    patient_id: int
    doctor_id: int
    appointment_id: Optional[int] = None
    visit_time: datetime = None
    notes: Optional[str] = None
    diagnosis: Optional[str] = None
    prescription: Optional[str] = None

    model_config = {"from_attributes": True}


class VisitOut(BaseModel):
    patient: PatientOut
    visit_time: datetime
    notes: Optional[str]
    diagnosis: Optional[str]
    prescription: Optional[str]

    model_config = {"from_attributes": True}
