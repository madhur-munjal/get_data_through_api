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
