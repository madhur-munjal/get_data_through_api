import uuid
from datetime import datetime, date
from typing import Optional

from pydantic import BaseModel, Field


class SubscriptionSchema(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    plan_id: str
    start_date: str  # datetime = Field(default_factory=datetime.utcnow)
    end_date: str  # Optional[datetime] = None
    is_active: bool = True
    auto_renew: bool = False
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    model_config = {"from_attributes": True}


class SubscriptionCreate(BaseModel):
    user_id: Optional[str] = None
    plan_id: str
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    auto_renew: bool = False
    price: float = None

    model_config = {"from_attributes": True}


class SubscriptionRead(SubscriptionSchema):
    plan_id: str
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    auto_renew: bool = False

    model_config = {"from_attributes": True}


# class (SubscriptionRead):
#     plan: Optional[PlanOut] = None
#
#     model_config = {"from_attributes": True}
#
#     @classmethod
#     def from_orm(cls, obj: Any) -> Self:
#         return cls(
#             id=obj.id,
#             user_id=obj.user_id,
#             plan_id=obj.plan_id,
#             plan=PlanOut.model_validate(obj.plan) if obj.plan else None,
#             start_date=obj.start_date,
#             end_date=obj.end_date,
#             is_active=obj.is_active,
#             auto_renew=obj.auto_renew,
#             created_at=obj.created_at,
#             updated_at=obj.updated_at
#         )


class SubscriptionOutWithPlan(BaseModel):
    appointment_left: Optional[int] = None
    subscription_id: str
    user_id: str
    plan_id: str
    plan_name: str
    plan_description: Optional[list] = None
    plan_price: float
    plan_currency: str
    start_date: date
    end_date: date
    is_active: bool
    auto_renew: bool

    model_config = {"from_attributes": True}

    @classmethod
    def from_orm(cls, row):
        return cls(
            subscription_id=row.id,
            user_id=row.user_id,
            plan_id=row.plan.id,
            plan_name=row.plan.name,
            plan_description=[
                description.strip() for description in row.plan.description.split(",")
            ],
            plan_price=row.plan.price,
            plan_currency=row.plan.currency,
            start_date=row.start_date.date(),
            end_date=row.end_date.date() if row.end_date else None,
            is_active=row.is_active,
            auto_renew=row.auto_renew,
            created_at=row.created_at,
            updated_at=row.updated_at,
        )
