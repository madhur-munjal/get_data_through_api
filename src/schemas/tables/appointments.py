import uuid
from datetime import datetime

from sqlalchemy import Column, String, DateTime, ForeignKey, Date, Time, Enum, Integer
from sqlalchemy.orm import relationship
from src.models.enums import AppointmentStatus, AppointmentType
from src.database import Base


class Appointment(Base):
    __tablename__ = "appointments"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    patient_id = Column(String(36), ForeignKey("patients.patient_id"))
    doctor_id = Column(String(36), ForeignKey("users.id"))
    scheduled_date_time = Column(DateTime, nullable=False)  #, default=datetime.utcnow)
    # scheduled_date = Column(Date, nullable=False)
    # scheduled_time = Column(Time, nullable=False)
    type = Column(Integer, nullable=False, default=AppointmentType.NEW)
    status = Column(Integer, nullable=False, default=AppointmentStatus.UPCOMING)
    created_at = Column(DateTime, default=datetime.utcnow)

    patient = relationship("Patient", back_populates="appointments")
    user = relationship("User", back_populates="appointments")
    visits = relationship("Visit", back_populates="appointments")
