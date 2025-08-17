import uuid

from sqlalchemy import (
    Column, String, Date, Enum, Boolean, DateTime, ForeignKey, Text, JSON
)
from sqlalchemy.dialects.mysql import BINARY
from sqlalchemy.sql import func

from src.database import Base


class Patient(Base):
    __tablename__ = "patients"

    patient_id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    __table_args__ = (
        # Add any additional constraints here if needed
    )
    # Personal Info
    first_name = Column(String(50), nullable=False)
    last_name = Column(String(50), nullable=True)
    gender = Column(Enum("male", "female", "other"), nullable=True)
    date_of_birth = Column(Date, nullable=True)
    phone = Column(String(15), nullable=True) # Change this to mobile
    email = Column(String(100), nullable=True)
    address = Column(Text, nullable=True)

    # Medical Info
    blood_group = Column(Enum("A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-"), nullable=True)
    allergies = Column(Text, nullable=True)
    chronic_conditions = Column(Text, nullable=True)
    medications = Column(Text, nullable=True)
    notes = Column(Text, nullable=True)

    # Metadata
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())

    # Optional: Link to assigned doctor or clinic
    assigned_doctor_id = Column(String(36), ForeignKey("users.id"), nullable=True)
    extra_data = Column(JSON, nullable=True)  # For extensibility (e.g. insurance, emergency contact)
