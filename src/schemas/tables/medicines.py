from sqlalchemy import Column, Integer, String, Float, Boolean, Text, DateTime, ForeignKey
from sqlalchemy.sql import func
from src.database import Base
from sqlalchemy.orm import relationship


class Medicine(Base):
    __tablename__ = "medicines"

    id = Column(Integer, primary_key=True, index=True)
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