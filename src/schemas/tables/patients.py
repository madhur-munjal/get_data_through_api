import enum
import uuid

from sqlalchemy import Column, Integer, String, Float, DateTime, Enum
from sqlalchemy import ForeignKey, Date
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from src.database import Base


# Enums matching your Pydantic model
class Gender(enum.Enum):
    male = "male"
    female = "female"
    other = "other"


class TemperatureUnit(enum.Enum):
    celsius = "celsius"
    fahrenheit = "fahrenheit"


class Patient(Base):
    __tablename__ = "patients"

    patient_id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    firstName = Column(String(15), nullable=False)  # mandatory
    lastName = Column(String(15), nullable=True)
    age = Column(Integer, nullable=False)  # mandatory
    mobile = Column(String(15), nullable=False)  # mandatory
    gender = Column(Enum(Gender), nullable=False)  # mandatory
    address = Column(String(45), nullable=True)
    currentVisit = Column(DateTime, nullable=True)
    lastVisit = Column(Date, nullable=True)
    bloodGroup = Column(String(5), nullable=True)  # Optional, but you can validate values in app logic
    weight = Column(Float, nullable=True)
    bloodPressureUpper = Column(Integer, nullable=True)
    bloodPressureLower = Column(Integer, nullable=True)
    temperature = Column(Float, nullable=True)
    temperatureType = Column(Enum(TemperatureUnit), nullable=True)

    assigned_doctor_id = Column(String(36), ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())

    appointments = relationship("Appointment", back_populates="patient")
    visits = relationship("Visit", back_populates="patient")

# import uuid
#
# from sqlalchemy import (
#     Column,
#     String,
#     Date,
#     Enum,
#     Boolean,
#     DateTime,
#     ForeignKey,
#     Text,
#     JSON,
# )
# from sqlalchemy.orm import relationship
# from sqlalchemy.sql import func
#
# from src.database import Base
#
#
# class Patient(Base):
#     __tablename__ = "patients"
#
#     patient_id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
#     # Personal Info
#     first_name = Column(String(50), nullable=False)
#     last_name = Column(String(50), nullable=True, default=None)
#     gender = Column(Enum("male", "female", "other"), nullable=True, default=None)
#     date_of_birth = Column(Date, nullable=True, default=None)
#     mobile = Column(String(15), unique=True)
#     email = Column(String(100), nullable=True)
#     address = Column(Text, nullable=True)
#
#     # Medical Info
#     blood_group = Column(
#         Enum("A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-"), nullable=True
#     )
#     # allergies = Column(Text, nullable=True)
#     # chronic_conditions = Column(Text, nullable=True)
#     # medications = Column(Text, nullable=True)
#     notes = Column(Text, nullable=True)
#
#     # Metadata
#     # is_active = Column(Boolean, default=True)
#     created_at = Column(DateTime, server_default=func.now())
#     updated_at = Column(DateTime, onupdate=func.now())
#
#     # Optional: Link to assigned doctor or clinic
#     assigned_doctor_id = Column(String(36), ForeignKey("users.id"), nullable=True)
#     extra_data = Column(
#         JSON, nullable=True
#     )  # For extensibility (e.g. insurance, emergency contact)
#
#     # from .appointments import Appointment
#     # from .visits import Visit
#
#     appointments = relationship("Appointment", back_populates="patient")
#     visits = relationship("Visit", back_populates="patient")
