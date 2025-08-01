from pydantic import BaseModel, EmailStr
from typing import Union, Optional


class UserCreate(BaseModel):
    username: str
    password: str
    email: EmailStr
    address: str
    contact_number: str


class UserLogin(BaseModel):
    username: str
    password: str


class UserOut(BaseModel):
    id: int
    username: str

    class Config:
        orm_mode = True


class TokenData(BaseModel):
    access_token: str
    token_type: str


class Token(BaseModel):
    """Model used to return from the login or register endpoint."""
    status_code: int = 200
    status: str = "Success"
    message: str = "User logged in successfully"
    data: Optional[Union[dict, TokenData]] = None


# class Sign_Up_details(BaseModel):
#     """Model used to return from the login or register endpoint."""
#     status_code: int = 200
#     status: str = "Success"
#     message: str = "User logged in successfully"
#     data: Optional[Union[dict, TokenData]] = None
