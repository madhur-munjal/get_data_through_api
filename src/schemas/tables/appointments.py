import uuid
from datetime import datetime

from sqlalchemy import (
    Column,
    String,
    DateTime,
    ForeignKey,
    Date,
    Time
)
from sqlalchemy.orm import relationship

from src.database import Base


class Appointment(Base):

    __tablename__ = "appointments"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    patient_id = Column(String(36), ForeignKey("patients.patient_id"))
    doctor_id = Column(String(36), ForeignKey("users.id"))
    scheduled_date = Column(Date, nullable=True)
    scheduled_time = Column(Time, nullable=True)
    status = Column(String(20), default="scheduled")
    created_at = Column(DateTime, default=datetime.utcnow)
    # from .visits import Visit
    # from .patients import Patient
    # from .users import User

    patient = relationship("Patient", back_populates="appointments")
    user = relationship("User", back_populates="appointments")
    visits = relationship("Visit", back_populates="appointments")
