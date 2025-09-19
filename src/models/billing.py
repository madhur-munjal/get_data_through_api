import datetime
from typing import Optional
from pydantic import BaseModel

from .enums import BillingTypeEnum


class BillingCreate(BaseModel):
    appointment_id: str
    type: BillingTypeEnum  # e.g., "cash", "card", "upi", "insurance"
    amount: float
    # currency: str = "INR"
    # status: str  # e.g., "paid", "pending"
    # issued_at: datetime
    # paid_at: Optional[datetime] = None

    model_config = {"from_attributes": True}


class BillingOut(BaseModel):
    appointment_id: str
    type: str  # e.g., "cash", "card", "upi", "insurance"
    amount: float

    model_config = {"from_attributes": True}


class DoctorsBillingInput(BaseModel):
    name: str
    upi_id: str
    currency: str

    model_config = {"from_attributes": True}


class DoctorsBillingSave(BaseModel):
    doctor_id: str
    name: str
    upi_id: str
    currency: str

    model_config = {"from_attributes": True}


class BillingDetails(BaseModel):
    patient_firstName: str
    patient_lastName: Optional[str]
    billing_id: str
    BillingDate: datetime.date
    BillingType: str  # e.g., "cash", "card", "upi", "insurance"
    ReceivedBy: Optional[str]
    amount: float

    model_config = {"from_attributes": True}

    @classmethod
    def from_billing_row(cls, row):
        return cls(
            patient_firstName=row.appointment.patient.firstName,
            patient_lastName=row.appointment.patient.lastName,
            billing_id=row.billing_id,
            BillingDate=row.created_at.date(),
            BillingType=row.type,
            ReceivedBy=row.created_by,
            amount=row.amount,
        )
