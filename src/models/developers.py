import datetime
from datetime import date
from typing import Optional
from uuid import UUID

from pydantic import BaseModel
from pydantic import constr
from pydantic import model_validator

from src.utility import get_appointments_left_by_doctor, get_staff_left_count, get_staff_left_doctor_count
from src.utility import validate_user_fields


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
    staff_left_nondoctor: int  # 0
    staff_left_doctor: int  # 0

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
            staff_left_nondoctor=get_staff_left_count(db, user.id),
            staff_left_doctor=get_staff_left_doctor_count(db, user.id),
        )


class SubscriptionUpdate(BaseModel):
    plan_name: Optional[str] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    is_active: Optional[bool] = None


class DeveloperUserUpdate(BaseModel):
    user_id: str  # Required
    firstName: Optional[constr(min_length=3, max_length=15)] = None
    lastName: Optional[constr(min_length=3, max_length=15)] = None
    email: Optional[str]
    country: Optional[str] = None
    mobile: Optional[constr(min_length=5)] = None
    subscription: Optional[SubscriptionUpdate] = None

    model_config = {"from_attributes": True}

    @model_validator(mode="after")
    def validate(cls, values):
        return validate_user_fields(values, cls)


class SubscriptionWithPlan(BaseModel):
    subscription_id: str
    plan_id: str
    plan_name: str
    plan_description: Optional[list] = None
    plan_price: float
    plan_currency: str
    subscription_startDate: date
    subscription_endDate: date
    is_active: bool
    created_at: datetime.datetime
    updated_at: datetime.datetime

    model_config = {"from_attributes": True}

    @classmethod
    def from_orm(cls, row):
        return cls(
            subscription_id=row.id,
            plan_id=row.plan.id,
            plan_name=row.plan.name,
            plan_description=[
                description.strip() for description in row.plan.description.split(",")
            ],
            plan_price=row.plan.price,
            plan_currency=row.plan.currency,
            subscription_startDate=row.start_date.date(),
            subscription_endDate=row.end_date.date() if row.end_date else None,
            is_active=row.is_active,
            created_at=row.created_at,
            updated_at=row.updated_at,
        )


class UserWithAllSubscription(BaseModel):
    user_id: str
    firstName: constr(min_length=3, max_length=15)
    lastName: constr(min_length=3, max_length=15)
    email: str
    country: str
    mobile: constr(min_length=5)
    username: constr(min_length=5, max_length=18)
    role: str
    appointment_left: int  # 110 - actual,
    staff_left_nondoctor: int  # 0
    staff_left_doctor: int  # 0
    subscription: list[SubscriptionWithPlan] = []

    model_config = {"from_attributes": True}

    @classmethod
    def from_row(cls, db, user_row):
        return cls(
            user_id=user_row.id,
            firstName=user_row.firstName,
            lastName=user_row.lastName,
            email=user_row.email,
            country=user_row.country,
            mobile=user_row.mobile,
            username=user_row.username,
            role=user_row.role,
            appointment_left=get_appointments_left_by_doctor(db, user_row.id),
            staff_left_nondoctor=get_staff_left_count(db, user_row.id),
            staff_left_doctor=get_staff_left_doctor_count(db, user_row.id),
            subscription=[
                SubscriptionWithPlan.from_orm(sub) for sub in user_row.subscription
            ],
        )
