import uuid
from datetime import datetime

from sqlalchemy import (
    Column,
    String,
    DateTime,
    ForeignKey,
    Float,
    Text,
    Enum,
    Boolean,
    TIMESTAMP,
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from src.database import Base


class InterestedUser(Base):
    __tablename__ = "interested_users"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    doctor_id = Column(String(36), ForeignKey("users.id"), nullable=False)
    plan_id = Column(String(36), ForeignKey("plans.id"), nullable=False)
    # created_at = Column(DateTime, default=datetime.utcnow)
    created_by = Column(String(100), nullable=True, default="website")
    interest_date = Column(TIMESTAMP, server_default=func.now())
    source = Column(String(100), nullable=True)
    status = Column(String(50), default="interested")
    notes = Column(Text, nullable=True)

    # is_deleted = Column(Boolean, nullable=False, default=False)
    # deleted_at = Column(DateTime, nullable=True)

    user = relationship("User", back_populates="interested_users")
    plan = relationship("Plan", back_populates="interested_users")
