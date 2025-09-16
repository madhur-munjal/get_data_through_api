import uuid
from datetime import datetime
from sqlalchemy import Boolean, Column, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from src.database import Base


class Notification(Base):
    __tablename__ = "notifications"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    doctor_id = Column(String(36), ForeignKey("users.id"), nullable=False)
    appointment_id = Column(String(36), nullable=True)  # could be null for billing notifications
    billing_id = Column(String(36), nullable=True)  # could be null for appointment notifications
    firstName = Column(String(15), nullable=False)  # mandatory
    lastName = Column(String(15), nullable=True)
    type = Column(String(50), nullable=True)  # e.g., 'appointment', 'payment'
    message = Column(String(255), nullable=False)
    read = Column(Boolean, nullable=False, default=False)
    updated_by = Column(String(50), nullable=False)  # could be user id or
    created_at = Column(DateTime, default=datetime.utcnow)
