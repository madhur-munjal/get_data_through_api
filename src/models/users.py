from typing import Union, Optional, Annotated
import re
from pydantic import BaseModel, EmailStr, constr, StringConstraints, field_validator


ContactStr = Annotated[str, StringConstraints(pattern=r'^[6-9]\d{9}$')]
# PasswordStr = Annotated[
#     str,
#     StringConstraints(
#         pattern=r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[^A-Za-z0-9]).{8,}$',
#         min_length=8
#     )
# ]


class UserCreate(BaseModel):
    """Model used to create a new user."""
    firstName: constr(min_length=3, max_length=15)
    lastName: constr(min_length=3, max_length=15)
    email: EmailStr
    country: str
    # address: str
    contact_number: ContactStr
    username: str
    password: str

    class Config:
        orm_mode = True


    @field_validator("password", mode="after")
    def validate_password(cls, value):
        # At least one lowercase, one uppercase, one digit, one special char, min 8 chars
        pattern = r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[^A-Za-z0-9]).{8,}$'
        if not re.fullmatch(pattern, value):
            raise ValueError(
                "Password must be at least 8 characters long and include "
                "uppercase, lowercase, digit, and special character"
            )
        return value



class UserLogin(BaseModel):
    username: str
    password: str


class UserOut(BaseModel):
    id: int
    firstName: constr(min_length=3, max_length=15)
    lastName: constr(min_length=3, max_length=15)
    email: EmailStr
    country: str
    # address: str
    contact_number: ContactStr
    username: str
    # password: str

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


class VerifyOTPRequest(BaseModel):
    email: EmailStr
    otp: str

class DeleteUserRequest(BaseModel):
    user_id: int