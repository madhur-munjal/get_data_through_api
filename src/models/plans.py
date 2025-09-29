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
    description: Optional[list] = None
    price: float
    currency: str
    # duration_days: int

    model_config = {"from_attributes": True}

    @classmethod
    def from_row(cls, row):
        return cls(
            id=row.id,
            name=row.name,
            description=[description.strip() for description in row.description.split(",")],
            price=row.price,
            currency=row.currency,
            # duration_days=row.duration_days
        )


class PlanDetailsOnMail(BaseModel):
    plan_id: str

    model_config = {"from_attributes": True}
