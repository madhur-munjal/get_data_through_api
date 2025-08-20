# import uuid
# from datetime import datetime
#
# from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text
# from sqlalchemy.orm import relationship
#
# from src.database import Base  # assuming you have a Base class from your DB setup
#
#
# class Visit(Base):
#     __tablename__ = "visits"
#
#     id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
#     patient_id = Column(String(36), ForeignKey("patients.patient_id"), nullable=False)
#     doctor_id = Column(String(36), ForeignKey("users.id"), nullable=False)
#     appointment_id = Column(String(36), ForeignKey("appointments.id"), nullable=True)
#     visit_time = Column(DateTime, default=datetime.utcnow)
#     notes = Column(Text, nullable=True)
#     diagnosis = Column(String(200), nullable=True)
#     prescription = Column(Text, nullable=True)
#
#     patients = relationship("Patient", back_populates="visits")
#     doctor = relationship("Doctor", back_populates="visits")
#     appointments = relationship("Appointment", back_populates="visit")
