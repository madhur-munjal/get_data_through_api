from typing import Optional, Annotated
from uuid import UUID
from fastapi import Request
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
    role: str  # Required
    sendToEmail: Optional[bool] = False

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
    profile_image_url: Optional[str] = None

    model_config = {"from_attributes": True}

    @model_validator(mode="after")
    def validate(cls, values):
        return validate_user_fields(values, cls)

    @staticmethod
    def build_image_url(staff_obj) -> Optional[str]:  # , request: Request
        image_filename = staff_obj.profile_image_url  # e.g., "id.jpg"
        if image_filename:
            # base_url = request.base_url._url.rstrip("/")
            return f"https://api.smarthealapp.com/images/{image_filename}"
        #
        # if filename:
        #     return f"https://smarthealapp.com/static/{filename}"
        return None

    # @classmethod
    # def from_orm_with_image(cls, staff_obj):
    #     data = staff_obj.__dict__.copy()
    #     data["profile_image_url"] = cls.build_image_url(staff_obj)
    #     return cls(**data)


class DeleteStaffRequest(BaseModel):
    id: str


class StaffUpdate(BaseModel):
    id: str
    firstName: constr(min_length=3, max_length=15)
    lastName: Optional[constr(min_length=3, max_length=15)] = None
    email: str
    country: Optional[str] = None
    mobile: constr(min_length=5)
    username: constr(min_length=5, max_length=18)
    role: str
    # password: Optional[constr(min_length=5)] = None
    sendToEmail: bool

    model_config = {"from_attributes": True}

    # @model_validator(mode="after")
    # def validate(cls, values):
    #     return validate_user_fields(values, cls)
