import uuid
from datetime import datetime

from sqlalchemy import Column, String, Integer, Float, DateTime, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from src.database import Base


class Plan(Base):
    __tablename__ = "plans"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    # Column(Integer, primary_key=True, default=lambda: str(uuid.uuid4()), index=True)
    name = Column(String(36), unique=True, nullable=False)         # e.g., "Basic", "Premium"
    description = Column(String(200), nullable=True)                # optional description
    price = Column(Float, nullable=False)                      # monthly or one-time price
    currency = Column(String(5), default="INR")                   # e.g., "INR", "USD"
    # duration_days = Column(Integer, default=30)                # plan duration

    subscription = relationship("Subscription", back_populates="plan")