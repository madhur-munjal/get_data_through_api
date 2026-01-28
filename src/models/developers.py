import datetime
from uuid import UUID

from pydantic import BaseModel
from pydantic import constr
from src.utility import get_appointments_left_by_doctor

from typing import Optional
from datetime import date


class DevelopersTabOut(BaseModel):
    id: UUID
    firstName: constr(min_length=3, max_length=15)
    lastName: constr(min_length=3, max_length=15)
    email: str
    country: str
    mobile: constr(min_length=5)
    username: constr(min_length=5, max_length=18)
    role: str
    subscription: str
    subscription_startDate: datetime.datetime  # '2026-01-20',
    subscription_endDate: datetime.datetime  # '2026-12-30',
    isActive: bool  # true,
    appointment_left: int  # 110 - actual,

    model_config = {"from_attributes": True}

    @classmethod
    def from_row(cls, db, user, subscription):
        return cls(
            id=user.id,
            firstName=user.firstName,
            lastName=user.lastName,
            email=user.email,
            country=user.country,
            mobile=user.mobile,
            username=user.username,
            role=user.role,
            subscription=subscription.plan.name,
            subscription_startDate=subscription.start_date,
            subscription_endDate=subscription.end_date,
            isActive=subscription.is_active,
            appointment_left=get_appointments_left_by_doctor(db, user.id),
        )


class SubscriptionUpdate(BaseModel):
    # plan_name: Optional[str] = None
    # start_date: Optional[date] = None
    end_date: Optional[date] = None
    is_active: Optional[bool] = None


class UserUpdate(BaseModel):
    firstName: Optional[constr(min_length=3, max_length=15)]  # Required
    lastName: Optional[constr(min_length=3, max_length=15)] = None
    email: Optional[str]
    country: Optional[str] = None
    subscription: Optional[SubscriptionUpdate] = None
