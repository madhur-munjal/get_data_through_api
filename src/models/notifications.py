from pydantic import BaseModel, computed_field
from datetime import datetime, date, time
from typing import Optional, Literal, List


class NotificationUpdateRequest(BaseModel):
    mark_all_as_read: bool
    id: Optional[List[str]] = []

    model_config = {"from_attributes": True}


class NotificationOut(BaseModel):
    id: str
    doctor_id: str
    appointment_id: Optional[str] = None
    billing_id: Optional[str] = None
    firstName: str
    lastName: Optional[str] = None
    type: Optional[str] = None  # e.g., 'appointment', 'payment'
    message: Optional[str]
    read: bool = False
    updated_by: str
    created_at: datetime
    # Derived fields
    # created_date: date  # = Field(default_factory=lambda: datetime.utcnow().date())
    # created_time: time  # = Field(default_factory=lambda: datetime.utcnow().time())

    # created_date: datetime # = Field(default_factory=datetime.utcnow)
    # created_time: time

    @computed_field
    @property
    def created_date(self) -> date:
        return self.created_at.date()

    @computed_field
    @property
    def created_time(self) -> time:
        return self.created_at.time()

    model_config = {"from_attributes": True}
