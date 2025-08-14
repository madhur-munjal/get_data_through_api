from typing import Union, Optional, Annotated
import re
from pydantic import BaseModel, EmailStr, constr, StringConstraints, model_validator, ValidationError
from pydantic_core import InitErrorDetails, PydanticCustomError
from src.utility import validate_user_fields

# PASSWORD_REGEX = re.compile("^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[^A-Za-z0-9]).{8,}$")
# USERNAME_REGEX = re.compile("^(?=[a-zA-Z])(?=.[._-])(?!.[.-]{2})[a-zA-Z][a-zA-Z0-9.-]{1,18}[a-zA-Z0-9]$")
# EMAIL_REGEX = re.compile("^[a-z0-9._%+-]+@[a-z0-9.-]+\\.[a-z]{2,4}$")  # Indian mobile numbers

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

    class Config:
        orm_mode = True

    @model_validator(mode="after")
    def validate(cls, values):
        return validate_user_fields(values, cls)


    # @model_validator(mode="after")
    # def validate_all(cls, values):
    #     errors: list[InitErrorDetails] = []
    #
    #     # Email validation
    #     if not EMAIL_REGEX.fullmatch(values.email):
    #         errors.append(
    #             InitErrorDetails(
    #                 type=PydanticCustomError("value_error", "Invalid email format"),
    #                 loc=("email",),
    #                 input=values.email
    #             )
    #         )
    #
    #     # Username validation
    #     if not USERNAME_REGEX.fullmatch(values.username):
    #         errors.append(
    #             InitErrorDetails(
    #                 type=PydanticCustomError("value_error", "Invalid username format"),
    #                 loc=("username",),
    #                 input=values.username
    #             )
    #         )
    #
    #     # Password validation
    #     if not PASSWORD_REGEX.fullmatch(values.password):
    #         errors.append(
    #             InitErrorDetails(
    #                 type=PydanticCustomError("value_error", "Invalid password format, Password must be at least 8 characters long and include uppercase, lowercase, digit, and special character"),
    #                 loc=("password",),
    #                 input=values.username
    #             )
    #         )
    #
    #     if errors:
    #         raise ValidationError.from_exception_data(cls, errors)
    #
    #     return values


    # @field_validator("password", mode="after")
    # def validate_password(cls, value):
    #     # At least one lowercase, one uppercase, one digit, one special char, min 8 chars
    #     pattern = '^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[^A-Za-z0-9]).{8,}$'
    #     if not re.fullmatch(pattern, value):
    #         raise ValueError(
    #             "Password must be at least 8 characters long and include "
    #             "uppercase, lowercase, digit, and special character"
    #         )
    #     return value
    #
    # @field_validator("username", mode="after")
    # def validate_username(cls, value):
    #     # At least one lowercase, one uppercase, one digit, one special char, min 8 chars
    #     pattern = '^(?=[a-zA-Z])(?=.[._-])(?!.[.-]{2})[a-zA-Z][a-zA-Z0-9.-]{1,18}[a-zA-Z0-9]$'
    #     if not re.fullmatch(pattern, value):
    #         raise ValueError(
    #             "Invalid Username"
    #         )
    #     return value
    #
    # @field_validator("email", mode="after")
    # def validate_email(cls, value):
    #     # At least one lowercase, one uppercase, one digit, one special char, min 8 chars
    #     pattern = '^[a-z0-9._%+-]+@[a-z0-9.-]+\\.[a-z]{2,4}$'
    #     if not re.fullmatch(pattern, value):
    #         raise ValueError(
    #             "Invalid Email format"
    #         )
    #     return value



class UserLogin(BaseModel):
    username: str
    password: str


class UserOut(BaseModel):
    id: int
    firstName: constr(min_length=3, max_length=15)
    lastName: constr(min_length=3, max_length=15)
    email: str
    country: str
    mobile: constr(min_length=5)
    username: constr(min_length=5, max_length=18)

    model_config = {
        "from_attributes": True
    }


class TokenData(BaseModel):
    access_token: str
    token_type: str


class Token(BaseModel):
    """Model used to return from the login or register endpoint."""
    status_code: int = 200
    status: str = "Success"
    message: str = "User logged in successfully"
    data: Optional[Union[dict, TokenData]] = None


class ForgotPasswordRequest(BaseModel):
    username: str
    email: EmailStr


class ResetPasswordRequest(BaseModel):
    email: EmailStr
    new_password: str

    @model_validator(mode="after")
    def validate(cls, values):
        return validate_user_fields(values, cls)

    # @field_validator("new_password", mode="after")
    # def validate_password(cls, value):
    #     # At least one lowercase, one uppercase, one digit, one special char, min 8 chars
    #     pattern = r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[^A-Za-z0-9]).{8,}$'
    #     if not re.fullmatch(pattern, value):
    #         raise ValueError(
    #             "Password must be at least 8 characters long and include "
    #             "uppercase, lowercase, digit, and special character"
    #         )
    #     return value



class VerifyOTPRequest(BaseModel):
    email: EmailStr
    otp: str

class DeleteUserRequest(BaseModel):
    user_id: int