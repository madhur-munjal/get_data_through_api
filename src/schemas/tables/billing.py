import uuid
from datetime import datetime

from sqlalchemy import Column, String, DateTime, ForeignKey, Float, Text, Enum, Integer
from sqlalchemy.orm import relationship
from src.models.enums import AppointmentStatus, AppointmentType
from src.database import Base


class Billing(Base):
    __tablename__ = "billing"

    billing_id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    visit_id = Column(String(36), ForeignKey("visits.id"), nullable=False)
    patient_id = Column(String(36), ForeignKey("patients.patient_id"), nullable=False)
    invoice_number = Column(String(36), unique=True)
    billing_date = Column(DateTime, default=datetime.utcnow)
    total_amount = Column(Float)
    discount = Column(Float, default=0.0)
    tax = Column(Float, default=0.0)
    amount_paid = Column(Float, default=0.0)
    payment_status = Column(Enum("Pending", "Paid", "Partial", name="payment_status_enum"))
    payment_method = Column(String(36))  # e.g., Cash, Card, Insurance
    notes = Column(Text)

    visit = relationship("Visit", back_populates="billing")