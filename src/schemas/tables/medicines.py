import uuid

from sqlalchemy import (
    Column,
    String,
    Boolean,
    Text,
    DateTime,
    ForeignKey,
    Integer,
    JSON,
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from src.database import Base


class Medicine(Base):
    __tablename__ = "medicines"

    medicine_id = Column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    doctor_id = Column(String(36), ForeignKey("users.id"))
    medicine_name = Column(String(255), nullable=False, index=True)
    composition = Column(Text, nullable=True)
    manufacturer = Column(String(255), nullable=True)
    type = Column(String(100), nullable=True)  # e.g., Tablet, Syrup, etc.
    count = Column(Integer, default=0)  # e.g., number of pills in a pack
    dosage = Column(JSON, nullable=True)  # e.g., Morning, Afternoon, Night
    before_meal = Column(
        Boolean, default=False
    )  # NEW: Indicates if the medicine should be taken before meals
    # timing = Column(String(100), nullable=True)  # e.g., Before Food, After Food, With Food
    duration = Column(String(100), nullable=True)  # e.g., 5 days, 1 week, etc.
    notes = Column(Text, nullable=True)  # Additional instructions or notes
    is_deleted = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    user = relationship("User", back_populates="medicines")
