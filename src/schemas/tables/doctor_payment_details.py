import uuid

from sqlalchemy import Boolean, Column, String, ForeignKey
from sqlalchemy.orm import relationship
from src.database import Base


class DoctorPaymentDetails(Base):
    __tablename__ = "doctor_payment_details"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    doctor_id = Column(String(36), ForeignKey("users.id"), nullable=False)
    name = Column(String(36), nullable=False)

    # account_holder_name = Column(String, nullable=True)
    # bank_name = Column(String, nullable=True)
    # account_number = Column(String, nullable=True)
    # ifsc_code = Column(String, nullable=True)

    upi_id = Column(String(50), nullable=False)
    currency = Column(String(6), default="INR")  # 💱 e.g., 'INR', 'USD', 'EUR'

    # preferred_mode = Column(String, nullable=True)  # e.g., 'UPI', 'Bank Transfer'
    # is_active = Column(Boolean, default=True)

    doctor = relationship("User", back_populates="payment_details")