import uuid

from sqlalchemy import (
    Column,
    Text,
    String,
    ForeignKey,
    CheckConstraint,
UniqueConstraint
)
from sqlalchemy.orm import relationship
from src.database import Base


class Staff(Base):
    __tablename__ = "staff"

    __table_args__ = (
        CheckConstraint(
            "length(firstName) >= 3", name="check_first_name_min_length_staff"
        ),
        CheckConstraint(
            "length(lastName) >= 3", name="check_last_name_min_length_staff"
        ),
    )

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    firstName = Column(String(15), nullable=False)  # mandatory
    lastName = Column(String(15), nullable=True)
    email = Column(String(255), nullable=False)  # mandatory
    country = Column(String(255), nullable=True)
    mobile = Column(Text, nullable=False)  # mandatory
    username = Column(String(255), nullable=False, unique=True)  # mandatory
    password = Column(Text, nullable=False)  # mandatory
    role = Column(String(50), nullable=False, default="staff")  # mandatory
    doc_id = Column(String(36), ForeignKey("users.id"), nullable=False)  # mandatory

    doctor = relationship("User", back_populates="staff")

    __table_args__ = (
        UniqueConstraint("doc_id", "email", name="uq_doc_staff"),
    )
