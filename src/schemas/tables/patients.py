import enum
import uuid

from sqlalchemy import Column, Integer, String, Float, DateTime, Enum, UniqueConstraint
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
    age = Column(Integer, nullable=True)
    mobile = Column(String(15), nullable=False)  # mandatory
    gender = Column(Enum(Gender), nullable=True)
    address = Column(String(45), nullable=True)
    # currentVisit = Column(DateTime, nullable=True)
    lastVisit = Column(Date, nullable=True)
    bloodGroup = Column(
        String(5), nullable=True
    )  # e.g., "A+", "O-", etc.
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

    __table_args__ = (
        UniqueConstraint("assigned_doctor_id", "mobile", name="uq_doc_patient"),
    )
