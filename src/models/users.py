from typing import Annotated, Optional
from uuid import UUID
from fastapi import File, UploadFile, Form
from pydantic import BaseModel, EmailStr, constr, StringConstraints, model_validator
from pydantic import HttpUrl
from src.utility import validate_user_fields
from fastapi import Request

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


class UserUpdate(BaseModel):
    """Model used to update an existing user."""

    firstName: Optional[constr(min_length=3, max_length=15)] = None
    lastName: Optional[constr(min_length=3, max_length=15)] = None
    email: Optional[str] = None
    country: Optional[str] = None
    mobile: Optional[constr(min_length=5)] = None
    username: Optional[constr(min_length=5, max_length=18)] = None
    password: Optional[constr(min_length=5)] = None

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



    @model_validator(mode="after")
    def validate(cls, values):
        return validate_user_fields(values, cls)

    @staticmethod
    def build_image_url(user_obj) -> Optional[str]:
        image_filename = user_obj.profile_image_url  # e.g., "id.jpg"
        if image_filename:
            # base_url = request.base_url._url.rstrip("/")
            # return base_url + f"/static/{image_filename}"
            return f"https://smarthealapp.com/images/{image_filename}"
        # if filename:
        #     return f"https://smarthealapp.com/static/{filename}"
        return None

    @classmethod
    def from_orm_with_image(cls, user_obj):
        data = user_obj.__dict__.copy()
        data["profile_image_url"] = cls.build_image_url(user_obj)
        return cls(**data)

    model_config = {"from_attributes": True}


class ForgotPasswordRequest(BaseModel):
    username: str
    email: str


class ResetPasswordRequest(BaseModel):
    email: EmailStr
    password: constr(min_length=5)  # Required

    model_config = {"from_attributes": True}

    @model_validator(mode="after")
    def validate(cls, values):
        return validate_user_fields(values, cls)
    # password: str
    #
    # model_config = {"from_attributes": True}
    #
    # @model_validator(mode="after")
    # def validate(cls, values):
    #     return validate_user_fields(values, cls)



class VerifyOTPRequest(BaseModel):
    otp: str
    token: str

    model_config = {"from_attributes": True}


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

