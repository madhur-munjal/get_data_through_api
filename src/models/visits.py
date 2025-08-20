from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class VisitCreate(BaseModel):
    patient_id: int
    doctor_id: int
    appointment_id: Optional[int] = None
    visit_time: Optional[datetime] = None
    notes: Optional[str] = None
    diagnosis: Optional[str] = None
    prescription: Optional[str] = None


class VisitRead(BaseModel):
    id: int
    patient_id: int
    doctor_id: int
    appointment_id: Optional[int]
    visit_time: datetime
    notes: Optional[str]
    diagnosis: Optional[str]
    prescription: Optional[str]

    model_config = {"from_attributes": True}
