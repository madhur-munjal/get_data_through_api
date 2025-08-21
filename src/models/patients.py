from uuid import UUID
from datetime import date, datetime
from pydantic import BaseModel, EmailStr, Field
from typing import Optional, Literal, Dict


class PatientDTO(BaseModel):
    # patient_id: UUID
    # Personal Info
    first_name: str = Field(..., max_length=50)
    last_name: Optional[str] = Field(None, max_length=50)
    gender: Optional[Literal["male", "female", "other"]] = None
    date_of_birth: Optional[date] = None
    mobile: Optional[str] = Field(None, max_length=15)
    email: Optional[EmailStr] = None
    address: Optional[str] = None

    # Medical Info
    blood_group: Optional[Literal["A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-"]] = (
        None
    )
    allergies: Optional[str] = None
    chronic_conditions: Optional[str] = None
    medications: Optional[str] = None
    notes: Optional[str] = None

    # Metadata
    is_active: bool = True
    created_at: datetime
    updated_at: Optional[datetime] = None

    # Relationships & Extensibility
    # assigned_doctor_id: Optional[UUID] = None
    extra_data: Optional[Dict[str, str]] = None


# # TODO: verify the fields data type
# class PatentCreate(PatientDTO):
#     pass  # Same as PatentBase, used for incoming creation requests


class PatentUpdate(PatientDTO):
    pass  # Optional: Customize fields to allow partial updates


class PatientOut(PatientDTO):
    name: str
    age: int

    model_config = {"from_attributes": True}

