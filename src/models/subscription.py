import uuid
from datetime import datetime
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
    # user_id: str
    plan_id: str
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    auto_renew: bool = False

    model_config = {"from_attributes": True}


class SubscriptionRead(SubscriptionSchema):
    plan_id: str
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    auto_renew: bool = False

    model_config = {"from_attributes": True}

