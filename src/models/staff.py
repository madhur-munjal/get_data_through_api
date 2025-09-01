from typing import Optional, Annotated
from uuid import UUID

from pydantic import BaseModel, constr, StringConstraints, model_validator

from src.utility import validate_user_fields

ContactStr = Annotated[str, StringConstraints(pattern=r"^[6-9]\d{9}$")]


class StaffCreate(BaseModel):
    """Model used to create a new user."""

    firstName: constr(min_length=3, max_length=15)  # Required
    lastName: Optional[constr(min_length=3, max_length=15)] = None
    email: str  # Required
    country: Optional[str] = None
    mobile: constr(min_length=5)  # Required
    username: constr(min_length=5, max_length=18)  # Required
    password: constr(min_length=5)  # Required

    model_config = {"from_attributes": True}

    @model_validator(mode="after")
    def validate(cls, values):
        return validate_user_fields(values, cls)


class StaffOut(BaseModel):
    id: UUID
    firstName: constr(min_length=3, max_length=15)
    lastName: Optional[constr(min_length=3, max_length=15)] = None
    email: str
    country: Optional[str] = None
    mobile: constr(min_length=5)
    username: constr(min_length=5, max_length=18)
    role: str

    model_config = {"from_attributes": True}

    @model_validator(mode="after")
    def validate(cls, values):
        return validate_user_fields(values, cls)
