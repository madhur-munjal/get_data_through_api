from typing import Union, Optional, Annotated
from uuid import UUID
from pydantic import BaseModel, EmailStr, constr, StringConstraints, model_validator

from src.utility import validate_user_fields

ContactStr = Annotated[str, StringConstraints(pattern=r'^[6-9]\d{9}$')]


class UserCreate(BaseModel):
    """Model used to create a new user."""
    firstName: constr(min_length=3, max_length=15)
    lastName: constr(min_length=3, max_length=15)
    email: str
    country: str
    mobile: constr(min_length=5)
    username: constr(min_length=5, max_length=18)
    password: constr(min_length=5)

    model_config = {
        "from_attributes": True
    }

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

    model_config = {
        "from_attributes": True
    }

    @model_validator(mode="after")
    def validate(cls, values):
        return validate_user_fields(values, cls)


# class TokenData(BaseModel):
#     access_token: str
#     token_type: str
#
#
# class Token(BaseModel):
#     """Model used to return from the login or register endpoint."""
#     status_code: int = 200
#     status: str = "Success"
#     message: str = "User logged in successfully"
#     data: Optional[Union[dict, TokenData]] = None


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


class DeleteUserRequest(BaseModel):
    user_id: int


# class ItemUpdate(BaseModel):
#     name: str | None = None
#     description: str | None = None
