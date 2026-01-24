import uuid

from sqlalchemy import Column, String, Boolean, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from src.database import Base


class Medicine(Base):
    __tablename__ = "medicines"

    medicine_id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    doctor_id = Column(String(36), ForeignKey("users.id"))
    medicine_name = Column(String(255), nullable=False, index=True)
    composition = Column(Text, nullable=True)
    manufacturer = Column(String(255), nullable=True)
    # description = Column(Text, nullable=True)
    # dosage_form = Column(String(100), nullable=True)  # e.g., Tablet, Capsule, Syrup
    # strength = Column(String(100), nullable=True)  # e.g., 500mg, 10ml
    # price = Column(Float, nullable=False)
    # stock_quantity = Column(Integer, default=0)
    # is_prescription_required = Column(Boolean, default=False)
    # is_active = Column(Boolean, default=True)
    is_deleted = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    user = relationship("User", back_populates="medicines")
