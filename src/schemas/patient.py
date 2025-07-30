from pydantic import BaseModel, Field
from typing import Optional, Dict, Any

from pydantic import BaseModel, EmailStr
from typing import Optional

import datetime


# class PatientResource(BaseModel):
#     """
#
#     """
#     # __tablename__ = "patient"
#     patient_id: int = Field(None, description="Unique identifier for the patient", example=1)
#     first_name: str = Field(None, description="First name of the patient", example="John")
#     last_name: str = Field(None, description="Last name of the patient", example="Doe")
#     phone_number: str = Field(None, description="Phone number of the patient", example="+1234567890")
#     address: str = Field(None, description="Address of the patient", example="123 Main St, City, Country")


class PatentBase(BaseModel):
    name: str
    address: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[EmailStr] = None
    description: Optional[str] = None

class PatentCreate(PatentBase):
    pass  # Same as PatentBase, used for incoming creation requests

class PatentUpdate(PatentBase):
    pass  # Optional: Customize fields to allow partial updates

class PatentOut(PatentBase):
    id: int

    class Config:
        orm_mode = True