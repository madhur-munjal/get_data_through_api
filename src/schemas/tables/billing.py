import uuid
from datetime import datetime

from sqlalchemy import Column, String, DateTime, ForeignKey, Float, Text, Enum, Integer
from sqlalchemy.orm import relationship
from src.models.enums import AppointmentStatus, AppointmentType
from src.database import Base


class Billing(Base):
    __tablename__ = "billing"

    billing_id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    appointment_id = Column(String(36), ForeignKey("appointments.id"), nullable=False)
    # We need to make sure that more than one appointment id should not present in visit, means patient booked one appointment and had visited twice.
    # patient_id = Column(String(36), ForeignKey("patients.patient_id"), nullable=False)
    # invoice_number = Column(String(36), unique=True)
    type = Column(Enum("Cash", "Card", "UPI", "Insurance", name="billing_type_enum"))
    billing_date = Column(DateTime, default=datetime.utcnow)
    amount = Column(Float)
    # discount = Column(Float, default=0.0)
    # tax = Column(Float, default=0.0)
    # amount_paid = Column(Float, default=0.0)
    # payment_status = Column(Enum("Pending", "Paid", "Partial", name="payment_status_enum"))
    notes = Column(Text, nullable=True)

    appointment = relationship("Appointment", back_populates="billing")