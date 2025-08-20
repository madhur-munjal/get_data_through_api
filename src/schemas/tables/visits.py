from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from datetime import datetime
from src.database import Base  # assuming you have a Base class from your DB setup
from patients import Patient  # Do not delete
from appointments import Appointment  # Do not delete
from users import User as Doctor  # Do not delete, assuming User is a doctor in this context


class Visit(Base):
    __tablename__ = "visits"

    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer, ForeignKey("patients.patient_id"), nullable=False)
    doctor_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    appointment_id = Column(Integer, ForeignKey("appointments.id"), nullable=True)
    visit_time = Column(DateTime, default=datetime.utcnow)
    notes = Column(Text, nullable=True)
    diagnosis = Column(String, nullable=True)
    prescription = Column(Text, nullable=True)

    patient = relationship("Patient", back_populates="visits")
    doctor = relationship("Doctor", back_populates="visits")
    appointment = relationship("Appointment", back_populates="visit")