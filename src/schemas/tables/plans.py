import uuid
from datetime import datetime

from sqlalchemy import Column, String, Integer, Float, DateTime, Boolean, ForeignKey, Text
from sqlalchemy.orm import relationship
from src.database import Base


class Plan(Base):
    __tablename__ = "plans"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    s_no = Column(Integer, nullable=False)
    name = Column(String(36), nullable=False)         # e.g., "Basic", "Premium"
    description = Column(Text, nullable=True)                # optional description
    price = Column(Float, nullable=False)                      # monthly or one-time price
    currency = Column(String(5), default="INR")                   # e.g., "INR", "USD"
    duration_months = Column(Integer, nullable=False)                # plan duration

    subscription = relationship("Subscription", back_populates="plan")