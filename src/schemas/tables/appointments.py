from datetime import datetime
from sqlalchemy.orm import relationship

from sqlalchemy import (
    Column,
    String,
    DateTime,
    ForeignKey,
    Integer
)

from src.database import Base
from patients import Patient  # Do not delete
from users import User  # Do not delete
from visits import Visit  # Do not delete

class Appointment(Base):
    __tablename__ = "appointments"

    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer, ForeignKey("patients.patient_id"))
    doctor_id = Column(Integer, ForeignKey("users.id"))
    scheduled_time = Column(DateTime, nullable=False)
    status = Column(String, default="scheduled")
    created_at = Column(DateTime, default=datetime.utcnow)

    patient = relationship("Patient", back_populates="appointments")
    doctor = relationship("User", back_populates="appointments")
    visit = relationship("Visit", back_populates="appointments")
