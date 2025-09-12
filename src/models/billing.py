from pydantic import BaseModel


class BillingCreate(BaseModel):
    # id: str
    appointment_id: str
    type: str  # e.g., "cash", "card", "upi", "insurance"
    amount: float
    # currency: str = "INR"
    # status: str  # e.g., "paid", "pending"
    # issued_at: datetime
    # paid_at: Optional[datetime] = None


class BillingOut(BaseModel):
    id: str
    appointment_id: str
    type: str  # e.g., "cash", "card", "upi", "insurance"
    amount: float
