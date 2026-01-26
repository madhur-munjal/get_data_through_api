import datetime
from uuid import UUID

from pydantic import BaseModel
from pydantic import constr


class DevelopersTabOut(BaseModel):
    client_name: str
    brand_name: str
    subscription_plan: str
    end_date: datetime.date
    status: str

    model_config = {"from_attributes": True}

    @classmethod
    def from_row(cls, row):
        return cls(
            client_name=row.client_name,
            brand_name=row.brand_name,
            subscription_plan=row.subscription_plan,
            end_date=row.end_date,
            status=row.status
        )


class UserOut(BaseModel):
    id: UUID
    firstName: constr(min_length=3, max_length=15)
    lastName: constr(min_length=3, max_length=15)
    email: str
    country: str
    mobile: constr(min_length=5)
    username: constr(min_length=5, max_length=18)
    role: str

    model_config = {"from_attributes": True}

    @classmethod
    def from_row(cls, row):
        return cls(
            id=row.id,
            firstName=row.firstName,
            lastName=row.lastName,
            email=row.email,
            country=row.country,
            mobile=row.mobile,
            username=row.username,
            role=row.role
        )
