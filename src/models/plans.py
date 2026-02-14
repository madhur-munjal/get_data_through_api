from typing import Optional

from pydantic import BaseModel


class PlanCreate(BaseModel):
    name: str
    description: str
    price: Optional[float] = None
    currency: Optional[str] = "INR"
    s_no: int
    duration_months: Optional[int] = None

    model_config = {"from_attributes": True}


class PlanOut(BaseModel):
    id: str
    s_no: int
    name: str
    description: Optional[list] = None
    price: Optional[float] = None
    currency: Optional[str] = None
    duration_months: Optional[int] = None

    model_config = {"from_attributes": True}

    @classmethod
    def from_row(cls, row):
        return cls(
            id=row.id,
            name=row.name,
            description=[
                description.strip() for description in row.description.split(",")
            ],
            price=row.price,
            currency=row.currency,
            s_no=row.s_no,
            duration_months=row.duration_months,
        )


class PlanDetailsOnMail(BaseModel):
    plan_id: str
    name: Optional[str] = None
    email: Optional[str] = None
    company_name: Optional[str] = None
    description: Optional[str] = None

    model_config = {"from_attributes": True}
