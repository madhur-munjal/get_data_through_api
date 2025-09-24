from typing import Annotated, Optional
from uuid import UUID
from fastapi import File, UploadFile, Form
from pydantic import BaseModel, EmailStr, constr, StringConstraints, model_validator

from src.utility import validate_user_fields

ContactStr = Annotated[str, StringConstraints(pattern=r"^[6-9]\d{9}$")]


class UserCreate(BaseModel):
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


class UserLogin(BaseModel):
    username: str
    password: str


class UserOut(BaseModel):
    id: UUID
    firstName: constr(min_length=3, max_length=15)
    lastName: constr(min_length=3, max_length=15)
    email: str
    country: str
    mobile: constr(min_length=5)
    username: constr(min_length=5, max_length=18)
    role: str
    profile_image_url: Optional[str] = None

    model_config = {"from_attributes": True}

    @model_validator(mode="after")
    def validate(cls, values):
        return validate_user_fields(values, cls)


class ForgotPasswordRequest(BaseModel):
    username: str
    email: str


class ResetPasswordRequest(BaseModel):
    email: EmailStr
    new_password: str

    @model_validator(mode="after")
    def validate(cls, values):
        return validate_user_fields(values, cls)


class VerifyOTPRequest(BaseModel):
    email: str
    otp: str

    @model_validator(mode="after")
    def validate(cls, values):
        return validate_user_fields(values, cls)


class UserIDRequest(BaseModel):
    user_id: str


class UpdateLoginRecord(BaseModel):
    mobile: Optional[str] = Form(None),
    current_password: Optional[str] = Form(None),
    password: Optional[constr(min_length=5)] = Form(None),
    image: Optional[UploadFile] = File(None)

    # mobile: Optional[str] = None
    # current_password: Optional[str] = None
    # password: Optional[constr(min_length=5)] = None
    # image: Optional[UploadFile] = File(None)
    # confirm_password: Optional[constr(min_length=5)] = None

    model_config = {"from_attributes": True}

    @model_validator(mode="after")
    def validate(cls, values):
        return validate_user_fields(values, cls)

