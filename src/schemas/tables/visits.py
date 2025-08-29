import uuid

from sqlalchemy import Column, String, ForeignKey, JSON, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from src.database import Base


class Visit(Base):
    __tablename__ = "visits"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    patient_id = Column(String(36), ForeignKey("patients.patient_id"), nullable=False)
    doctor_id = Column(String(36), ForeignKey("users.id"), nullable=False)
    appointment_id = Column(String(36), ForeignKey("appointments.id"), nullable=True)

    analysis = Column(String(250), nullable=True)
    advice = Column(String(250), nullable=True)
    tests = Column(String(250), nullable=True)
    followUpVisit = Column(String(100), nullable=True)
    medicationDetails = Column(JSON, nullable=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())

    # Uncommented additional fields and used as needed
    # follow_up = Column(String(100), nullable=True)    # visit_date = Column(Date, nullable=True)
    # scheduled_time = Column(Time, nullable=True)
    # visit_time = Column(DateTime, default=datetime.utcnow)
    # notes = Column(Text, nullable=True)
    # diagnosis = Column(String(200), nullable=True)
    # prescription = Column(JSON, nullable=True)

    patient = relationship("Patient", back_populates="visits")
    user = relationship("User", back_populates="visits")
    appointments = relationship("Appointment", back_populates="visits")
