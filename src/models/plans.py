from typing import Optional

from pydantic import BaseModel


class PlanCreate(BaseModel):
    name: str
    description: Optional[str] = None
    price: float
    currency: Optional[str] = "INR"
    # duration_days: Optional[int] = 30

    model_config = {"from_attributes": True}


class PlanOut(BaseModel):
    id: str
    name: str
    description: Optional[str]
    price: float
    currency: str
    # duration_days: int

    model_config = {"from_attributes": True}
