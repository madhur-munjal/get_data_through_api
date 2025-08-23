from datetime import datetime
from typing import Optional
from uuid import UUID
from pydantic import BaseModel

from .patients import PatientOut


class VisitDB(BaseModel):
    id: UUID
    patient_id: int
    doctor_id: int
    appointment_id: Optional[int] = None
    # visit_time: datetime = None
    # notes: Optional[str] = None
    # diagnosis: Optional[str] = None
    prescription: Optional[str] = None

    model_config = {"from_attributes": True}


class PrescriptionData(BaseModel):
    medicines: list
    model_config = {"from_attributes": True}


class VisitCreate(BaseModel):
    # id: int
    # patient_id: int
    # doctor_id: int
    appointment_id: UUID
    # visit_time: datetime = None
    # notes: Optional[str] = None
    # diagnosis: Optional[str] = None
    prescription: Optional[str] = None  # Need to changee to PrescriptionData
    follow_up: Optional[str]

    model_config = {"from_attributes": True}


class VisitOut(BaseModel):
    patient: PatientOut
    visit_time: datetime
    notes: Optional[str]
    diagnosis: Optional[str]
    prescription: Optional[str]

    model_config = {"from_attributes": True}
